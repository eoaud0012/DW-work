import os
import pathlib
import re
import subprocess
from datetime import datetime as dt
from dateutil.parser import parse  # 다양한 날짜 형식 자동 파싱
from bs4 import BeautifulSoup
import requests  # HTTP 요청 (번역 함수에서 사용)
import smtplib  # 이메일 발송용 SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import json
import random  # 자연스러운 타이핑에 사용할 랜덤 딜레이

# Selenium 관련
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# 클립보드 복사/붙여넣기에 사용 (기존 사용하던 라이브러리)
import pyperclip

# Selenium-stealth 라이브러리 (봇 탐지 회피용)
from selenium_stealth import stealth

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

def human_typing(element, text):
    """자연스러운 타이핑 시뮬레이션: 한 글자씩 입력하며 랜덤 딜레이 추가"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def kill_chrome():
    """
    크롬이 실행 중이라면 모두 종료합니다.
    Windows에서는 taskkill 명령어를 사용합니다.
    """
    try:
        subprocess.call("taskkill /F /IM chrome.exe", shell=True)
        print("기존의 모든 Chrome 프로세스 종료 완료")
    except Exception as e:
        print("Chrome 종료 중 오류 발생:", e)

def start_chrome_debug():
    """
    cmd 창에서 아래 명령어와 동일하게 remote debugging 모드로 크롬을 실행합니다.
    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_debug_profile"
    """
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\chrome_debug_profile"
    cmd = [chrome_path, "--remote-debugging-port=9222", f"--user-data-dir={user_data_dir}"]
    process = subprocess.Popen(cmd)
    # 크롬이 완전히 실행될 때까지 대기 (환경에 따라 조정)
    time.sleep(5)
    return process

def create_driver_debug():
    """
    remote debugging 모드로 실행된 크롬에 연결합니다.
    """
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=chrome_options)
    
    # Selenium-stealth 적용 (봇 탐지 회피)
    stealth(driver,
            languages=["ko-KR", "en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
           )
    return driver

# --------------------------------------------------------------------
# 로그인 함수 (기존 로그인 절차 유지)
# --------------------------------------------------------------------
def login_nikkei(driver, username):
    # www.nikkei.com으로 접속
    driver.get("https://www.nikkei.com")
    time.sleep(3)  # 페이지 로딩 대기

    # 로그인 링크 클릭
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'k-header-account-nav__item-login')]")
            )
        )
        login_button.click()
    except Exception as e:
        print("로그인 링크 클릭 실패:", e)
        return False

    # 아이디 입력 (비밀번호는 자동완성되어 있다고 가정)
    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-id-email"))
        )
        email_field.clear()
        pyperclip.copy(username)  # 아이디 복사
        time.sleep(1)
        email_field.send_keys(Keys.CONTROL, 'v')  # 붙여넣기
        time.sleep(2)
    except Exception as e:
        print("이메일 입력 필드 찾기 실패:", e)
        return False

    # 최종 로그인(제출) 버튼 클릭 (JavaScript로 클릭)
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='submit']"))
        )
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(3)  # 클릭 후 처리 대기
    except Exception as e:
        print("로그인 제출 버튼 클릭 실패:", e)
        return False
    
        # 두 번째 최종 로그인(제출) 버튼 클릭 (JavaScript로 클릭)
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='submit']"))
        )
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(3)  # 클릭 후 처리 대기
    except Exception as e:
        print("로그인 제출 버튼 클릭 실패:", e)
        return False

    # 로그인 성공 확인: URL에 "/login"이 남아있지 않은지 확인
    try:
        WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
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
    
    # 크롬 디버그 모드로 실행된 인스턴스에 연결
    driver = create_driver_debug()
    
    if not login_nikkei(driver, nikkei_username):
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
# 메인 함수: 크롬 디버그 모드 실행, 스크래핑, 번역, 이메일 발송 작업 수행
# --------------------------------------------------------------------
def main():
    # 먼저 기존에 실행 중인 Chrome 프로세스 모두 종료
    kill_chrome()
    
    # remote debugging 모드로 크롬 실행
    chrome_process = start_chrome_debug()
    
    try:
        articles = scrape_articles()
        article_count = len(articles)
        if article_count == 0:
            print("오늘자 기사가 없습니다.")
            return
        
        email_body = ""
        print(f"번역 요청 시작: 총 {article_count}개의 기사에 대해 번역 요청을 진행합니다.")
        for art in articles:
            print(f"번역 요청 중: {art['title']} (섹션: {art['section']}, {art['order']}/{article_count})")
            translated_title = translate_text(art['title'], mode="title")
            translated_summary = translate_text(art['content'], mode="content")
            
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
    finally:
        # 작업 종료 후 remote debugging 모드로 실행한 크롬 프로세스 종료
        chrome_process.terminate()

if __name__ == "__main__":
    main()
