import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Windows 시스템에서 맑은 고딕 폰트 경로 지정
font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  #맑은고딕

# 폰트 설정
plt.rc('font', family=fm.FontProperties(fname=font_path).get_name())


import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# 네이버 뉴스 검색 결과에서 기사 제목, 요약, URL을 크롤링
def crawl_news(search_url):
    res = requests.get(search_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    news_list = []
    for link in soup.select('.news_tit'):
        title = link.get('title')
        url = link.get('href')
        summary = soup.select_one('.api_txt_lines.dsc_txt_wrap').text
        news_list.append([title, summary, url])

    return news_list

# 검색 URL
search_url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=%EB%AC%BC%EB%A5%98%EC%8B%9C%EC%9E%A5'

# 뉴스 크롤링
news_list = crawl_news(search_url)

# 결과를 데이터프레임으로 변환
df = pd.DataFrame(news_list, columns=['Title', 'Summary', 'URL'])

# 오늘 날짜를 가져와서 파일명 생성
today = datetime.today().strftime('%y%m%d')
filename = f'news_crawling_{today}.xlsx'

# 결과를 엑셀 파일로 저장
df.to_excel(f'C:\\Users\\DW-PC\\Desktop\\GPT\\뉴스크롤링\\{filename}', index=False)
