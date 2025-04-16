import scrapy


class HttpbinSpider(scrapy.Spider):
    name = "httpbin"
    allowed_domains = ["httpbin.org"]
    start_urls = ["https://httpbin.org/ip"]

    def parse(self, response):
        print(response.text)
