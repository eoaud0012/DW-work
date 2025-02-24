import requests
from bs4 import BeautifulSoup
import urllib
import feedparser

# 블로그 RSS 피드 URL
rss_feed_url = "https://rss.blog.naver.com/birdiebirgi.xml"

# RSS 피드 파싱
feed = feedparser.parse(rss_feed_url)

# 최신 게시물 링크 가져오기
latest_post_link = feed.entries[0].link

# 페이지 가져오기
response = requests.get(latest_post_link)
html = response.text

# BeautifulSoup을 사용하여 HTML 파싱
soup = BeautifulSoup(html, "html.parser")

# 이미지 태그 찾기
image_tags = soup.find_all("img")

# 이미지 다운로드
for idx, image_tag in enumerate(image_tags):
    # 이미지 URL
    image_url = image_tag.get("src")
    # 이미지 다운로드
    urllib.request.urlretrieve(image_url, f"image_{idx+1}.jpg")
    print(f"Image {idx+1} downloaded successfully.")