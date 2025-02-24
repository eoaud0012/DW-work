import os
import json
import time
import smtplib
from datetime import datetime as dt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse
from newspaper import Article

# === Azure OpenAI API 및 이메일 관련 민감 정보 설정 ===
azure_endpoint = "https://apim-dwdp-openai.azure-api.net/007/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-04-01-preview"
azure_subscription_key = "d932deacbffc451e84417fac864394b9"
azure_application = "nikkei_nes_scrapping_test"
azure_compCode = "industry"
azure_userID = "eoaud0012"
azure_userNM = "daemyeong_lee"
azure_serviceType = "translate"  # 번역 서비스

email_password = "ywad kvgh etlc nafm"  # 앱 전용 비밀번호(또는 SMTP 비밀번호)
sender_email = "eoaud0012@gmail.com"
os.environ["EMAIL_PASSWORD"] = email_password

# --------------------------------------------------------------------
# 번역 함수 (Azure OpenAI API)
# --------------------------------------------------------------------
def translate_text(text):
    """
    번역 API에 다음과 같은 payload를 전달합니다.
    """
    endpoint = azure_endpoint
    headers = {
        "Ocp-Apim-Subscription-Key": azure_subscription_key,
        "application": azure_application,
        "compCode": azure_compCode,
        "userID": azure_userID,
        "userNM": azure_userNM,
        "serviceType": azure_serviceType,
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "messages": [
            {"role": "system", "content": "너는 한국어 번역 및 요약 도우미야."},
            {
                "role": "user",
                "content": (
                    f"다음 텍스트를 한국어로 번역해주고, 회사의 임원이 보시는 거라, "
                    f"기사의 핵심 내용을 머릿말 기호를 사용하여 깔끔하게 요약해줘.:\n\n{text}"
                )
            }
        ],
        "temperature": 0.3
    }
    try:
        data_str = json.dumps(data, ensure_ascii=False).encode("utf-8")
        response = requests.post(endpoint, headers=headers, data=data_str)
        response.raise_for_status()
        response.encoding = "utf-8"
        result = response.json()
        translated_text = result["choices"][0]["message"]["content"].strip()
        return translated_text
    except Exception as e:
        print("번역 중 오류 발생:", e)
        return text

# --------------------------------------------------------------------
# 이메일 발송 함수 (SMTP)
# --------------------------------------------------------------------
def send_email(subject, body, recipient):
    sender = sender_email
    email_pw = os.getenv("EMAIL_PASSWORD")
    if email_pw is None:
        print("EMAIL_PASSWORD 환경변수가 설정되어 있지 않습니다.")
        return
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender, email_pw)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
    except Exception as e:
        print("이메일 발송 중 오류 발생:", e)

# --------------------------------------------------------------------
# newspaper3k를 사용하여 URL로부터 기사 본문과 제목 추출
# --------------------------------------------------------------------
def get_article_text_with_newspaper(url):
    try:
        article = Article(url, language="en")
        article.download()
        article.parse()
        text = article.text if article.text.strip() else "본문 없음"
        title = article.title if article.title.strip() else "제목 없음"
        return title, text
    except Exception as e:
        print(f"newspaper3k 추출 중 오류 ({url}):", e)
        return "제목 없음", "본문 없음"

# --------------------------------------------------------------------
# BeautifulSoup을 사용하여 페이지 HTML에서 기사 컨테이너 파싱
# --------------------------------------------------------------------
def get_articles_from_page(html):
    articles = []
    soup = BeautifulSoup(html, "html.parser")
    # 기사 컨테이너가 "SoaBEf" 클래스인 div라고 가정
    containers = soup.find_all("div", class_="SoaBEf")
    for container in containers:
        a_tag = container.find("a", class_="WlydOe")
        url = a_tag.get("href") if a_tag else None

        title_tag = container.find("div", class_="n0jPhd")
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

        snippet_tag = container.find("div", class_="GI74Re")
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else "요약 없음"

        date_tag = container.find("div", class_="OSrXXb")
        date = date_tag.get_text(strip=True) if date_tag else "날짜 없음"

        if url:
            articles.append({
                "url": url,
                "title": title,
                "snippet": snippet,
                "date": date
            })
    return articles

