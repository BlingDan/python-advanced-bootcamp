# Xpath解析网页
import lxml.etree
import requests
import pandas as pd

myurl = 'https://movie.douban.com/subject/1292052/'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    # 'Referer': 'https://movie.douban.com/',
    'Connection': 'keep-alive'
}
response = requests.get(myurl, headers=header)

# xml化处理
selector = lxml.etree.HTML(response.text)

# 使用xpath获取正则表达式后需要加上text()  
file_name = selector.xpath('//*[@id="content"]/h1/span[1]/text()')
up_date= selector.xpath('//*[@id="info"]/span[10]/text()')
rating = selector.xpath('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()')
print(file_name)
print(up_date)
print(rating)

movie_list = [file_name, up_date, rating]
movie1 = pd.DataFrame(movie_list)
movie1.to_csv('./movie1.csv', encoding='utf-8')


