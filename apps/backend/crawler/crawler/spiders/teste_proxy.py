import scrapy

class TesteProxySpider(scrapy.Spider):
    name = 'teste_proxy'
    
    # Faz 5 requisições para ver se o IP muda
    start_urls = ['http://httpbin.org/ip' for _ in range(5)]
    
    # Garante que não use cache (para forçar nova requisição)
    custom_settings = {
        'HTTPCACHE_ENABLED': False
    }

    def parse(self, response):
        # Aqui ele imprime o IP que o site "viu"
        self.logger.info(f"RESPOSTA DO SITE: {response.text}")
        print(f"RESPOSTA DO SITE: {response.text}")
