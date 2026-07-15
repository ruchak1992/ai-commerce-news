# AI Commerce News

A small Claude-powered agent that researches recent AI-in-commerce news and writes a short daily briefing — three stories, each with a one-line "what" and "why," plus a takeaway.

## How it works

`agent.py` calls Claude with the `web_search` tool, prompting it to run 2-3 searches for recent AI + retail/ecommerce news and return a single formatted briefing. The result gets sent to Telegram in chunks (Telegram has a message-length limit).

```
🤖 AI IN COMMERCE BRIEFING

1. [Headline]
What: ...  Why: ...

(3 stories total)

📌 Takeaway: ...
```

## Running it

```bash
pip install anthropic requests
export ANTHROPIC_API_KEY=...
export TELEGRAM_TOKEN=...
export TELEGRAM_CHAT_ID=...
python agent.py
```

A GitHub Actions workflow (`.github/workflows/daily-digest.yml`) is set up to run this automatically, currently configured for **manual trigger only** (`workflow_dispatch`) rather than a daily schedule.

## Why I built this

I wanted a fast way to stay current on AI × commerce without doom-scrolling for it — a small personal agent that does the searching and summarizing so the news shows up in Telegram instead of me having to go find it.
