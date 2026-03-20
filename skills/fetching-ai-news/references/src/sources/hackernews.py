"""Hacker News fetcher via Algolia API."""

import logging
from datetime import datetime, timezone

import requests

from ..sources import NewsItem

logger = logging.getLogger(__name__)

# Algolia HN Search API — free, no key required
BASE_URL = "https://hn.algolia.com/api/v1/search"

# AI-related search queries to cast a wide net
AI_QUERIES = [
    "AI",
    "LLM",
    "GPT",
    "machine learning",
    "deep learning",
    "artificial intelligence",
]

# Vibe coding search queries
VIBE_CODING_QUERIES = [
    "vibe coding",
    "Cursor IDE",
    "Windsurf",
    "Copilot",
    "AI coding",
    "Claude code",
    "Devin AI",
    "code generation",
    "AI IDE",
    "agentic coding",
]

SEARCH_QUERIES = AI_QUERIES + VIBE_CODING_QUERIES


def fetch(hours: int = 24) -> list[NewsItem]:
    """Fetch AI-related stories from Hacker News.

    Args:
        hours: Look back this many hours for stories.

    Returns:
        List of normalized NewsItem objects.
    """
    items: dict[str, NewsItem] = {}  # Dedupe by URL within source
    timestamp_floor = int((datetime.now(timezone.utc).timestamp()) - (hours * 3600))

    for query in SEARCH_QUERIES:
        try:
            resp = requests.get(
                BASE_URL,
                params={
                    "query": query,
                    "tags": "story",
                    "numericFilters": f"created_at_i>{timestamp_floor}",
                    "hitsPerPage": 20,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            for hit in data.get("hits", []):
                url = (
                    hit.get("url")
                    or f"https://news.ycombinator.com/item?id={hit['objectID']}"
                )

                if url in items:
                    continue

                created_at = datetime.fromtimestamp(
                    hit.get("created_at_i", 0), tz=timezone.utc
                )
                points = hit.get("points", 0) or 0

                # Normalize score: HN stories with 100+ points are significant
                normalized_score = min(points / 300, 1.0)

                items[url] = NewsItem(
                    title=hit.get("title", "Untitled"),
                    url=url,
                    source="hackernews",
                    score=normalized_score,
                    published_at=created_at,
                    description="",  # HN stories don't have descriptions
                    tags=[query.lower()],
                )

        except requests.RequestException as e:
            logger.warning("HN search failed for query '%s': %s", query, e)
            continue

    logger.info("Fetched %d stories from Hacker News", len(items))
    return list(items.values())
