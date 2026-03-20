# Implementation Layout

The bundled implementation lives under `references/src/` so `SKILL.md` stays short and activation-friendly.

## Structure

```text
skills/fetching-ai-news/
├── SKILL.md
└── references/
    ├── __init__.py
    ├── .env.example
    ├── requirements.txt
    ├── setup-and-usage.md
    ├── output-format.md
    ├── implementation-layout.md
    └── src/
        ├── __init__.py
        ├── mcp_server.py
        ├── app.py
        ├── fetcher.py
        ├── processor.py
        ├── formatter.py
        ├── telegram.py
        └── sources/
            ├── __init__.py
            ├── hackernews.py
            ├── arxiv.py
            └── googlenews.py
```

## Module Roles

- `references/src/mcp_server.py` - FastMCP entrypoint exposing `run_ai_news_digest`
- `references/src/app.py` - top-level orchestration for fetch, classify, format, and optional send
- `references/src/fetcher.py` - parallel source fetching extracted from the original repo flow
- `references/src/processor.py` - classification, deduplication, and ranking
- `references/src/formatter.py` - Telegram MarkdownV2 message formatting
- `references/src/telegram.py` - Bot API delivery using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- `references/src/sources/*.py` - individual free-source adapters

## Why This Layout

- `SKILL.md` remains a short operator guide instead of a full manual.
- Supporting prose and implementation details live under `references/` for progressive disclosure.
- The code bundle stays self-contained and runnable with `python -m references.src.mcp_server`.
