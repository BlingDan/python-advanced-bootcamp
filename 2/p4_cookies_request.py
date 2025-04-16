import time
import requests
from fake_useragent import UserAgent

ua = UserAgent()
headers = {
    'User-Agent' : ua.random,
    'Referer' : 'https://accounts.douban.com/passport/login?source=movie'
}

# 会话对象：同一个Session对象发送的请求共享cookie
s = requests.Session()

login_url = 'https://accounts.douban.com/j/mobile/login/basic'
form_data = {
    'remeber' : 'true',
    'name': '***',
    'password': '***',
}
response = s.post(login_url, headers=headers, data=form_data)

# 被反爬虫之后需要图形验证码
print(response.text)