# --------------------------------------------------------------------
# Selenium으로 Google News 검색 결과 페이지에서 스크롤 후 기사 정보 수집
# --------------------------------------------------------------------
def get_articles_from_google_news(driver, scrolls=3):
    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    html = driver.page_source
    articles = get_articles_from_page(html)
    return articles

# --------------------------------------------------------------------
# 메인 함수: 기사 수집 → 번역(요약) → 이메일 발송
# --------------------------------------------------------------------
def main():
    keywords = ["Beer Market", "Soju Market"]
    GOOGLE_NEWS_URL = "https://www.google.com/search?q={query}&tbm=nws&tbs=qdr:m&hl=en&gl=us"

    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless")  # 디버깅 시 주석 해제 가능
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)

    print("로그인 성공!")

    excluded_domains = [
        "chosun.com", "koreatimes.co.kr", "mk.co.kr",
        "koreaherald.com", "koreajoongangdaily.joins.com",
        "businesskorea.co.kr"
    ]
    collected_articles = []
    total_articles_found = 0
    excluded_count = 0

    for keyword in keywords:
        try:
            driver.get(GOOGLE_NEWS_URL.format(query=keyword))
        except TimeoutException:
            continue
        time.sleep(2)
        articles = get_articles_from_google_news(driver, scrolls=5)
        total_articles_found += len(articles)
        for article in articles:
            domain = urlparse(article["url"]).netloc.lower()
            if any(excl in domain for excl in excluded_domains):
                excluded_count += 1
                continue
            collected_articles.append(article)
    driver.quit()

    print(f"전체 검색 기사: {total_articles_found}개, 도메인 제외된 기사: {excluded_count}개")

    if not collected_articles:
        print("수집된 기사가 없습니다.")
        return

    total_articles = len(collected_articles)
    for idx, article in enumerate(collected_articles, start=1):
        url = article["url"]
        date = article.get("date", "업로드 시간 없음")
        print(f"기사 URL: {url}, 업로드 시간: {date} ... {idx}")

    print(f"스크래핑 완료: 총 {total_articles}개의 오늘 날짜 기사가 수집되었습니다.")
    print(f"번역(요약) 요청 시작: 총 {total_articles}개의 기사에 대해 번역(요약) 요청을 진행합니다.")

    email_body = ""
    for i, article in enumerate(collected_articles):
        url = article["url"]
        # Newspaper3k로 기사 제목과 본문 추출
        np_title, article_text = get_article_text_with_newspaper(url)
        if np_title == "제목 없음":
            np_title = article["title"]
        if article_text == "본문 없음":
            article_text = article["snippet"]

        print(f"번역(요약) 요청 중: {np_title} ({i+1}/{total_articles})")
        
        # 번역 API에는 핵심 내용만 전달 (순서, 링크, 업로드 시간 등은 제외)
        translated_title = translate_text(np_title)
        translated_summary = translate_text(article_text)
        
        # 최종 메일 본문 구성 (원문 제목, 번역된 제목, 업로드 시간, 원문 URL, 요약)
        email_body += f"**제목:** {np_title} (전체 기사 {total_articles}개 중 {i+1}번 째)\n"
        email_body += f"**제목:** {translated_title}\n\n"
        email_body += f"**업로드 시간:** {article['date']}\n"
        email_body += f"**원문 URL:** [원문 기사]({url})\n\n"
        email_body += f"**요약:**\n{translated_summary}\n\n"
        email_body += "=" * 50 + "\n\n"

    subject = f"[{dt.now().strftime('%y/%m/%d')}] 외국 뉴스 기사 번역 및 요약 ({total_articles}개)"
    recipient = "eoaud0012@dongwon.com"
    send_email(subject, email_body, recipient)

    print("이메일 발송 성공!")
    print(f"이메일 발송 완료: 총 {total_articles}개의 기사 발송되었습니다.")

if __name__ == "__main__":
    main()
