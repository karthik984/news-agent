import os
import requests
from anthropic import Anthropic
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ---- Configure your topics here ----
TOPICS = [
    {
        "name": "Iran US War Update",
        "query": "Iran US war update today site:reuters.com OR site:bbc.com"
    },
    {
        "name": "AI Engineering News",
        "query": "AI engineering news this week site:techcrunch.com OR site:venturebeat.com"
    },
    {
        "name": "Stock Market Update",
        "query": "US stock market today dow nasdaq S&P site:marketwatch.com OR site:finance.yahoo.com"
    },
]
# ------------------------------------

def search_web(query: str) -> str:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    if not results:
        return "No results found."
    output = ""
    for r in results:
        output += f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n\n"
    return output

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def get_news_digest(query: str) -> str:
    print(f"Researching: {query}")
    search_results = search_web(query)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system="You are a news summarizer. Given search results, write a concise 3-5 sentence summary of the latest developments. Be factual and direct. Use plain text, no markdown.",
        messages=[{
            "role": "user",
            "content": f"Topic: {query}\n\nSearch Results:\n{search_results}\n\nWrite a concise news summary."
        }]
    )
    return response.content[0].text

def run():
    print("Running news agent...\n")
    full_digest = "🗞 *Daily News Digest*\n\n"

    for topic in TOPICS:
        summary = get_news_digest(topic["query"])
        full_digest += f"*{topic['name'].upper()}*\n{summary}\n\n"
        full_digest += "─" * 30 + "\n\n"

    send_telegram(full_digest)
    print("Digest sent to Telegram!")

if __name__ == "__main__":
    run()
