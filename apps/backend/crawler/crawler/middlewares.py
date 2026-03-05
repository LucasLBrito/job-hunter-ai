import random
from scrapy import signals

class RotateProxyMiddleware:
    """
    Middleware para rotacionar Proxies a partir de uma lista fornecida no settings.py.
    """
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list or []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_list=crawler.settings.get('PROXY_LIST')
        )

    def process_request(self, request, spider):
        if not self.proxy_list:
            return  # Nenhuma lista configurada, não injeta proxy

        proxy = random.choice(self.proxy_list)
        request.meta['proxy'] = proxy
        spider.logger.debug(f'Usando Proxy (Rotativo): {proxy}')


class ServiceProxyMiddleware:
    """
    Middleware para usar um serviço de proxy pago (ex: Bright Data, Smartproxy).
    O próprio servidor roteará o IP transparenteamente.
    """
    def process_request(self, request, spider):
        # Usuário e Senha do seu serviço de proxy
        user = "seu_usuario_cliente"
        password = "sua_senha_secreta"
        host = "gate.smartproxy.com"
        port = "7000"
        
        # Monta a URL completa
        proxy_url = f"http://{user}:{password}@{host}:{port}"
        
        request.meta['proxy'] = proxy_url
        spider.logger.debug(f'Usando Proxy (Serviço): {host}:{port}')
