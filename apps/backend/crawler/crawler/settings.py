BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

ROBOTSTXT_OBEY = False

# --- Configuração de Proxy ---
# Exemplo de lista de proxies para o RotateProxyMiddleware:
PROXY_LIST = [
    # 'http://111.111.111.111:8080',
    # 'http://usuario:senha@222.222.222.222:8080',
]

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400, 
    # Ative a que for adequada para seu caso (Lista ou Serviço pago)
    'crawler.middlewares.RotateProxyMiddleware': 350,
    # 'crawler.middlewares.ServiceProxyMiddleware': 350,
}

ITEM_PIPELINES = {
   'crawler.pipelines.MongoPipeline': 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = 'utf-8'
