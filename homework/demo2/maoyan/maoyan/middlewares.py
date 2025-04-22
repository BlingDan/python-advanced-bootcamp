# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from itemadapter import is_item, ItemAdapter
from fake_useragent import UserAgent
import re
import time
import scrapy
import random
import logging

class MaoyanSpiderMiddleware:
    
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

class MaoyanDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

class AjaxRequestHanderMiddleware():

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        # 使用 crawler.settings 获取配置或 spider.logger 获取 logger
        # 使用 crawler.spider 获取 spider 实例
        s.logger = logging.getLogger('maoyan.AjaxRequestHanderMiddleware')
        return s
    
    def process_request(self, request, spider):
        match = re.search(r'maoyan\.com/films/(\d+)', request.url)
        if match and 'is_ajax' not in request.meta:
            movie_id = match.group(1)
            self.logger.info(f"Parsing AJAX response for movie_id: {movie_id} from {request.url}")

            # 构造ajax url
            timestamp = int(time.time() * 1000)
            ajax_url = f'https://www.maoyan.com/ajax/films/{movie_id}?timeStamp={timestamp}'

            ajax_headers = request.headers.copy()
            ajax_headers['Referer'] = request.url
            ajax_headers['Accept'] = '*/*' # AJAX 请求通常接受任何类型
            ajax_headers['X-Requested-With'] = 'XMLHttpRequest'  # 非常重要，说明这个是一个ajax请求，不然会被识别为普通的浏览器请求
             # 移除可能不适用于 AJAX 的 Headers (可选，但有时有帮助)   
            keys_to_remove = ['Sec-Fetch-Mode', 'Sec-Fetch-Site', 'Sec-Fetch-User', 'Upgrade-Insecure-Requests']
            for key in keys_to_remove:
                ajax_headers.pop(key, None)
            self.logger.info(f'Constructed ajax url: {ajax_url}')

            # 发送ajax请求
            # cookies = spider.parse_cookie_string(spider.RAW_COOKIE_STRING_FROM_BROWSER)
            ajax_request = scrapy.Request(
                url = ajax_url,
                method = 'GET',
                headers = ajax_headers,
                callback = request.callback,
                meta = {
                    'original_url' : request.url,
                    'movie_id': movie_id,
                    'is_ajax': True,
                    **request.meta, # 合并传递原始meta
                },
                dont_filter = True, # 不使用默认的过滤器，避免重复请求
            )
            return ajax_request

        # 如果请求不是ajax请求，则返回None
        return None
     
    def process_response(self, request, response, spider):
        return response
    
    def process_exception(self, request, exception, spider):
        self.logger.error(f'Error processing request {request.url}: {exception}')
        return None

# todo: 随机生成桌面浏览器user-agent
class RandomDeskTopUserAgentMiddleware():
    
    # from_crawler是中间件的标准类方法，在初始化中间件时候会调用这个方法
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        return s
    
    def __init__(self):
        self.logger = logging.getLogger('maoyan.RandomDeskTopUserAgentMiddleware')
        self.ua = UserAgent()
        self.desktop_browers = [
                'chrome',
                'firefox',
                'safari',
                'edge',
        ]
        pool_size = 50
        self.user_agent_pool = []

        # self.logger.info('Attemping to load user agent pool...')
        try :
            for _ in range(pool_size):
                browser_name = random.choice(self.desktop_browers)
                ua_string = getattr(self.ua, browser_name)
                self.user_agent_pool.append(ua_string)
        except Exception as e:
            self.logger.warning(f'Could not load UA from {browser_name}: {e}. Skipping this one')
        
        if not self.user_agent_pool:
            self.logger.error('Failed to load any user agent. Middleware RandomDeskTyopUserAgentMiddleware  potentially disastrous')
            self.user_agent_pool = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36']
        else:
            self.logger.info(f'Successfully loaded {len(self.user_agent_pool)} user agents')

    def process_request(self, request, spider):
        if not self.user_agent_pool:
            self.logger.warning('No user agent available. Using default one')
            request.headers.set('User-Agent', self.user_agent_pool[0])
        else:
            request.headers['User-Agent'] = random.choice(self.user_agent_pool)
        
        
        self.logger.info(f'Using User-Agent: {request.headers.get("User-Agent")}')
        return None