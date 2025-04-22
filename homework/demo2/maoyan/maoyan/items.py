# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MaoyanItem(scrapy.Item):
    # define the fields for your item here like:
    movie_name = scrapy.Field()
    movie_types = scrapy.Field()
    movie_update_time = scrapy.Field()
    