"""AI News fetcher — parallel source fetching."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .sources import NewsItem
from .sources import arxiv, googlenews, hackernews

logger = logging.getLogger(__name__)

# How far back to look for news (in hours)
LOOKBACK_HOURS = 13


def fetch_all_sources(hours: int) -> list[NewsItem]:
    """Fetch news from all sources in parallel.

    Args:
        hours: Look back this many hours.

    Returns:
        Combined list of news items from all sources.
    """
    all_items: list[NewsItem] = []
    fetchers = {
        "Hacker News": lambda: hackernews.fetch(hours),
        "ArXiv": lambda: arxiv.fetch(hours),
        "Google News": lambda: googlenews.fetch(hours),
    }

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fn): name for name, fn in fetchers.items()}

        for future in as_completed(futures):
            source_name = futures[future]
            try:
                items = future.result()
                all_items.extend(items)
                logger.info("✓ %s: %d items", source_name, len(items))
            except Exception as e:
                logger.error("✗ %s failed: %s", source_name, e)

    return all_items
