import os
import json
import time
import smtplib
from datetime import datetime as dt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
        print("이메일 발송 성공!")
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
# Selenium으로 Google News 검색 결과에서 모든 기사 URL 수집 (여러 CSS 선택자 사용)
# --------------------------------------------------------------------
def get_all_urls_from_google_news(driver, scrolls=3):
    urls = set()
    # 여러 선택자를 시도하여 다양한 뉴스 카드 컨테이너를 커버함
    selectors = ["div.MjjYud", "div.dbsr", "div.g", "a.WlydOe"]
    for _ in range(scrolls):
        for sel in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for element in elements:
                    try:
                        link_element = element.find_element(By.TAG_NAME, "a")
                        url = link_element.get_attribute("href")
                        if url:
                            urls.add(url)
                    except NoSuchElementException:
                        continue
            except Exception as e:
                print(f"Selector '{sel}' 검색 오류:", e)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    return list(urls)

# --------------------------------------------------------------------
# 메인 함수: URL 수집, 기사 처리, 번역/요약, 이메일 발송
# --------------------------------------------------------------------
def main():
    keywords = ["Beer Market", "Soju Market"]
    # 지난 1개월(30일) 이내 기사 검색 + 영어/미국 기준
    GOOGLE_NEWS_URL = "https://www.google.com/search?q={query}&tbm=nws&tbs=qdr:m&hl=en&gl=us"

    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 디버깅 시에는 헤드리스 모드 주석 처리
    # chrome_options.add_argument("--headless")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)

    excluded_domains = ["chosun.com", "koreatimes.co.kr", "mk.co.kr"]
    collected_urls = []

    for keyword in keywords:
        print(f"🔍 '{keyword}' 검색 중...")
        try:
            driver.get(GOOGLE_NEWS_URL.format(query=keyword))
        except TimeoutException:
            print(f"'{keyword}' 검색 페이지 로딩 타임아웃 발생. 건너뜁니다.")
            continue
        time.sleep(2)
        urls = get_all_urls_from_google_news(driver, scrolls=5)
        print(f"'{keyword}'에서 {len(urls)}개의 URL 수집됨.")
        if not urls:
            print(f"'{keyword}' 관련 기사가 없습니다.")
            continue
        for url in urls:
            domain = urlparse(url).netloc.lower()
            if any(excl in domain for excl in excluded_domains):
                print(f"{domain} 기사이므로 제외합니다.")
                continue
            collected_urls.append(url)
    driver.quit()

    if not collected_urls:
        print("수집된 기사가 없습니다.")
        return

    print(f"총 {len(collected_urls)}개의 URL 처리 예정.")

    email_body = ""
    for url in collected_urls:
        print(f"Processing article: {url}")
        title, article_text = get_article_text_with_newspaper(url)
        translated_text = translate_text(
            f"제목: {title}\n링크: {url}\n\n내용:\n{article_text}"
        )
        email_body += f"제목: {title}\n링크: {url}\n\n"
        email_body += f"----- 번역 및 요약 -----\n{translated_text}\n"
        email_body += "=" * 50 + "\n\n"
        print(f"✅ 기사 처리 완료: {title}")

    subject = f"[{dt.now().strftime('%y/%m/%d')}] 외국 뉴스 기사 번역 및 요약"
    recipient = "eoaud0012@dongwon.com"
    send_email(subject, email_body, recipient)
    print("\n최종 이메일 본문:\n", email_body)

if __name__ == "__main__":
    main()
