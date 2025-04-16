# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os


class SpidersPipeline:
    # def process_item(self, item, spider):
    #     return item

    # 每一个item管道组件都会调用process_item方法，并且必须返回一个item对象
    def process_item(self, item, spider):
        # 打印当前工作目录
        print(f"-----------------------当前工作目录: {os.getcwd()}")
        # 打印文件保存路径
        file_path = os.path.join(os.getcwd(), 'movies.csv')
        print(f"-----------------------文件将保存在: {file_path}")

        title = item['title']
        link = item['link']
        detail = item['detail']

        output = f'|{title}|\t|{link}|\t|{detail}|\n\n'
        with open(file_path, 'a+', encoding='utf-8') as f:
            f.write(output)
        return item