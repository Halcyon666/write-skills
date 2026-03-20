from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewsItem:
    """Normalized news item from any source."""

    title: str
    url: str
    source: str  # "hackernews" | "arxiv" | "googlenews"
    score: float  # Normalized 0-1 for ranking
    published_at: datetime
    category: str = ""  # "ai" | "vibe_coding" — assigned by processor
    description: str = ""  # Short blurb, max 200 chars
    tags: list[str] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NewsItem):
            return NotImplemented
        return self.url == other.url
