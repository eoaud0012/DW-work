# 뉴욕 타임스 유료 계정 없어서 중단

import os
import json
import time
import smtplib
import requests
import datetime
from datetime import datetime as dt, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")  # 창 최대화 옵션 추가
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")  # 헤드리스 모드 추가
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=options)
    return driver

def handle_terms_popup(driver):
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
        
        if driver.find_elements(By.XPATH, "//button[contains(., 'Continue')]"):
            terms_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]")
            ))
            terms_button.click()
            time.sleep(2)
            driver.switch_to.default_content()
            print("Terms popup closed successfully (iframe).")
            return
        driver.switch_to.default_content()
    except Exception as e:
        print("No terms popup in iframe, checking for div popup...", e)
        driver.switch_to.default_content()
    
    try:
        if driver.find_elements(By.ID, "complianceOverlay"):
            terms_popup = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "complianceOverlay"))
            )
            terms_button = terms_popup.find_element(By.XPATH, ".//button[contains(., 'Continue')]")
            terms_button.click()
            time.sleep(2)
            print("Terms popup closed successfully (div).")
            return
    except Exception as e:
        print("No terms popup or unable to close popup:", e)

def search_nytimes(driver, keyword):
    print(f"'{keyword}' 키워드를 검색합니다.")
    driver.get("https://www.nytimes.com/international/")
    handle_terms_popup(driver)
    
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='search-button']"))
    ).click()
    
    search_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='search-input']"))
    )
    search_input.clear()
    search_input.send_keys(keyword)
    search_input.submit()
    time.sleep(3)
    
    return driver.page_source

def scrape_articles(html, keyword):
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    today = dt.now().date()
    month_ago = today - timedelta(days=30)
    
    for link in soup.find_all("a", href=True):
        if "article" in link["href"]:
            url = link["href"] if link["href"].startswith("http") else f"https://www.nytimes.com{link['href']}"
            date_tag = link.find_next("time")
            if date_tag and date_tag.has_attr("datetime"):
                article_date = dt.fromisoformat(date_tag["datetime"].split("T")[0]).date()
                if month_ago <= article_date <= today:
                    articles.append({"url": url, "upload_time": article_date})
    
    return articles

def get_article_content(driver, url):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "제목 없음"
    content = "\n".join([p.get_text(strip=True) for p in soup.find_all("p")])
    return title, content

def translate_text(text):
    azure_endpoint = "https://apim-dwdp-openai.azure-api.net/007/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-04-01-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": "d932deacbffc451e84417fac864394b9",
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "messages": [
            {"role": "system", "content": "너는 한국어 번역 및 요약 도우미야."},
            {"role": "user", "content": f"다음 텍스트를 한국어로 번역해주고, 회사의 임원이 보시는 거라, 기사의 핵심 내용을 머릿말 기호를 사용하여 깔끔하게 요약해줘.:\n\n{text}"}
        ],
        "temperature": 0.3
    }
    response = requests.post(azure_endpoint, headers=headers, json=data)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "번역 실패")

def send_email(subject, body, recipient):
    sender_email = "eoaud0012@gmail.com"
    email_password = "ywad kvgh etlc nafm"
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        print("이메일 발송 성공!")
    except Exception as e:
        print("이메일 발송 중 오류 발생:", e)

def main():
    keywords = ["beverage", "korean rice wine", "wine", "soju", "beer", "drink"]
    driver = setup_driver()
    articles = []
    
    for keyword in keywords:
        html = search_nytimes(driver, keyword)
        articles += scrape_articles(html, keyword)
    
    email_body = ""
    for art in articles:
        title, content = get_article_content(driver, art['url'])
        text_to_translate = f"제목: {title}\n업로드 시간: {art['upload_time']}\n원문 URL: {art['url']}\n\n내용:\n{content}"
        print(f"번역 요청 중: {title}")
        translated_text = translate_text(text_to_translate)
        email_body += translated_text + "\n" + ("=" * 50) + "\n\n"
    
    driver.quit()
    
    if email_body:
        send_email("[NYT] 최근 일주일 패키징 음료 시장 기사", email_body, "eoaud0012@dongwon.com")
    else:
        print("최근 한 달 간 관련 기사가 없습니다.")

if __name__ == "__main__":
    main()
