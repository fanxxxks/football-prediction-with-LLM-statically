import requests
import schedule
import time
import os
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


NEWS_API_KEY = "63bf0eb9f22b4a1eb7f6899fc3d48461"  
FOOTBALL_API_KEY = "b6015161c2204f5bab09fe5cde8d589b"  
NEWS_API_DOMAIN = "https://newsapi.org"  


def check_api_keys():
    if "YOUR_REAL_" in NEWS_API_KEY or NEWS_API_KEY.strip() == "":
        raise ValueError("111")
    if "YOUR_REAL_" in FOOTBALL_API_KEY or FOOTBALL_API_KEY.strip() == "":
        raise ValueError("222")


session = requests.Session()
retry_strategy = Retry(
    total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)


def get_project_data_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def crawl_news():
    try:
        
        news_url = f"{NEWS_API_DOMAIN}/v2/everything?q=football&language=en&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
        response = session.get(news_url, timeout=30)
        response.raise_for_status()  
        news_data = response.json()["articles"]
        
        today = datetime.now().strftime("%Y-%m-%d")
        data_dir = get_project_data_dir()
        filename = os.path.join(data_dir, f"news_data_{today}.txt")
        
        with open(filename, "w", encoding="utf-8") as f:
            for news in news_data:
                title = news["title"].replace("\n", " ").strip()
                published_at = news["publishedAt"]
                url = news["url"]
                description = news["description"].replace("\n", " ").strip() if news["description"] else "无摘要"
                f.write(f"{title}\n发布时间: {published_at}\n链接: {url}\n摘要: {description}\n\n")
        print(f"新闻数据已写入项目内：{filename}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("333")
        else:
            print(f"新闻API请求失败：{e.response.status_code} - {e.response.reason}")
    except Exception as e:
        print(f"新闻抓取失败：{str(e)}")


def crawl_match_data():
    try:
        match_url = "https://api.football-data.org/v4/competitions/PL/standings"
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}  
        response = session.get(match_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        standings = data["standings"][0]["table"]
        
        today = datetime.now().strftime("%Y-%m-%d")
        data_dir = get_project_data_dir()
        filename = os.path.join(data_dir, f"match_data_{today}.txt")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("排名,球队名称,比赛场次,胜场,平场,负场,积分\n")
            for entry in standings:
                rank = entry["position"]
                team = entry["team"]["name"]
                played = entry["playedGames"]
                won = entry["won"]
                draw = entry["draw"]
                lost = entry["lost"]
                points = entry["points"]
                f.write(f"{rank},{team},{played},{won},{draw},{lost},{points}\n")
        print(f"赛事数据已写入项目内：{filename}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("444")
        else:
            print(f"赛事API请求失败：{e.response.status_code} - {e.response.reason}")
    except Exception as e:
        print(f"赛事抓取失败：{str(e)}")


if __name__ == "__main__":
    
    
    try:
        check_api_keys()  
        crawl_news()
        crawl_match_data()
        
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    except ValueError as e:
        print(f"\n配置错误：{e}")
    except KeyboardInterrupt:
        print("\已停止")