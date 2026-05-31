import anthropic
import requests
import os
from datetime import date

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

def run_digest():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = date.today().strftime("%B %d, %Y")

    messages = [{"role": "user", "content": f"Give me today's ({today}) AI in commerce briefing."}]
    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    # Agentic loop
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            tools=tools,
            system="""You are a commerce & retail tech analyst. 
Search for the latest AI in commerce, retail, and ecommerce news from the past 24 hours.
Do 4-5 searches covering different angles: funding rounds, product launches, retailer adoption, startups, big tech moves.
Then write a concise morning briefing with:
- 🔑 3-5 headline stories (2-3 sentences each)
- 💡 Why it matters for each
- 📌 One overall 'so what' takeaway at the end
Keep it punchy. Use emojis for readability. Format for Telegram (no markdown headers, just bold with *).""",
            messages=messages
        )

        # Claude is done — extract and return final text
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

        # Claude wants to search — append full response and loop
        messages.append({"role": "assistant", "content": response.content})

        # Collect tool_use block IDs and pass empty results back
        # (web_search is server-side — results are already in response.content)
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": ""
                })

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        else:
            # No tool use and not end_turn — extract whatever text we have
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            break

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown"
        })

if __name__ == "__main__":
    print("Running digest...")
    digest = run_digest()
    print(digest)  # also print to logs so we can debug
    send_telegram(digest)
    print("Sent!")
