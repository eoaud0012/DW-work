import os
# Selenium Manager의 자동 드라이버 관리를 사용하므로, 환경변수 설정은 주석 처리합니다.
# os.environ["SELENIUM_MANAGER_DISABLE"] = "1"

import pathlib
import re
from datetime import datetime as dt
from dateutil.parser import parse  # 다양한 날짜 형식 자동 파싱
from bs4 import BeautifulSoup
import requests  # HTTP 요청 (번역 함수에서 사용)
import smtplib  # 이메일 발송용 SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Selenium 관련
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
import json

# 클립보드 복사/붙여넣기에 사용 (xclip이 설치되어 있으면 Linux에서도 작동)
import pyperclip

# === API 및 이메일 관련 민감 정보 설정 (테스트용) ===
azure_endpoint = "https://apim-dwdp-openai.azure-api.net/007/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-04-01-preview"
azure_subscription_key = "d932deacbffc451e84417fac864394b9"
azure_application = "nikkei_nes_scrapping_test"
azure_compCode = "industry"
azure_userID = "eoaud0012"
azure_userNM = "daemyeong_lee"
azure_serviceType = "translate"  # 번역 서비스

email_password = "ywad kvgh etlc nafm"  # 앱 전용 비밀번호(2FA 사용 시) 권장
sender_email = "eoaud0012@gmail.com"

# Nikkei 로그인 정보
nikkei_username = "tigerxxx1494@gmail.com"
nikkei_password = "!dongwon123"

# (옵션) 환경 변수 설정 (필요 시)
os.environ["EMAIL_PASSWORD"] = email_password

# --- Monkey patch 시작 ---
_original_read_text = pathlib.Path.read_text
def patched_read_text(self, encoding="utf-8", errors="replace"):
    return _original_read_text(self, encoding=encoding, errors=errors)
pathlib.Path.read_text = patched_read_text
# --- Monkey patch 끝 ---

# --------------------------------------------------------------------
# 로그인 함수 (pyperclip 사용; Docker에서는 xclip이 설치되어 있어 작동함)
# --------------------------------------------------------------------
def login_nikkei(driver, username, password):
    driver.get("https://id.nikkei.com/account")
    time.sleep(3)  # 페이지 로딩 대기

    # 로그인 버튼 노출 확인
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//button[@data-testid="button-login"]'))
        )
    except Exception:
        print("이미 로그인되어 있거나 로그인 페이지 로딩 실패.")
        return True

    # 로그인 버튼 클릭
    try:
        driver.find_element(By.XPATH, '//button[@data-testid="button-login"]').click()
    except Exception as e:
        print("로그인 버튼 클릭 실패:", e)
        return False

    # 이메일 입력
    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-id-email"))
        )
        email_field.clear()

        # pyperclip을 사용해 복사 후 붙여넣기 (xclip이 설치되어 있으면 작동)
        pyperclip.copy(username)
        time.sleep(1)  # 너무 빠른 입력 방지
        email_field.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)
    except Exception as e:
        print("이메일 입력 필드 찾기 실패:", e)
        return False

    # 이메일 제출
    try:
        driver.find_element(By.XPATH, '//button[@data-testid="submit"]').click()
    except Exception as e:
        print("이메일 제출 버튼 클릭 실패:", e)
        return False

    # 비밀번호 입력 페이지 로딩 대기
    try:
        WebDriverWait(driver, 10).until(EC.url_contains("/login/password"))
    except Exception as e:
        print("비밀번호 페이지 전환 대기 실패:", e)
        return False

    # 비밀번호 입력
    try:
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-password-password"))
        )
        password_field.clear()

        # pyperclip을 사용해 복사 후 붙여넣기
        pyperclip.copy(password)
        time.sleep(1)
        password_field.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)
    except Exception as e:
        print("비밀번호 입력 필드 찾기 실패:", e)
        return False

    # 비밀번호 제출
    try:
        driver.find_element(By.XPATH, '//button[@data-testid="submit"]').click()
    except Exception as e:
        print("비밀번호 제출 버튼 클릭 실패:", e)
        return False

    # 로그인 성공 여부 확인
    try:
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), username)
        )
    except Exception as e:
        print("로그인 성공 확인 실패:", e)
        return False

    print("로그인 성공!")
    return True

