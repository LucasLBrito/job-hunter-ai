import httpx
import asyncio

async def check_remoteok_json():
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Items: {len(data)}")
            for e in data[:5]:
                if isinstance(e, dict):
                   print(f"- {e.get('position')} at {e.get('company')}")

if __name__ == "__main__":
    asyncio.run(check_remoteok_json())
