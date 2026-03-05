import scrapy
from bs4 import BeautifulSoup

class CathoSpider(scrapy.Spider):
    name = "catho"
    allowed_domains = ["catho.com.br"]
    
    def __init__(self, query="python", limit=20, *args, **kwargs):
        super(CathoSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.limit = int(limit)
        self.scraped_count = 0

    def start_requests(self):
        url = f"https://www.catho.com.br/vagas/?q={self.query}"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        job_lists = soup.find("ul", class_=lambda x: x and "gtm-job-list" in x) or soup.find("ul", {"id": "search-result"})
        if not job_lists:
            job_cards = soup.find_all("article")
        else:
            job_cards = job_lists.find_all("li")

        for card in job_cards:
            if self.scraped_count >= self.limit:
                break
                
            try:
                title_elem = card.find("h2")
                if not title_elem:
                    continue
                link_elem = title_elem.find("a")
                if not link_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                job_url = link_elem.get("href", "")
                if not job_url.startswith("http"):
                    job_url = f"https://www.catho.com.br{job_url}"

                company = "Nao revelado (Catho)"
                company_candidate = card.find("span", attrs={"data-gtm-element": "job-company-name"})
                if company_candidate:
                    company = company_candidate.get_text(strip=True)
                    
                location = "Brasil"
                loc_elem = card.find("a", href=lambda h: h and "/vagas/" in h)
                if loc_elem:
                    location = loc_elem.get_text(strip=True)

                self.scraped_count += 1
                
                yield {
                    "source": "catho",
                    "url": job_url,
                    "title": title,
                    "company": company,
                    "location": location,
                    "raw_html": str(card) # Raw data approach
                }
            except Exception as e:
                self.logger.warning(f"Error parsing catho job card: {e}")
