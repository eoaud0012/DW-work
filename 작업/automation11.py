from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import time
import os

os.system('pip install --upgrade selenium')
os.system('taskkill /f /im chrome.exe')

print(webdriver.__version__)

options = Options()

user_data = r"C:\Users\DW-PC\AppData\Local\Google\Chrome\User Data"
options.add_argument(f"user-data-dir={user_data}")
options.add_experimental_option("detach", True)  # 화면이 꺼지지 않고 유지
options.add_argument("--start-maximized")  # 최대 크기로 시작
driver = webdriver.Chrome(options=options)

url = "https://blog.naver.com/birdiebirgi?categoryNo=6&tab=1"

driver.get(url)

try:
     # 경제뉴스스크랩 카테고리로 이동
    time.sleep(5)
    driver.find_element(By.ID, "category6").click()
    time.sleep(2)
except Exception as e:
    print("오류!")


# driver.quit()
