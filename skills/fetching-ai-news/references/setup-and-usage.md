# Setup and Usage

Detailed usage for the bundled reference implementation that ships with this skill.

## Setup

```bash
cd skills/fetching-ai-news
pip install -r references/requirements.txt
```

Optional Telegram setup:

```bash
cp references/.env.example .env
# Fill TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID before using send=true
```

## Run as an MCP Server

```bash
cd skills/fetching-ai-news
python -m references.src.mcp_server
```

The server exposes one tool: `run_ai_news_digest`.

Parameters:
- `hours` (default `13`): fetch window in hours
- `max_per_category` (default `6`): cap for each category
- `send` (default `false`): deliver the formatted digest to Telegram

## Run as a Python Module

```python
from references.src.app import run_digest

result = run_digest(hours=13, max_per_category=6, send=False)
print(result["raw_count"])
print(len(result["categorized"]["ai"]))
print(len(result["categorized"]["vibe_coding"]))
```

## Telegram Notes

Only set `send=true` when the environment already contains `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

Minimal setup flow:
1. Create a bot via `@BotFather`
2. Send the bot a message
3. Read the chat id from `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Export the two variables or copy from `references/.env.example`

## Related References

- [output-format.md](output-format.md) - return payload and presentation guidance
- [implementation-layout.md](implementation-layout.md) - bundled file layout and module roles
