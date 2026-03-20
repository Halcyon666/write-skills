"""ArXiv RSS feed fetcher for AI-related papers."""

import logging
import re
from collections.abc import Sequence
from datetime import datetime, timezone

import feedparser

from ..sources import NewsItem

logger = logging.getLogger(__name__)

# ArXiv RSS feeds for AI-related categories
FEED_URLS = [
    "https://rss.arxiv.org/rss/cs.AI",  # Artificial Intelligence
    "https://rss.arxiv.org/rss/cs.CL",  # Computation and Language (NLP)
    "https://rss.arxiv.org/rss/cs.LG",  # Machine Learning
    "https://rss.arxiv.org/rss/cs.CV",  # Computer Vision
]

# Regex to extract arxiv ID from various URL formats
ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5})")


def _as_text(value: object, default: str = "") -> str:
    """Return string values from feedparser fields."""
    return value if isinstance(value, str) else default


def _parse_datetime(value: object) -> datetime:
    """Convert feedparser time tuples to UTC datetimes."""
    if isinstance(value, Sequence) and len(value) >= 6:
        parts = value[:6]
        if all(isinstance(part, int) for part in parts):
            year, month, day, hour, minute, second = parts
            return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _clean_description(raw: str) -> str:
    """Strip HTML tags and truncate to 200 chars."""
    clean = re.sub(r"<[^>]+>", "", raw).strip()
    clean = re.sub(r"\s+", " ", clean)
    if len(clean) > 200:
        clean = clean[:197] + "..."
    return clean


def _extract_category(url: str) -> str:
    """Extract category label from feed URL."""
    if "cs.AI" in url:
        return "cs.AI"
    if "cs.CL" in url:
        return "cs.CL"
    if "cs.LG" in url:
        return "cs.LG"
    if "cs.CV" in url:
        return "cs.CV"
    return "arxiv"


def fetch(hours: int = 24) -> list[NewsItem]:
    """Fetch AI papers from ArXiv RSS feeds.

    Args:
        hours: Look back this many hours (ArXiv RSS is daily, so this
               mainly prevents re-sending old papers).

    Returns:
        List of normalized NewsItem objects.
    """
    items: dict[str, NewsItem] = {}

    for feed_url in FEED_URLS:
        try:
            feed = feedparser.parse(feed_url)
            category = _extract_category(feed_url)

            for entry in feed.entries:
                link = _as_text(entry.get("link"))

                # Normalize arxiv URLs to abstract page
                match = ARXIV_ID_RE.search(link)
                if match:
                    canonical_url = f"https://arxiv.org/abs/{match.group(1)}"
                else:
                    canonical_url = link

                if canonical_url in items:
                    continue

                # Parse published date
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                pub_dt = _parse_datetime(published)

                title = _as_text(entry.get("title"), "Untitled").strip()
                summary = _as_text(entry.get("summary"))
                description = _clean_description(
                    summary or _as_text(entry.get("description"))
                )

                # ArXiv papers get a flat base score — no engagement metrics
                items[canonical_url] = NewsItem(
                    title=title,
                    url=canonical_url,
                    source="arxiv",
                    score=0.3,  # Base score for research papers
                    published_at=pub_dt,
                    description=description,
                    tags=[category],
                )

        except Exception as e:
            logger.warning("ArXiv feed failed for %s: %s", feed_url, e)
            continue

    logger.info("Fetched %d papers from ArXiv", len(items))
    return list(items.values())
