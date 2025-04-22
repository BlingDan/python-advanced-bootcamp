# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class MaoyanPipeline:
    pass

class MaoyanCsvPipeline:
    def __init__(self):
        self.file = open('maoyantop10.csv', 'a', encoding='utf-8')

    def process_item(self, item, spider):
        # Convert movie_types list to string
        movie_types_str = '|'.join(item['movie_types'])
        self.file.write(f"{item['movie_name']},{movie_types_str},{item['movie_update_time']}\n")
        return item

    def close_spider(self, spider):
        self.file.close()
    