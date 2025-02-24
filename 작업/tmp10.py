from newspaper import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def extract_main_text_with_newspaper(page_source):
    """
    newspaper3k 라이브러리를 이용해
    HTML 소스에서 기사 본문을 추출한다.
    """
    article = Article(url="", language="en")  # url은 없어도 됨
    article.set_html(page_source)
    article.parse()
    return article.text

def main():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 필요 시 헤드리스 모드
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.einnews.com/pr_news/785345547/low-alcohol-beer-market-to-hit-usd-34-14b-by-2032-at-6-1-cagr-driven-by-the-rising-popularity-of-craft-beer")
    time.sleep(3)

    page_source = driver.page_source
    main_text = extract_main_text_with_newspaper(page_source)
    print("==== 추출된 본문 ====")
    print(main_text)

    driver.quit()

if __name__ == "__main__":
    main()
