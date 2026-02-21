import httpx
import asyncio
import time

async def test_endpoints():
    # We need a token. Let's assume the user is 'LUCAS' and we can create a token if we know the password,
    # or we can bypass auth for testing if we modify the code.
    # Bypassing auth is easier for a quick check.
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/",
        "/health",
        "/api/v1/stats/",
        "/api/v1/jobs/recommended?limit=5",
    ]
    
    async with httpx.AsyncClient() as client:
        for ep in endpoints:
            start = time.time()
            try:
                r = await client.get(base_url + ep, timeout=5.0)
                print(f"GET {ep}: {r.status_code} in {time.time() - start:.4f}s")
                if r.status_code == 200:
                    print(f"   Response: {r.text[:100]}")
            except Exception as e:
                print(f"GET {ep}: FAILED - {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
