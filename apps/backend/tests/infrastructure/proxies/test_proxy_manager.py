import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.infrastructure.proxies.manager import proxy_manager

async def main():
    print("Fetching proxies...")
    count = await proxy_manager.fetch_proxies()
    print(f"Total proxies in pool: {count}")
    
    if count > 0:
        print("\nGetting 3 random proxies:")
        for _ in range(3):
            print(" -", proxy_manager.get_random_proxy(format_target="raw"))
            
        print("\nTesting for ONE working proxy (this might take a few seconds)...")
        working = await proxy_manager.get_working_proxy()
        if working:
            print(f"✅ Found working proxy: {working}")
        else:
            print("❌ Could not find a working proxy among the sampled ones.")
            
if __name__ == "__main__":
    asyncio.run(main())
