import scrapy
from bs4 import BeautifulSoup

class VagasSpider(scrapy.Spider):
    name = "vagas"
    allowed_domains = ["vagas.com.br"]
    
    def __init__(self, query="python", limit=20, *args, **kwargs):
        super(VagasSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.limit = int(limit)
        self.scraped_count = 0

    def start_requests(self):
        query_formatted = self.query.replace(" ", "-")
        url = f"https://www.vagas.com.br/vagas-de-{query_formatted}"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.select("a.link-detalhes-vaga")
        
        for a in job_cards:
            if self.scraped_count >= self.limit:
                break
                
            try:
                title = a.get_text(strip=True)
                job_url = "https://www.vagas.com.br" + a.get("href", "")
                parent = a.find_parent("li")
                if not parent:
                    continue
                
                company_elem = parent.find(class_="empresa")
                company = company_elem.get_text(strip=True) if company_elem else "Nao revelado"
                
                loc_elem = parent.find(class_="vaga-local")
                location = loc_elem.get_text(strip=True) if loc_elem else "Brasil"
                
                desc_elem = parent.find(class_="detalhes")
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                self.scraped_count += 1
                
                yield {
                    "source": "vagas.com.br",
                    "url": job_url,
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description,
                    "raw_html": str(parent) # Enviar um pedaço do HTML para o MongoDB (raw)
                }
            except Exception as e:
                self.logger.warning(f"Error parsing job card: {e}")
