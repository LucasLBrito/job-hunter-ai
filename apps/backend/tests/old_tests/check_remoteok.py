import httpx
import feedparser
import asyncio

async def check_remoteok():
    url = "https://remoteok.com/rss"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        feed = feedparser.parse(r.text)
        print(f"Entries: {len(feed.entries)}")
        for e in feed.entries[:3]:
            print(f"- {e.title}")

if __name__ == "__main__":
    asyncio.run(check_remoteok())
