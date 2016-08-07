from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler
from scrapy.core.downloader.handlers.http11 import ScrapyAgent
from twisted.internet import reactor
from txsocksx.http import SOCKS5Agent
from twisted.internet.endpoints import TCP4ClientEndpoint
from scrapy.core.downloader.webclient import _parse
import base64


class TorProxyDownloadHandler(HTTP11DownloadHandler):

    def download_request(self, request, spider):
        """Return a deferred for the HTTP download"""
        agent = ScrapyTorAgent(contextFactory=self._contextFactory, pool=self._pool)
        return agent.download_request(request)


class ScrapyTorAgent(ScrapyAgent):
    def _get_agent(self, request, timeout):
        bindaddress = request.meta.get('bindaddress') or self._bindAddress
        proxy = request.meta.get('proxy')
        if proxy:
            proxy_scheme, _, proxy_host, proxy_port, _ = _parse(proxy)

            if proxy_scheme == 'socks5':
                endpoint = TCP4ClientEndpoint(reactor, proxy_host, proxy_port, timeout=timeout, bindAddress=bindaddress)
                agent = SOCKS5Agent(reactor, proxyEndpoint=endpoint,  endpointArgs=dict(methods={'login': ('x8055734', 'gcDamDU8Ty')}))
                return agent
            elif proxy_scheme == "http":
                # Use the following lines if your proxy requires authentication
                proxy_user_pass = "ripperripper:ripperripper123"
                # setup basic authentication for the proxy
                encoded_user_pass = base64.encodestring(proxy_user_pass)
                request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass

        return super(ScrapyTorAgent, self)._get_agent(request, timeout)
