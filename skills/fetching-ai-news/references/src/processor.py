"""Filter, deduplicate, classify, and rank news items."""

import logging
import re
from difflib import SequenceMatcher
from datetime import datetime, timezone

from .sources import NewsItem

logger = logging.getLogger(__name__)

# ── Category keyword lists ──────────────────────────────────────────────

AI_KEYWORDS = [
    r"\bAI\b",
    r"\bartificial intelligence\b",
    r"\bLLM\b",
    r"\bGPT\b",
    r"\bClaude\b",
    r"\bGemini\b",
    r"\bmachine learning\b",
    r"\bdeep learning\b",
    r"\bneural network\b",
    r"\btransformer\b",
    r"\bNLP\b",
    r"\bcomputer vision\b",
    r"\bdiffusion\b",
    r"\bfine[- ]tuning\b",
    r"\bRAG\b",
    r"\bOpenAI\b",
    r"\bAnthropic\b",
    r"\bDeepMind\b",
    r"\bMeta AI\b",
    r"\bMistral\b",
    r"\bHugging Face\b",
    r"\bDeepSeek\b",
    r"\bGrok\b",
]

VIBE_CODING_KEYWORDS = [
    r"\bvibe coding\b",
    r"\bCursor\b",
    r"\bWindsurf\b",
    r"\bCopilot\b",
    r"\bAI coding\b",
    r"\bcode generation\b",
    r"\bagentic coding\b",
    r"\bAI IDE\b",
    r"\bClaude code\b",
    r"\bCline\b",
    r"\bDevin\b",
    r"\bv0\b",
    r"\bbolt\.new\b",
    r"\bLovable\b",
    r"\bReplit\b",
    r"\bAI developer\b",
    r"\bAI engineer\b",
    r"\bcode assistant\b",
    r"\bGitHub Copilot\b",
    r"\bAI pair programming\b",
]

_AI_PATTERNS = [re.compile(kw, re.IGNORECASE) for kw in AI_KEYWORDS]
_VIBE_PATTERNS = [re.compile(kw, re.IGNORECASE) for kw in VIBE_CODING_KEYWORDS]

# Source weights for ranking
SOURCE_WEIGHTS = {
    "hackernews": 0.8,
    "googlenews": 0.5,
    "arxiv": 0.6,
}


# ── Classification ──────────────────────────────────────────────────────


def _classify(item: NewsItem) -> str | None:
    """Classify a news item as 'ai', 'vibe_coding', or None (irrelevant).

    Vibe coding is checked first — if it matches both, it goes to vibe_coding
    since those keywords are more specific.
    """
    text = f"{item.title} {item.description}"

    is_vibe = any(p.search(text) for p in _VIBE_PATTERNS)
    is_ai = any(p.search(text) for p in _AI_PATTERNS)

    if is_vibe:
        return "vibe_coding"
    if is_ai:
        return "ai"
    # ArXiv papers are always AI-relevant
    if item.source == "arxiv":
        return "ai"
    return None


# ── Dedup & scoring helpers ─────────────────────────────────────────────


def _title_similarity(a: str, b: str) -> float:
    """Compute fuzzy similarity between two titles."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _normalize_url(url: str) -> str:
    """Strip tracking params and normalize URL for deduplication."""
    url = re.sub(r"[?&](utm_\w+|ref|source|campaign)=[^&]*", "", url)
    url = url.rstrip("/").split("#")[0]
    return url.lower()


def _recency_score(item: NewsItem) -> float:
    """Score 0-1 based on how recent the item is (last 24h)."""
    age_hours = (datetime.now(timezone.utc) - item.published_at).total_seconds() / 3600
    if age_hours <= 0:
        return 1.0
    if age_hours >= 24:
        return 0.0
    return 1.0 - (age_hours / 24)


def _deduplicate(items: list[NewsItem]) -> list[NewsItem]:
    """Remove duplicate items by URL normalization and fuzzy title matching."""
    seen_urls: set[str] = set()
    unique: list[NewsItem] = []

    for item in items:
        norm_url = _normalize_url(item.url)

        if norm_url in seen_urls:
            continue

        # Only check fuzzy matching against recent unique items (last 50)
        # to avoid O(n²) complexity on large datasets
        is_duplicate = False
        check_against = unique[-50:] if len(unique) > 50 else unique

        for existing in check_against:
            if _title_similarity(item.title, existing.title) > 0.85:
                if item.score > existing.score:
                    unique.remove(existing)
                    seen_urls.discard(_normalize_url(existing.url))
                    break
                else:
                    is_duplicate = True
                    break

        if not is_duplicate:
            seen_urls.add(norm_url)
            unique.append(item)

    return unique


def _rank(items: list[NewsItem]) -> list[NewsItem]:
    """Compute final score and sort descending."""
    for item in items:
        source_weight = SOURCE_WEIGHTS.get(item.source, 0.5)
        recency = _recency_score(item)
        engagement = item.score

        item.score = (source_weight * 0.4) + (recency * 0.3) + (engagement * 0.3)

    return sorted(items, key=lambda x: x.score, reverse=True)


# ── Main pipeline ───────────────────────────────────────────────────────


def process(
    items: list[NewsItem],
    max_per_category: int = 6,
) -> dict[str, list[NewsItem]]:
    """Full processing pipeline: classify → dedupe → rank → top N per category.

    Args:
        items: Raw items from all sources.
        max_per_category: Maximum number of items per category.

    Returns:
        Dict with keys "ai" and "vibe_coding", each containing
        a ranked list of top news items.
    """
    logger.info("Processing %d raw items", len(items))

    # Step 1: Classify into categories
    ai_items: list[NewsItem] = []
    vibe_items: list[NewsItem] = []

    for item in items:
        category = _classify(item)
        if category == "ai":
            item.category = "ai"
            ai_items.append(item)
        elif category == "vibe_coding":
            item.category = "vibe_coding"
            vibe_items.append(item)

    logger.info("Classified: %d AI, %d Vibe Coding", len(ai_items), len(vibe_items))

    # Step 2 & 3: Deduplicate and rank each category independently
    ai_deduped = _deduplicate(ai_items)
    vibe_deduped = _deduplicate(vibe_items)
    logger.info(
        "After dedup: %d AI, %d Vibe Coding", len(ai_deduped), len(vibe_deduped)
    )

    ai_ranked = _rank(ai_deduped)[:max_per_category]
    vibe_ranked = _rank(vibe_deduped)[:max_per_category]

    logger.info(
        "Returning top %d AI + %d Vibe Coding items",
        len(ai_ranked),
        len(vibe_ranked),
    )

    return {
        "ai": ai_ranked,
        "vibe_coding": vibe_ranked,
    }
