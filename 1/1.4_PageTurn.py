# 通过观察url构造实现翻页功能
import requests
from bs4 import BeautifulSoup as bs
from time import sleep

def get_movie_info(myurl):
    """
    myurl: 每个页面url如 https://movie.douban.com/top250?start=50&filter=
    """
    header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Connection': 'keep-alive'
    }
    response = requests.get(myurl, headers=header)

    bs_info = bs(response.text, 'html.parser')
    for all_tags in bs_info.find_all('div', attrs={'class':'hd'}):
        for atags in all_tags.find_all('a',):
            print(atags.get('href'))
            print(atags.find('span',).text)

urls = tuple(f'https://movie.douban.com/top250?start={page * 25}&filter=' for page in range(10))
print(urls)

sleep(5)
for url in urls:
    get_movie_info(url)
    sleep(5)