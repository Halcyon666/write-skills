# Output Format

The bundled MCP tool returns a dictionary with these top-level fields:

```json
{
  "raw_count": 150,
  "ai_count": 6,
  "vibe_coding_count": 6,
  "sent": false,
  "messages": ["...", "..."],
  "items": {
    "ai": [{"title": "...", "url": "...", "source": "...", "score": 1.23, "published_at": "..."}],
    "vibe_coding": [{"title": "...", "url": "...", "source": "...", "score": 0.98, "published_at": "..."}]
  }
}
```

## Presentation Guidance

- Use `raw_count`, `ai_count`, and `vibe_coding_count` for the high-level summary.
- Use `items.ai` and `items.vibe_coding` when the user wants links or ranked highlights.
- Use `messages` only when the user wants preformatted Telegram Markdown output.
- If `send=true`, confirm the final delivery state from `sent`.

## Empty or Partial Results

- `raw_count=0` usually means the sources returned nothing in the chosen time window.
- A non-zero `raw_count` with one empty category is valid; the classifier may not have found enough matching items.
- Treat missing Telegram delivery as a configuration issue, not as a scraping failure.
