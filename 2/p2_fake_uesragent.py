import fake_useragent
from fake_useragent import UserAgent

#从 fake-useragent 2.0.0 版本开始，verify_ssl 参数已被移除
ua = UserAgent()

print(ua.random)
print(ua.chrome)