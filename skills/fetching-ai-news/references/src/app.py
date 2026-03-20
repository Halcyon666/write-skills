"""Shared AI News Digest application runner."""

import logging
from typing import TypedDict

from .formatter import format_messages
from .processor import process
from .sources import NewsItem
from .telegram import send_messages
from .fetcher import LOOKBACK_HOURS, fetch_all_sources

logger = logging.getLogger(__name__)


class DigestResult(TypedDict):
    """Structured result from a digest run."""

    raw_items: list[NewsItem]
    categorized: dict[str, list[NewsItem]]
    messages: list[str]
    sent: bool


def run_digest(
    hours: int = LOOKBACK_HOURS,
    max_per_category: int = 6,
    send: bool = True,
) -> DigestResult:
    """Run the digest pipeline and optionally send Telegram messages."""
    raw_items = fetch_all_sources(hours)
    if not raw_items:
        logger.warning("No items fetched from any source.")
        return {
            "raw_items": raw_items,
            "categorized": {"ai": [], "vibe_coding": []},
            "messages": [],
            "sent": False,
        }

    logger.info("Total raw items: %d", len(raw_items))

    categorized = process(raw_items, max_per_category=max_per_category)
    total = sum(len(items) for items in categorized.values())
    logger.info("Top items after processing: %d", total)

    messages = format_messages(categorized)
    logger.info("Formatted into %d message(s)", len(messages))

    if send:
        send_messages(messages)

    return {
        "raw_items": raw_items,
        "categorized": categorized,
        "messages": messages,
        "sent": send,
    }