# --------------------------------------------------------------------
# 번역 및 요약 함수: Azure OpenAI API를 이용해 텍스트를 한국어로 번역/요약
# --------------------------------------------------------------------
def translate_text(text, mode="default"):
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
    
    if mode == "title":
        user_content = f"다음 텍스트를 한국어로 번역해줘:\n\n{text}"
    elif mode == "content":
        user_content = (
            f"다음 기사 본문을 읽고, 머릿말 기호('-')를 사용해 핵심 요약만 만들어줘. "
            f"불필요한 부가 설명이나 원문은 생략하고 오직 요약만 출력해줘. "
            f"또한, 만약 한자나 일본어 전문 용어가 그대로 남는다면, 해당 용어 옆에 괄호를 사용하여 한글 번역(병기)을 추가해줘:\n\n{text}"
        )
    else:
        user_content = f"다음 텍스트를 한국어로 번역해줘:\n\n{text}"
    
    data = {
        "messages": [
            {"role": "system", "content": "너는 한국어 번역 및 요약 도우미야."},
            {"role": "user", "content": user_content}
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
# 이메일 발송 함수
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
# 기사 스크래핑 함수 (다섯 개의 섹션 탐색)
# --------------------------------------------------------------------
def scrape_articles():
    base_url = "https://www.nikkei.com"
    section_urls = [
        ("https://www.nikkei.com/economy/", "경제"),
        ("https://www.nikkei.com/economy/economy/", "경제 세부"),
        ("https://www.nikkei.com/financial/monetary-policy/", "금융 정책"),
        ("https://www.nikkei.com/economy/column/", "경제 칼럼"),
        ("https://www.nikkei.com/opinion/editorial/", "오피니언 사설")
    ]
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
    
    # 매 실행마다 고유한 사용자 데이터 디렉토리를 생성하여 오류를 방지합니다.
    import tempfile
    temp_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")

    # Selenium Manager를 활용하여 자동으로 chromedriver를 관리합니다.
    driver = webdriver.Chrome(options=chrome_options)
    
    # 로그인 수행
    if not login_nikkei(driver, nikkei_username, nikkei_password):
        driver.quit()
        return []
    
    articles = []
    seen_links = set()
    today = dt.now().date()
    global_counter = 0
    
    try:
        for url, section_label in section_urls:
            driver.get(url)
            time.sleep(3)
            main_html = driver.page_source
            soup = BeautifulSoup(main_html, "html.parser")
            article_link_tags = soup.find_all("a", href=re.compile(r"/article/"))
            
            for tag in article_link_tags:
                href = tag.get("href")
                if not href:
                    continue
                article_url = href if href.startswith("http") else base_url + href
                if article_url in seen_links:
                    continue
                seen_links.add(article_url)
                try:
                    driver.get(article_url)
                    time.sleep(3)
                    article_html = driver.page_source
                    article_soup = BeautifulSoup(article_html, "html.parser")
                    
                    title_tag = article_soup.find("h1")
                    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
                    
                    time_tag = article_soup.find("time")
                    upload_time = time_tag.get_text(strip=True) if time_tag else "시간 정보 없음"
                    
                    if upload_time == "시간 정보 없음":
                        continue
                    try:
                        article_date = parse(upload_time, fuzzy=True)
                    except Exception:
                        continue
                    if article_date.date() != today:
                        continue
                    
                    global_counter += 1
                    print(f"기사 URL: {article_url}, 업로드 시간: {upload_time} (섹션: {section_label}) ... {global_counter}")
                    
                    content_section = article_soup.find("section", attrs={"data-track-article-content": True})
                    if content_section:
                        paragraphs = content_section.find_all("p")
                        content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                    else:
                        content = "내용 없음"
                    
                    articles.append({
                        "title": title,
                        "upload_time": upload_time,
                        "content": content,
                        "url": article_url,
                        "section": section_label,
                        "order": global_counter
                    })
                except Exception as e:
                    print(f"기사 페이지 요청 실패 ({article_url}):", e)
                    continue
    finally:
        driver.quit()
    
    print(f"스크래핑 완료: 총 {len(articles)}개의 오늘 날짜 기사가 수집되었습니다.")
    return articles

# --------------------------------------------------------------------
# URL에서 신문사 이름 추출 (매핑은 필요에 따라 확장 가능)
# --------------------------------------------------------------------
def get_newspaper_name(url):
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower()
    if "nikkei" in domain:
        return "닛케이 기사"
    return "원문 기사"

# --------------------------------------------------------------------
# 메인 함수: 스크래핑, 번역, 이메일 발송 작업 수행
# --------------------------------------------------------------------
def main():
    articles = scrape_articles()
    article_count = len(articles)
    if article_count == 0:
        print("오늘자 기사가 없습니다.")
        return
    
    email_body = ""
    print(f"번역 요청 시작: 총 {article_count}개의 기사에 대해 번역 요청을 진행합니다.")
    for art in articles:
        print(f"번역 요청 중: {art['title']} (섹션: {art['section']}, {art['order']}/{article_count})")
        # 제목은 mode="title", 요약은 mode="content"로 요청
        translated_title = translate_text(art['title'], mode="title")
        translated_summary = translate_text(art['content'], mode="content")
        
        # "**번역:**" 라벨과 그 이후의 내용을 제거 (특정 패턴 정리)
        parts = re.split(r"\*\*번역:\*\*", translated_summary)
        if parts[0].strip():
            translated_summary = parts[0].strip()
        elif len(parts) > 1 and parts[1].strip():
            translated_summary = parts[1].strip()
        else:
            translated_summary = "요약 내용 없음"
        
        newspaper_name = get_newspaper_name(art['url'])
        
        final_article_text = (
            f"**제목:** {art['title']} (전체 기사 {article_count}개 중 {art['order']}번 째, 섹션: {art['section']})\n"
            f"**제목:** {translated_title}\n\n"
            f"**업로드 시간:** {art['upload_time']}\n"
            f"**원문 URL:** [{newspaper_name}]({art['url']})\n\n"
            f"---\n\n"
            f"**요약:**\n\n"
            f"{translated_summary}\n"
        )
        email_body += final_article_text + ("\n" + "=" * 50 + "\n\n")
    
    subject = f"[{dt.now().strftime('%y/%m/%d')}] Nikkei 뉴스 기사 번역 및 요약 ({article_count}개)"
    recipient = "eoaud0012@dongwon.com"
    send_email(subject, email_body, recipient)
    print(f"이메일 발송 완료: 총 {article_count}개의 기사 발송되었습니다.")

if __name__ == "__main__":
    main()