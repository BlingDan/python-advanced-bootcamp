# 这里同样引用了pipline midedlewares等
import scrapy
from bs4 import BeautifulSoup
from spiders.items import DouBanMovieItem 


class MoviesSpider(scrapy.Spider):
    name = "movies" # 爬虫名称 运行时候很重要
    allowed_domains = ["movie.douban.com"] # 允许爬取的域名，防止无限爬取
    start_urls = ["https://movie.douban.com/top250"] # 第一次发起的请求，获取一部分头部信息等
    
    # 注释默认的parse方法，重写parse方法
    # def parse(self, response):
    #     pass

    # 爬虫启动时，会自动调用start_requests方法，并且只会被调用一次用于生成初始的Request对象
    # 这个函数实现翻页功能，对每个url发起请求并调用parse方法进行处理
    def start_requests(self):
        for i in range(0, 3):
            url = f'https://movie.douban.com/top250?start={i*25}'
            yield scrapy.Request(url=url, callback=self.parse1)
    

    def parse1(self, response):
        items = []

        soup = BeautifulSoup(response.text, 'html.parser')
        title_list = soup.find_all('div', attrs={'class', 'hd'})

        for i in title_list: 
            item = DouBanMovieItem()
            title = i.find('a').find('span',).text
            link = i.find('a').get('href')
            item['title'] = title
            item['link'] = link
            
            # 返回请求或者item对象交给engin, 由engin决定如何处理: 
            # 1. 交给调度器入队列
            # 2. 交给下载器下载
            # 3. 交给spider解析

            # meta: dict[str, Any] | None = None ： 用于在请求之间传递参数 item，depth等等
            yield scrapy.Request(url=link, meta={'item': item}, callback=self.parse2)            


    # 解析具体页面 获取电影详细信息
    def parse2(self, response):
        item = response.meta['item'] 
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', attrs={'class':'related-info'}).get_text().strip()
        item['detail'] = content

        yield item

