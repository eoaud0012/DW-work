import os
import pathlib
import re
import datetime
from datetime import datetime as dt
from dateutil.parser import parse  # 다양한 날짜 형식 자동 파싱
from bs4 import BeautifulSoup
import requests  # HTTP 요청 (번역 함수에서 사용)
import smtplib  # 이메일 발송용 SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver  # Selenium 웹드라이버
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# === API 및 이메일 관련 민감 정보 설정 (테스트용) ===
azure_endpoint = "https://apim-dwdp-openai.azure-api.net/007/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-04-01-preview"
azure_subscription_key = "d932deacbffc451e84417fac864394b9"
azure_application = "nikkei_nes_scrapping_test"
azure_compCode = "industry"
azure_userID = "eoaud0012"
azure_userNM = "daemyeong_lee"
azure_serviceType = "translate"  # 예: 번역 서비스인 경우

email_password = "ywad kvgh etlc nafm"  # 앱 전용 비밀번호(2FA 사용 시) 권장
sender_email = "eoaud0012@gmail.com"

# Nikkei 로그인 정보
nikkei_username = "tigerxxx1494@gmail.com"
nikkei_password = "!dongwon123"

# (옵션) 환경 변수 설정 (필요 시)
os.environ["EMAIL_PASSWORD"] = email_password

# --- Monkey patch 시작 ---
# 파일 읽기 시 인코딩 오류 방지를 위해 pathlib.Path.read_text를 패치합니다.
_original_read_text = pathlib.Path.read_text
def patched_read_text(self, encoding="utf-8", errors="replace"):
    return _original_read_text(self, encoding=encoding, errors=errors)
pathlib.Path.read_text = patched_read_text
# --- Monkey patch 끝 ---

# --------------------------------------------------------------------
# 로그인 함수: Nikkei 유료 계정으로 로그인
# --------------------------------------------------------------------
def login_nikkei(driver, username, password):
    # 1. https://id.nikkei.com/account 페이지로 접속
    driver.get("https://id.nikkei.com/account")
    
    try:
        # 2. "로그인" 버튼 대기 및 클릭 (data-testid="button-login")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="button-login"]'))
        )
        login_button.click()
    except Exception as e:
        print("로그인 버튼 클릭 실패:", e)
        return False

    try:
        # 3. 이메일 입력 페이지가 로드될 때까지 대기
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-id-email"))
        )
        email_field.clear()
        email_field.send_keys(username)
    except Exception as e:
        print("이메일 입력 필드 찾기 실패:", e)
        return False

    try:
        # 4. 이메일 제출 버튼 클릭 (data-testid="submit")
        email_submit = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="submit"]'))
        )
        email_submit.click()
    except Exception as e:
        print("이메일 제출 버튼 클릭 실패:", e)
        return False

    try:
        # 5. 비밀번호 입력 페이지로 전환될 때까지 대기
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login/password")
        )
    except Exception as e:
        print("비밀번호 페이지 전환 대기 실패:", e)
        return False

    try:
        # 6. 비밀번호 입력 필드 대기 (ID: "login-password-password")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-password-password"))
        )
        password_field.clear()
        password_field.send_keys(password)
    except Exception as e:
        print("비밀번호 입력 필드 찾기 실패:", e)
        return False

    try:
        # 7. 비밀번호 제출 버튼 클릭 (data-testid="submit")
        password_submit = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="submit"]'))
        )
        password_submit.click()
    except Exception as e:
        print("비밀번호 제출 버튼 클릭 실패:", e)
        return False

    try:
        # 8. 로그인 성공 확인: 예를 들어, body 태그 내에 username이 있는지 확인
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), username)
        )
    except Exception as e:
        print("로그인 성공 확인 실패:", e)
        return False

    print("로그인 성공!")
    return True

# --------------------------------------------------------------------
# 번역 함수: Azure OpenAI API를 이용해 텍스트를 한국어로 번역
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
            {"role": "user", "content": f"다음 텍스트를 한국어로 번역해주고, 회사의 임원이 보시는 거라, 기사의 핵심 내용을 머릿말 기호를 사용하여 깔끔하게 요약해줘.:\n\n{text}"}
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
# 기사 스크래핑 함수 (로그인 포함)
# --------------------------------------------------------------------
def scrape_articles():
    base_url = "https://www.nikkei.com"
    section_url = f"{base_url}/economy/"
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                                "AppleWebKit/537.36 (KHTML, like Gecko) " +
                                "Chrome/114.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    
    # 먼저 Nikkei 로그인 수행
    if not login_nikkei(driver, nikkei_username, nikkei_password):
        driver.quit()
        return []
    
    articles = []
    seen_links = set()
    today = dt.now().date()
    
    try:
        # 로그인 후 경제 섹션 페이지로 이동
        driver.get(base_url)
        time.sleep(3)
        driver.get(section_url)
        time.sleep(3)  # 페이지 로드 대기 (필요 시 조정)
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
                time.sleep(3)  # 페이지 로드 대기
                article_html = driver.page_source
                article_soup = BeautifulSoup(article_html, "html.parser")
                
                title_tag = article_soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
                
                time_tag = article_soup.find("time")
                upload_time = time_tag.get_text(strip=True) if time_tag else "시간 정보 없음"
                
                print(f"기사 URL: {article_url}, 업로드 시간: {upload_time}")
                
                if upload_time == "시간 정보 없음":
                    continue
                
                try:
                    article_date = parse(upload_time, fuzzy=True)
                except Exception as e:
                    print(f"날짜 파싱 오류 for article URL: {article_url}: {e}")
                    continue
                
                if article_date.date() != today:
                    continue
                
                # 기사 본문 추출
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
                    "url": article_url
                })
            except Exception as e:
                print(f"기사 페이지 요청 실패 ({article_url}):", e)
                continue
    finally:
        driver.quit()
    
    print(f"스크래핑 완료: 총 {len(articles)}개의 오늘 날짜 기사가 수집되었습니다.")
    return articles

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
    for idx, art in enumerate(articles, start=1):
        text_to_translate = (
            f"제목: {art['title']} (전체 기사 {article_count}개 중 {idx}번 째)\n"
            f"업로드 시간: {art['upload_time']}\n"
            f"원문 URL: {art['url']}\n\n"
            f"내용:\n{art['content']}"
        )
        print(f"번역 요청 중: {art['title']} ({idx}/{article_count})")
        translated_text = translate_text(text_to_translate)
        email_body += translated_text + "\n" + ("=" * 50) + "\n\n"
    
    subject = f"[{dt.now().strftime('%y/%m/%d')}] 외국 뉴스 기사 번역 및 요약 ({article_count}개)"
    recipient = "eoaud0012@dongwon.com"
    send_email(subject, email_body, recipient)
    print(f"이메일 발송 완료: 총 {article_count}개의 기사 발송되었습니다.")

if __name__ == "__main__":
    main()
