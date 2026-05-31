import anthropic
import requests
import os
from datetime import date

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

def run_digest():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = date.today().strftime("%b %d, %Y")

    messages = [{"role": "user", "content": f"Today's AI commerce briefing ({today})."}]
    tools = [{"type": "web_search_20250305", "name": "web_search"}]
    all_text = []  # collect text across ALL iterations

    max_iterations = 8
    for i in range(max_iterations):
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2500,
            tools=tools,
            system="""Daily AI commerce briefing. Do 2-3 web searches for recent AI + retail/ecommerce news, then write the briefing in ONE response (don't split it across turns).

Output ONLY the briefing — no preamble.

Format (plain text, no markdown):
🤖 AI IN COMMERCE BRIEFING

1. [Headline]
What: 1 sentence. Why: 1 sentence.

(3 stories total)

📌 Takeaway: 1 sentence.""",
            messages=messages
        )

        # Collect any text in this response
        for block in response.content:
            if hasattr(block, "text") and block.text.strip():
                all_text.append(block.text)

        print(f"Iter {i+1}: stop={response.stop_reason}, text_blocks={sum(1 for b in response.content if hasattr(b,'text'))}, tool_uses={sum(1 for b in response.content if b.type=='tool_use')}")

        if response.stop_reason == "end_turn":
            break

        messages.append({"role": "assistant", "content": response.content})
        tool_results = [
            {"type": "tool_result", "tool_use_id": b.id, "content": ""}
            for b in response.content if b.type == "tool_use"
        ]
        if not tool_results:
            break
        messages.append({"role": "user", "content": tool_results})

    return "\n".join(all_text) if all_text else "Digest generation failed."

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for i, chunk in enumerate(chunks):
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk})
        print(f"Chunk {i+1}/{len(chunks)} — {r.status_code}: {r.text[:150]}")

if __name__ == "__main__":
    print("Running digest...")
    digest = run_digest()
    print(f"Length: {len(digest)} chars\n{'='*50}\n{digest}\n{'='*50}")
    send_telegram(digest)
    print("Done!")
