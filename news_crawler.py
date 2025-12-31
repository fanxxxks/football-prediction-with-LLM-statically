import requests
import csv
from datetime import datetime

API_KEY = "63bf0eb9f22b4a1eb7f6899fc3d48461"  
KEYWORD = "football"       
LANGUAGE = "en"               
PAGE_SIZE = 10                

url = f"https://newsapi.org/v2/everything?q={KEYWORD}&language={LANGUAGE}&pageSize={PAGE_SIZE}&apiKey={API_KEY}"
response = requests.get(url) 
news_data = response.json()   

if response.status_code == 200:
    print("新闻抓取成功！")
else:
    print(f"抓取失败，错误码：{response.status_code}")
    print("错误信息：", news_data.get("message", "未知错误"))
    exit() 


filename = f"data/football_news_{datetime.now().strftime('%Y%m%d')}.csv"  # 存到data文件夹

with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["新闻标题", "发布时间", "新闻链接", "内容摘要"])

    for article in news_data["articles"]:
        title = article.get("title", "无标题")
        published_at = article.get("publishedAt", "无时间")
        url = article.get("url", "无链接")
        description = article.get("description", "无摘要")
        writer.writerow([title, published_at, url, description])

print(f"新闻已保存到：{filename}")