import requests
from bs4 import BeautifulSoup
import csv
from fake_useragent import UserAgent
import json
import time

ua = UserAgent()
# url = "https://www.maoyan.com/films?showType=1"

def get_movie_info(movie_id):
    # 电影详情 API
    detail_url = f"https://m.maoyan.com/ajax/detailmovie?movieId={movie_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "m.maoyan.com",
        "Referer": f"https://m.maoyan.com/movie/{movie_id}",
        "Origin": "https://m.maoyan.com",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    cookies = {
        # input cookie from browser
    }
    
    try:
        response = requests.get(detail_url, headers=headers, cookies=cookies)
        response.encoding = 'utf-8'
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            movie_data = data.get('detailMovie', {})
            print(data)
            # if movie_data:
            #     print("\n电影信息:")
            #     print(f"名称: {movie_data.get('nm')}")
            #     print(f"英文名: {movie_data.get('enm')}")
            #     print(f"评分: {movie_data.get('sc')}")
            #     print(f"导演: {movie_data.get('dir')}")
            #     print(f"主演: {movie_data.get('star')}")
            #     print(f"类型: {movie_data.get('cat')}")
            #     print(f"地区: {movie_data.get('src')}")
            #     print(f"时长: {movie_data.get('dur')}")
            #     print(f"上映时间: {movie_data.get('pubDesc')}")
            #     print(f"简介: {movie_data.get('dra')}")
            # else:
            #     print("未找到电影数据")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

# 测试获取电影信息
get_movie_info('1519877')

