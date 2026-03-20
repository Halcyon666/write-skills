"""Format news items into Telegram-friendly messages."""

import re
from datetime import datetime, timezone

from .sources import NewsItem

# Telegram message character limit
TELEGRAM_MAX_LENGTH = 4096

# Source display names
SOURCE_LABELS = {
    "hackernews": "Hacker News",
    "arxiv": "ArXiv",
    "googlenews": "Google News",
}

# Category display config
CATEGORY_CONFIG = {
    "ai": {"emoji": "🤖", "title": "AI News"},
    "vibe_coding": {"emoji": "🎧", "title": "Vibe Coding"},
}

# Characters that need escaping in Telegram MarkdownV2
# See: https://core.telegram.org/bots/api#markdownv2-style
_ESCAPE_CHARS = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")


def _escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    return _ESCAPE_CHARS.sub(r"\\\1", text)


def _format_source_label(item: NewsItem) -> str:
    """Build the source attribution line."""
    label = SOURCE_LABELS.get(item.source, item.source)

    if item.source == "arxiv" and item.tags:
        tag = _escape_md(item.tags[0])
        return f"via {_escape_md(label)} \\· {tag}"
    else:
        return f"via {_escape_md(label)}"


def _format_single_item(index: int, item: NewsItem) -> str:
    """Format a single news item as MarkdownV2."""
    title = _escape_md(item.title)
    url = item.url
    source_line = _format_source_label(item)

    lines = [
        f"*{index}\\. {title}*",
        f"[Read more]({url})",
        source_line,
    ]

    if item.description:
        desc = _escape_md(item.description[:150])
        lines.insert(1, f"_{desc}_")

    return "\n".join(lines)


def _format_section(
    category_key: str,
    items: list[NewsItem],
) -> str:
    """Format a single category section."""
    config = CATEGORY_CONFIG.get(category_key, {"emoji": "📰", "title": category_key})

    if not items:
        return f"\n{config['emoji']} *{_escape_md(config['title'])}*\n\n_No stories found\\._\n"

    header = f"\n{config['emoji']} *{_escape_md(config['title'])}*\n"
    blocks = []
    for i, item in enumerate(items, 1):
        blocks.append(_format_single_item(i, item))

    return header + "\n" + "\n\n".join(blocks) + "\n"


def format_messages(
    categorized: dict[str, list[NewsItem]],
) -> list[str]:
    """Format categorized news items into Telegram messages.

    Always sends two separate messages: one for AI News, one for Vibe Coding.

    Args:
        categorized: Dict with "ai" and "vibe_coding" keys.

    Returns:
        List of formatted message strings (MarkdownV2).
    """
    all_items = []
    for items in categorized.values():
        all_items.extend(items)

    if not all_items:
        return ["No news found for this period\\."]

    now = datetime.now(timezone.utc)
    date_str = _escape_md(now.strftime("%b %d, %Y"))

    messages: list[str] = []

    # Message 1: AI News
    ai_items = categorized.get("ai", [])
    ai_msg = f"📡 *AI News Digest — {date_str}*\n"
    ai_msg += _format_section("ai", ai_items)
    messages.append(ai_msg.rstrip())

    # Message 2: Vibe Coding
    vibe_items = categorized.get("vibe_coding", [])
    vibe_msg = f"🎧 *Vibe Coding Digest — {date_str}*\n"
    vibe_msg += _format_section("vibe_coding", vibe_items)
    messages.append(vibe_msg.rstrip())

    return messages
