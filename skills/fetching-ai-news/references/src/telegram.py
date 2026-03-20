"""Telegram Bot API message sender."""

import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


def _get_config() -> tuple[str, str]:
    """Read Telegram config from environment variables."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID environment variable is not set")

    return token, chat_id


def send_messages(messages: list[str]) -> None:
    """Send formatted messages to Telegram.

    Args:
        messages: List of MarkdownV2-formatted message strings.

    Raises:
        RuntimeError: If Telegram credentials are missing.
        requests.RequestException: If API call fails after retries.
    """
    token, chat_id = _get_config()
    url = f"{TELEGRAM_API_BASE}/bot{token}/sendMessage"

    for i, message in enumerate(messages):
        # Retry logic for transient failures
        for attempt in range(3):
            try:
                resp = requests.post(
                    url,
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "MarkdownV2",
                        "disable_web_page_preview": True,
                    },
                    timeout=15,
                )

                if resp.status_code == 429:
                    # Rate limited — respect Retry-After header
                    retry_after = (
                        resp.json().get("parameters", {}).get("retry_after", 5)
                    )
                    logger.warning("Rate limited, waiting %ds", retry_after)
                    time.sleep(retry_after)
                    continue

                # Handle group upgraded to supergroup — extract new chat_id and retry
                if resp.status_code == 400:
                    error_data = resp.json()
                    description = error_data.get("description", "")
                    if "upgraded to a supergroup" in description:
                        migrate_to = error_data.get("parameters", {}).get(
                            "migrate_to_chat_id"
                        )
                        if migrate_to:
                            logger.warning(
                                "Group upgraded to supergroup. New chat_id: %s. "
                                "Please update TELEGRAM_CHAT_ID in your environment.",
                                migrate_to,
                            )
                            chat_id = str(migrate_to)
                            continue  # Retry with new chat_id
                        else:
                            logger.error(
                                "Group upgraded to supergroup but no migrate_to_chat_id provided. "
                                "Please manually update TELEGRAM_CHAT_ID."
                            )

                resp.raise_for_status()
                result = resp.json()

                if not result.get("ok"):
                    logger.error(
                        "Telegram API error: %s", result.get("description", "Unknown")
                    )
                    # If MarkdownV2 parsing fails, retry as plain text
                    if "parse" in result.get("description", "").lower():
                        logger.info("Retrying message %d as plain text", i + 1)
                        resp = requests.post(
                            url,
                            json={
                                "chat_id": chat_id,
                                "text": message,
                                "disable_web_page_preview": True,
                            },
                            timeout=15,
                        )
                        resp.raise_for_status()

                logger.info("Sent message %d/%d", i + 1, len(messages))
                break  # Success — exit retry loop

            except requests.RequestException as e:
                logger.warning(
                    "Attempt %d failed for message %d: %s",
                    attempt + 1,
                    i + 1,
                    e,
                )
                if attempt < 2:
                    time.sleep(2**attempt)
                else:
                    raise

        # Small delay between messages to avoid hitting rate limits
        if i < len(messages) - 1:
            time.sleep(1)
