import os
import pathlib
import re
import datetime
from datetime import datetime as dt
from dateutil.parser import parse  # 다양한 날짜 형식을 파싱하기 위해 사용
from bs4 import BeautifulSoup
import requests  # HTTP 요청용
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

# === API 키 및 기타 민감 정보 직접 설정 (테스트용) ===
# 아래 값을 실제 환경에 맞게 수정하세요.
openai_api_key = "your_openai_api_key_here"  # (이 코드는 사용하지 않습니다. Azure 엔드포인트를 사용합니다.)
# Azure OpenAI 엔드포인트와 헤더 정보:
azure_endpoint = "https://apim-dwdp-openai.azure-api.net/007/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-04-01-preview"
azure_subscription_key = "d932deacbffc451e84417fac864394b9"
azure_application = "nikkei_nes_scrapping_test"
azure_compCode = "industry"
azure_userID = "eoaud0012"
azure_userNM = "daemyeong_lee"
azure_serviceType = "translate"  # 예: 번역 서비스인 경우

# 이메일 비밀번호 및 발신자 이메일
email_password = "ywad kvgh etlc nafm"  # 앱 전용 비밀번호(2FA 사용 시) 권장
sender_email = "eoaud0012@gmail.com"

# 환경 변수 설정 (선택 사항)
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["EMAIL_PASSWORD"] = email_password

# --- Monkey patch 시작 ---
# pathlib.Path.read_text() 호출 시, errors="replace" 옵션을 사용하여
# 잘못된 바이트가 있으면 대체 문자로 처리하도록 수정합니다.
_original_read_text = pathlib.Path.read_text
def patched_read_text(self, encoding="utf-8", errors="replace"):
    return _original_read_text(self, encoding=encoding, errors=errors)
pathlib.Path.read_text = patched_read_text
# --- Monkey patch 끝 ---

# --------------------------------------------------------------------
# 번역 함수: Azure OpenAI 엔드포인트를 이용한 번역 요청
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
        "Content-Type": "application/json"
    }
    # OpenAI Chat API와 유사한 요청 본문 구성
    data = {
        "messages": [
            {"role": "system", "content": "너는 한국어 번역 도우미야."},
            {"role": "user", "content": f"다음 텍스트를 한국어로 번역해줘:\n\n{text}"}
        ],
        "temperature": 0.3
    }
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        # 강제로 UTF-8 인코딩 지정
        response.encoding = "utf-8"
        result = response.json()
        translated_text = result["choices"][0]["message"]["content"].strip()
        return translated_text
    except Exception as e:
        print("번역 중 오류 발생:", e)
        return text  # 오류 발생 시 원본 텍스트 반환

# --------------------------------------------------------------------
# 이메일 발송 함수
# --------------------------------------------------------------------
def send_email(subject, body, recipient):
    sender = sender_email  # 위에서 설정한 발신자 이메일 사용
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
# Nikkei 경제 섹션의 오늘자 기사를 Selenium을 이용해 스크래핑하는 함수
# --------------------------------------------------------------------
def scrape_articles():
    base_url = "https://www.nikkei.com"
    section_url = f"{base_url}/economy/"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/114.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    
    articles = []
    seen_links = set()
    today = dt.now().date()
    
    try:
        driver.get(section_url)
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
                article_html = driver.page_source
                article_soup = BeautifulSoup(article_html, "html.parser")
                
                title_tag = article_soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
                
                time_tag = article_soup.find("time")
                upload_time = time_tag.get_text(strip=True) if time_tag else "시간 정보 없음"
                
                print(f"★기사 URL: {article_url}, ★업로드 시간: {upload_time}")
                
                if upload_time == "시간 정보 없음":
                    continue
                
                try:
                    article_date = parse(upload_time, fuzzy=True)
                except Exception as e:
                    print(f"날짜 파싱 오류 for article URL: {article_url}: {e}")
                    continue
                
                # if article_date.date() != today:
                #     continue
                
                # 여기서 기사 본문 추출 방식을 수정합니다.
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
    
    return articles


# --------------------------------------------------------------------
# 메인 함수: 스크래핑, 번역, 이메일 발송
# --------------------------------------------------------------------
def main():
    articles = scrape_articles()
    
    if not articles:
        print("오늘자 기사가 없습니다.")
        return
    
    email_body = ""
    
    for art in articles:
        text_to_translate = (
            f"제목: {art['title']}\n"
            f"업로드 시간: {art['upload_time']}\n"
            f"원문 URL: {art['url']}\n\n"
            f"내용:\n{art['content']}"
        )
        print(f"번역 요청 중: {art['title']}")
        translated_text = translate_text(text_to_translate)
        email_body += translated_text + "\n" + ("=" * 50) + "\n\n"
    
    subject = "오늘자 Nikkei 기사 번역본"
    recipient = "eoaud0012@dongwon.com"
    send_email(subject, email_body, recipient)

if __name__ == "__main__":
    main()
