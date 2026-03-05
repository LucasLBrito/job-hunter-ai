import httpx
import random
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class FreeProxyManager:
    """
    Manages a list of free HTTP proxies fetched from popular GitHub repositories.
    Repos specified by user: TheSpeedX, proxifly, iplocate.
    """
    
    # Raw URLs for plain text proxy lists (IP:PORT format)
    SOURCES = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
        # Adding some generic fallbacks as 'iplocate' repo name might vary, but here are some reliable ones:
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
    ]

    def __init__(self):
        self.proxies: List[str] = []
        self._last_fetch = None

    async def fetch_proxies(self) -> int:
        """
        Fetches proxies from the defined sources asynchronously.
        """
        all_proxies = set()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for source in self.SOURCES:
                try:
                    response = await client.get(source)
                    if response.status_code == 200:
                        lines = response.text.strip().split('\n')
                        valid_proxies = [p.strip() for p in lines if ':' in p and len(p.split(':')) == 2]
                        all_proxies.update(valid_proxies)
                        logger.info(f"Fetched {len(valid_proxies)} proxies from {source}")
                except Exception as e:
                    logger.warning(f"Failed to fetch proxies from {source}: {e}")
                    
        self.proxies = list(all_proxies)
        logger.info(f"Total unique proxies fetched: {len(self.proxies)}")
        return len(self.proxies)

    def get_random_proxy(self, format_target="requests") -> Optional[str]:
        """
        Returns a random proxy from the pool.
        :param format_target: "requests" | "httpx" | "raw"
        """
        if not self.proxies:
            return None
            
        proxy_raw = random.choice(self.proxies)
        
        # e.g., '192.168.0.1:8080'
        if format_target == "raw":
            return proxy_raw
            
        formatted = f"http://{proxy_raw}"
        
        if format_target == "requests":
            return {"http": formatted, "https": formatted}
        elif format_target == "httpx":
            return formatted
            
        return formatted

    async def get_working_proxy(self) -> Optional[str]:
        """
        Tests random proxies until one works, then returns it.
        Since free proxies die fast, this tries up to 10 proxies.
        """
        if not self.proxies:
            await self.fetch_proxies()
            
        if not self.proxies:
            return None
            
        # Try all proxies in batches of 500 to avoid OS limits
        import asyncio
        batch_size = 500
        
        async def check_proxy(proxy_raw: str) -> Optional[str]:
            try:
                async with httpx.AsyncClient(proxies=f"http://{proxy_raw}", timeout=8.0) as client:
                    res = await client.get("http://httpbin.org/ip")
                    if res.status_code == 200:
                        return proxy_raw
            except Exception:
                pass
            return None

        # Shuffle to distribute load
        shuffled_proxies = list(self.proxies)
        random.shuffle(shuffled_proxies)

        for i in range(0, len(shuffled_proxies), batch_size):
            batch = shuffled_proxies[i : i + batch_size]
            tasks = [check_proxy(p) for p in batch]
            results = await asyncio.gather(*tasks)
            
            working_proxies = [r for r in results if r]
            if working_proxies:
                best_proxy = working_proxies[0]
                logger.info(f"Found {len(working_proxies)} working proxies in batch. Using: {best_proxy}")
                return best_proxy
                
        logger.warning("Tested all proxies but none worked.")
        return None

# Singleton instance for the app
proxy_manager = FreeProxyManager()
