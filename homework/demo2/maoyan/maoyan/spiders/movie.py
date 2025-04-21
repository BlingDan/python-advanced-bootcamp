import scrapy
from fake_useragent import UserAgent
import re
import time
from maoyan.items import MaoyanItem

# TODO: 将 AJAX 请求的处理逻辑放到 middleware， Spider 只需要关注核心业务逻辑（解析页面、提取数据），Middleware 负责处理 AJAX 请求的技术细节
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    RAW_COOKIE_STRING_FROM_BROWSER = (
        '__mta=150256137.1745110481671.1745122443414.1745197819169.21; uuid_n_v=v1; uuid=2C18EB701D8211F09556811A74262E1C79A68A4C875F41A39971FC60998C63D9; _lxsdk_cuid=19650b0b8d1c8-0a2657e6b845cf-26011d51-190140-19650b0b8d1c8; _ga=GA1.1.1984843978.1745110481; WEBDFPID=55y43zwx98vv57vxywx13890uxvy9w8x80349u4w99397958x8wy6z9z-1745201352032-1745114951264KAQCOISfd79fef3d01d5e9aadc18ccd4d0c95071013; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; token=AgHGJ2yWcBWwAgJHxykt72gVhpvCq3dfEjayTdPFlF03qikP3oGFkC-ByQnOCvTK5bvcPDAwE-pkmAAAAACfKAAAdrx5Oirh0W-TR-Xm6cGiwOaISF_z_JUyrZjKlZGoXNtL1pa8tbmJER-OaUuf7KH4; uid=3147436124; uid.sig=CB2BxeZ6qXR8F7N0Y7d7eaX7t-c; _lxsdk=2C18EB701D8211F09556811A74262E1C79A68A4C875F41A39971FC60998C63D9; _csrf=72a8c023a7af730071df82d84801cd77288646e372f5b0af4846abbe9f6f074a; Hm_lvt_e0bacf12e04a7bd88ddbd9c74ef2b533=1745110481,1745195252; HMACCOUNT=1D786444578FCCAE; Hm_lpvt_e0bacf12e04a7bd88ddbd9c74ef2b533=1745198246; __mta=150256137.1745110481671.1745197819169.1745198246402.22; _ga_WN80P4PSY7=GS1.1.1745197818.7.1.1745198248.0.0.0; _lxsdk_s=19655be39c7-04a-9b8-667%7C%7C18'
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
                dont_filter=True,  # 不进行URL去重
                meta={
                    'dont_redirect': True,  # 不进行重定向
                    'handle_httpstatus_list': [301, 302]  # 处理这些状态码
                }
            )

    def parse(self, response):
        self.logger.info(f"Parsing response from url: {response.url}")

        # Get the first 3 movie links 
        movie_links = response.xpath('//div[@class="channel-detail movie-item-title"]/a/@href').getall()[:3]
        
        for link in movie_links:
            # Create full URL
            movie_url = response.urljoin(link)
            self.logger.info(f"Found movie URL: {movie_url}")
            
            yield scrapy.Request(
                url=movie_url,
                callback=self.parse_movie_page,
                headers=self.headers,
                cookies=self.parse_cookie_string(self.RAW_COOKIE_STRING_FROM_BROWSER)
            )

    def parse_movie_page(self, response):
        """ 处理电影详细页的初始HTML，提取movie_id并且构造ajax请求
        Args:
            response (_type_): _description_
        """
        self.logger.info(f'Parsing movie page: {response.url}')

        # 提取movie_id
        match = re.search(r'/films/(\d+)', response.url)
        if not match:
            self.logger.error(f'No movie_id found in URL: {response.url}')
            return
        movie_id = match.group(1)
        self.logger.info(f'Found movie_id: {movie_id}')

        # 构造ajax请求
        timestamp = int(time.time() * 1000) # 获取当前时间戳
        ajax_url = f'https://www.maoyan.com/ajax/films/{movie_id}?timeStamp={timestamp}'
        self.logger.info(f'Contrusted ajax url: {ajax_url}')

        # 发送ajax请求
        ajax_headers = self.headers.copy()
        ajax_headers['Referer'] = response.url
        ajax_headers['Accept'] = '*/*' # AJAX 请求通常接受任何类型
        ajax_headers['X-Requested-With'] = 'XMLHttpRequest'  # 非常重要，说明这个是一个ajax请求，不然会被识别为普通的浏览器请求
        ajax_headers.pop('Sec-Fetch-Dest', None)    # 移除可能不适用于 AJAX 的 Headers (可选，但有时有帮助)
        ajax_headers.pop('Sec-Fetch-Mode', None)
        ajax_headers.pop('Sec-Fetch-Site', None)
        ajax_headers.pop('Sec-Fetch-User', None)
        ajax_headers.pop('Upgrade-Insecure-Requests', None)

        cookies = self.parse_cookie_string(self.RAW_COOKIE_STRING_FROM_BROWSER)
        yield scrapy.Request(
            url=ajax_url,
            callback=self.parse_movie_ajax,
            headers=ajax_headers,
            cookies=cookies,
            method='GET',
            meta={
                'dont_redirect': True,
                'movie_id': movie_id
            }
        )
    
    def parse_movie_ajax(self, response):
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
