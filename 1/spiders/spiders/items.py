# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# class SpidersItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pas

# 定义一个item类，用于存储数据
class DouBanMovieItem(scrapy.Item):
    # scrapy.Field() 定义一个字段，用于存储数据 类似于 Python 中的字典
    title = scrapy.Field()
    link = scrapy.Field()
    detail = scrapy.Field()
