"""Google News RSS fetcher for AI news articles."""

import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from ..sources import NewsItem

logger = logging.getLogger(__name__)

# Google News RSS search URLs — free, no API key needed
FEED_URLS = [
    # AI news
    "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=LLM+OR+GPT+OR+OpenAI+OR+Anthropic&hl=en-US&gl=US&ceid=US:en",
    # Vibe coding news
    "https://news.google.com/rss/search?q=%22vibe+coding%22+OR+%22AI+coding%22+OR+%22Cursor+IDE%22&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Copilot+OR+Windsurf+OR+%22code+generation%22+OR+%22AI+IDE%22&hl=en-US&gl=US&ceid=US:en",
]


def _clean_html(raw: str) -> str:
    """Strip HTML tags and truncate."""
    clean = re.sub(r"<[^>]+>", "", raw).strip()
    clean = re.sub(r"\s+", " ", clean)
    if len(clean) > 200:
        clean = clean[:197] + "..."
    return clean


def _as_text(value: object, default: str = "") -> str:
    """Return string values from feedparser fields."""
    return value if isinstance(value, str) else default


def _parse_date(entry: dict) -> datetime:
    """Parse published date from RSS entry."""
    pub = _as_text(entry.get("published"))
    if pub:
        try:
            return parsedate_to_datetime(pub).astimezone(timezone.utc)
        except (ValueError, TypeError):
            pass
    return datetime.now(timezone.utc)


def _extract_source(title: str) -> str:
    """Extract source name from Google News title format 'Headline - Source'."""
    if " - " in title:
        return title.rsplit(" - ", 1)[-1].strip()
    return ""


def _clean_title(title: str) -> str:
    """Remove source suffix from Google News title."""
    if " - " in title:
        return title.rsplit(" - ", 1)[0].strip()
    return title.strip()


def fetch(hours: int = 24) -> list[NewsItem]:
    """Fetch AI news from Google News RSS feeds.

    Args:
        hours: Not strictly enforced by Google News RSS, but used
               for consistency with other fetchers.

    Returns:
        List of normalized NewsItem objects.
    """
    items: dict[str, NewsItem] = {}

    for feed_url in FEED_URLS:
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                link = _as_text(entry.get("link"))
                if not link or link in items:
                    continue

                raw_title = _as_text(entry.get("title"), "Untitled")
                source_name = _extract_source(raw_title)
                title = _clean_title(raw_title)
                pub_dt = _parse_date(entry)
                summary = _as_text(entry.get("summary"))
                description = _clean_html(summary or _as_text(entry.get("description")))

                items[link] = NewsItem(
                    title=title,
                    url=link,
                    source="googlenews",
                    score=0.4,  # Base score for news articles
                    published_at=pub_dt,
                    description=description,
                    tags=[source_name.lower()] if source_name else [],
                )

        except Exception as e:
            logger.warning("Google News feed failed for %s: %s", feed_url, e)
            continue

    logger.info("Fetched %d articles from Google News", len(items))
    return list(items.values())
