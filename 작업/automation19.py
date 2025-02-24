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
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse

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

# (옵션) 환경 변수 설정
os.environ["EMAIL_PASSWORD"] = email_password

# --------------------------------------------------------------------
# 번역 함수: Azure OpenAI API를 이용해 텍스트를 한국어로 번역 및 요약
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
# 이메일 발송 함수 (SMTP 사용)
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
# 전체 기사 본문 추출 함수: 신문사마다 다른 HTML 구조를 고려
# --------------------------------------------------------------------
def get_full_article_text(driver):
    """
    본문 후보 CSS 선택자를 순차적으로 시도하며,
    일단 텍스트가 추출되면 반환.
    """
    candidate_selectors = [
        "article p",
        "div.article-content p",
        "div#articleBody p",
        "div.story-body p",
        "div#main-content p",
        "div#news_content p",
    ]

    max_text = ""
    for selector in candidate_selectors:
        paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
        text_list = [p.text.strip() for p in paragraphs if p.text.strip()]
        joined_text = "\n".join(text_list)
        if len(joined_text) > len(max_text):
            max_text = joined_text

    if not max_text.strip():
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        text_list = [p.text.strip() for p in paragraphs if p.text.strip()]
        max_text = "\n".join(text_list) if text_list else "본문 없음"

    return max_text if max_text else "본문 없음"


# --------------------------------------------------------------------
# 메인 크롤링 및 번역/요약, 이메일 발송 함수
# --------------------------------------------------------------------
def main():
    keywords = ["Beer Market", "Soju Market"]
    # tbs=qdr:m → 지난 1개월(30일) 이내 기사
    GOOGLE_NEWS_URL = "https://www.google.com/search?q={query}&tbm=nws&tbs=qdr:m"

    # 크롬 옵션 설정 (이미지 비활성화, 헤드리스 등)
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 필요 시 헤드리스 모드 활성화
    # chrome_options.add_argument("--headless")

    # 이미지 로딩 비활성화 (로딩 시간 단축)
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 페이지 로딩 최대 시간 설정 (예: 30초)
    driver.set_page_load_timeout(30)

    # 제외할 도메인 목록 (한국 신문사)
    excluded_domains = ["chosun.com", "koreatimes.co.kr", "mk.co.kr"]

    email_body = ""

    for keyword in keywords:
        print(f"🔍 '{keyword}' 검색 중...")
        try:
            driver.get(GOOGLE_NEWS_URL.format(query=keyword))
        except TimeoutException:
            print(f"'{keyword}' 검색 페이지 로딩 타임아웃 발생. 건너뜁니다.")
            continue

        time.sleep(2)

        # Google 뉴스 기사 목록
        articles = driver.find_elements(By.CSS_SELECTOR, "div.MjjYud")
        if not articles:
            print(f"📭 '{keyword}' 관련 최근 기사가 없습니다.")
            continue

        # 상위 3개 기사 처리
        for article in articles[:3]:
            try:
                # a 태그(링크) 추출
                link_element = article.find_element(By.TAG_NAME, "a")
                link = link_element.get_attribute("href")

                # 도메인 분석
                domain = urlparse(link).netloc.lower()
                # 한국 신문사 도메인 제외
                if any(excl in domain for excl in excluded_domains):
                    print(f"{domain} 기사이므로 제외합니다.")
                    continue

                # h3 태그가 없으면 a 태그 텍스트 사용
                try:
                    title_element = article.find_element(By.CSS_SELECTOR, "h3")
                    search_title = title_element.text.strip()
                except:
                    search_title = link_element.text.strip()
                    if not search_title:
                        print("기사 제목을 찾을 수 없어 건너뜁니다.")
                        continue

                print(f"➡ 기사 페이지 접속: {search_title}")
                try:
                    driver.get(link)
                except TimeoutException:
                    print("기사 페이지 로딩 타임아웃 발생. 건너뜁니다.")
                    continue

                time.sleep(3)

                # 기사 페이지에서 실제 제목 추출 시도
                try:
                    article_title = driver.find_element(By.CSS_SELECTOR, "div.stitle_con > span").text.strip()
                    if not article_title:
                        article_title = search_title
                except:
                    article_title = search_title

                # 기사 본문 추출
                full_content = get_full_article_text(driver)

                # 번역 및 요약
                translated_text = translate_text(
                    f"제목: {article_title}\n링크: {link}\n\n내용:\n{full_content}"
                )

                # 이메일 본문 구성
                email_body += f"제목: {article_title}\n링크: {link}\n\n"
                email_body += f"----- 번역 및 요약 -----\n{translated_text}\n"
                email_body += "=" * 50 + "\n\n"

                print(f"✅ 기사 처리 완료: {article_title}")

                # 검색 결과 페이지로 복귀
                driver.back()
                time.sleep(2)

            except Exception as e:
                print(f"❌ 기사 크롤링 중 오류 발생: {e}")

    driver.quit()

    if not email_body:
        print("수집된 기사가 없습니다.")
        return

    subject = f"[{dt.now().strftime('%y/%m/%d')}] 외국 뉴스 기사 번역 및 요약"
    recipient = "eoaud0012@dongwon.com"
    send_email(subject, email_body, recipient)

    print("\n최종 이메일 본문:\n", email_body)

if __name__ == "__main__":
    main()
