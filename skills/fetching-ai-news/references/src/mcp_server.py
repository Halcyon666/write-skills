"""Local stdio MCP server for AI News Digest."""

from fastmcp import FastMCP

from .app import run_digest

mcp = FastMCP("ai-news-digest")


@mcp.tool()
def run_ai_news_digest(
    hours: int = 13,
    max_per_category: int = 6,
    send: bool = False,
) -> dict[str, object]:
    """Generate the AI news digest and optionally send it to Telegram.

    Args:
        hours: Look back this many hours when fetching news.
        max_per_category: Maximum number of items per category.
        send: Send the formatted digest to Telegram when true.
    """
    result = run_digest(hours=hours, max_per_category=max_per_category, send=send)
    categorized = result["categorized"]

    return {
        "raw_count": len(result["raw_items"]),
        "ai_count": len(categorized["ai"]),
        "vibe_coding_count": len(categorized["vibe_coding"]),
        "sent": result["sent"],
        "messages": result["messages"],
        "items": {
            key: [
                {
                    "title": item.title,
                    "url": item.url,
                    "source": item.source,
                    "score": item.score,
                    "published_at": item.published_at.isoformat(),
                }
                for item in items
            ]
            for key, items in categorized.items()
        },
    }


def main() -> None:
    """Start the local stdio MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
