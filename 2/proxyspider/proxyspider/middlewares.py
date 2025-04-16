# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from collections import defaultdict
import random
from urllib.parse import urlparse
from typing import Optional
from scrapy import Request, signals
from scrapy.exceptions import NotConfigured

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware

class ProxyspiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn't have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

class ProxyspiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

# TODO: 随机代理地址无法使用，不清楚发送的request是http还是https 待验证，输出不了结果
# 随机使用代理IP，继承HttpProxyMiddleware
class RandomHttpProxyMiddleware(HttpProxyMiddleware):

    def __init__(self, auth_encoding = "utf-8", proxy_list = None):
        self.auth_encoding = auth_encoding
        self.proxies = defaultdict(list)
        for proxy in proxy_list:
            parser = urlparse(proxy)
            self.proxies[parser.scheme].append(parser.netloc)  
        print(f'__init__ proxies: {self.proxies}')

    # 这是一个类方法，第一个参数cls代表类本身
    # 当Scrapy创建中间件实例时候，它就会调用from_crawler方法
    # return cls(auth_encoding, http_proxy_list) 实际上等同于return RandomHttpProxyMiddleware(auth_encoding, http_proxy_list)
    # 因此，返回调用cls的参数顺序应该保持一致
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.get("HTTP_PROXY_LIST"):
            raise NotConfigured

        http_proxy_list = crawler.settings.get("HTTP_PROXY_LIST")
        print(f'http_proxy_list: {http_proxy_list}')
        auth_encoding = crawler.settings.get("HTTPPROXY_AUTH_ENCODING", "utf-8")
        return cls(auth_encoding, http_proxy_list)

    def process_request(self, request, spider):
        # 为每个请求设置代理
        scheme = urlparse(request.url).scheme
        self._set_proxy_and_creds(request, None, None, scheme)
        return None

    def _set_proxy_and_creds(
        self,
        request: Request,
        proxy_url: Optional[str],
        creds: Optional[bytes],
        scheme: Optional[str],
    ) -> None:
        proxy_url = random.choice(self.proxies[scheme])
        request.meta["proxy"] = proxy_url
