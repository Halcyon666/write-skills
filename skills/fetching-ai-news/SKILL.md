---
name: fetching-ai-news
description: Fetches AI news and vibe-coding stories from free sources and exposes a bundled MCP tool. Use when asked to scrape AI news, gather recent AI headlines, build a digest, or send the digest to Telegram.
compatibility: Requires Python 3.10+ and pip install -r references/requirements.txt.
license: MIT
---

# Fetching AI News

Fetches, classifies, and ranks AI News and Vibe Coding stories with a bundled reference implementation.

## When to Use

- User asks to fetch or scrape recent AI news
- User wants AI News Digest or Vibe Coding digest
- User wants to preview digest content before sending
- User wants to send the generated digest to Telegram
- User needs a reusable AI-news MCP capability without paid APIs

## Instructions

1. Install dependencies from the bundled reference package.

```bash
cd skills/fetching-ai-news
pip install -r references/requirements.txt
```

2. Start the bundled MCP server.

```bash
cd skills/fetching-ai-news
python -m references.src.mcp_server
```

3. Call `run_ai_news_digest(hours=13, max_per_category=6, send=false)`.

4. Summarize counts plus top links from `items.ai` and `items.vibe_coding`.

5. Only use `send=true` after confirming Telegram credentials are configured.

## References

| Topic | File |
| --- | --- |
| Detailed setup and invocation | [references/setup-and-usage.md](references/setup-and-usage.md) |
| Return payload and presentation rules | [references/output-format.md](references/output-format.md) |
| Bundled implementation layout | [references/implementation-layout.md](references/implementation-layout.md) |

## Workflow Checklist

- [ ] Install dependencies (first time only)
- [ ] Start the MCP server from `skills/fetching-ai-news`
- [ ] Choose `hours`, `max_per_category`, and `send`
- [ ] Call `run_ai_news_digest`
- [ ] Summarize counts and link top items
- [ ] If sending to Telegram, verify `sent=true`

## Common Pitfalls

- Do not write a new scraper when the bundled reference implementation already fits
- Do not set `send=true` unless user explicitly wants Telegram delivery
- Do not assume Telegram credentials exist; check environment first
- Do not treat empty results as failure; check `raw_count` first
- Run the server from `skills/fetching-ai-news`, not repo root
