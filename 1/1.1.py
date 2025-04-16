import requests
from bs4 import BeautifulSoup as bs



myurl = 'https://movie.douban.com/top250'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://movie.douban.com/',
    'Connection': 'keep-alive'
}

# request获取网页内容，bs进行解析
response = requests.get(myurl, headers=header)
bs_info = bs(response.text, 'html.parser')
print(bs_info)

for all_tags in bs_info.find_all('div', attrs={'class':'hd'}):
    for atags in all_tags.find_all('a',):
        print(atags.get('href'))
        print(atags.find('span',).text)