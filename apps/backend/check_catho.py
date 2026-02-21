import asyncio
import httpx

async def test_catho():
    url = "https://www.catho.com.br/vagas/python/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)
    r = await client.get(url, headers=headers)
    print(r.status_code)
    
if __name__ == "__main__":
    asyncio.run(test_catho())
