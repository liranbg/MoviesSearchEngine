# Importing base64 library because we'll need it ONLY in case if the proxy we are going to use requires authentication
import random
import logging
from scrapy.core.downloader.webclient import _parse


# Start your middleware class
class ProxyMiddleware(object):
    def __init__(self):
        self.proxy_list = [
            "http://us-dc.proxymesh.com:31280",
            "http://ch.proxymesh.com:31280",
            "http://us-il.proxymesh.com:31280",
            "http://uk.proxymesh.com:31280",
            "http://us.proxymesh.com:31280",
            "socks5://proxy-nl.privateinternetaccess.com:1080",
            #"",
            "http://open.proxymesh.com:31280"
        ]

    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy
        if len(self.proxy_list) > 0:
            proxy = random.choice(self.proxy_list)
            #logging.info("Using proxy from {}".format(proxy))
            request.meta['proxy'] = proxy



