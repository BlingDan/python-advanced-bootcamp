import scrapy
from fake_useragent import UserAgent
import re
import time
from maoyan.items import MaoyanItem

class MovieSpider(scrapy.Spider):
    name = "movie"
    allowed_domains = ["maoyan.com"]
    start_urls = ["https://maoyan.com/films?showType=3"]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.maoyan.com',
        'Referer': 'https://www.maoyan.com/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    RAW_COOKIE_STRING_FROM_BROWSER = (
           # input cookie from browser
    )

    def parse_cookie_string(self, cookie_string):
         """
         将一个 Cookie 字符串解析成字典
         """
         cookies = {}
         for cookie_part in re.split(r';\s*', cookie_string):
             if '=' in cookie_part:
                 name, value = cookie_part.split('=', 1)
                 cookies[name] = value
         return cookies

    '''
    scrapy是异步框架，有自己一套请求机制：middleware,schedule,downloader,spider等。
    从start_requests 的yield开始，scrapy会将request对象交给downloder处理，downloader通过各种middleware获取response,然后将response交给parse()回调函数
    如果直接使用request则不会经过middleware因为这是个同步框架直接得到了结果
    '''
    def start_requests(self):
        cookies = self.parse_cookie_string(self.RAW_COOKIE_STRING_FROM_BROWSER)
        
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers=self.headers,
                cookies=cookies,
            )

    def parse(self, response):
        self.logger.info(f"Parsing response from url: {response.url}")

        # Get the first n movie links 
        movie_links = response.xpath('//div[@class="channel-detail movie-item-title"]/a/@href').getall()[:3]
        
        for link in movie_links:
            # Create full URL
            movie_url = response.urljoin(link)
            self.logger.info(f"Found movie URL: {movie_url}")
            
            # Middleware将会拦截此请求，转化为ajax请求，并用下面的回调函数处理ajax响应
            yield scrapy.Request(
                url=movie_url,
                callback=self.parse_movie_details,
                headers=self.headers,
                cookies=self.parse_cookie_string(self.RAW_COOKIE_STRING_FROM_BROWSER),
            )
    

    def parse_movie_details(self, response):
        """ 解析 AJAX 返回的 HTML 片段
        Args:
            response (_type_): _description_
        """
        movie_id = response.meta.get('movie_id')
        original_url = response.meta.get('original_url')
        self.logger.info(f"Parsing AJAX response for movie_id: {movie_id} from {original_url}")

        # 提取电影信息
        movie_name = response.xpath('//div[@class="movie-brief-container"]/h1/text()').get()
        movie_types = response.xpath('//div[@class="movie-brief-container"]/ul/li[1]/a/text()').getall()
        movie_update_time = response.xpath('//div[@class="movie-brief-container"]/ul/li[3]/text()').get()


        item = MaoyanItem()
        item['movie_name'] = movie_name
        item['movie_types'] = movie_types
        item['movie_update_time'] = movie_update_time

        yield item
