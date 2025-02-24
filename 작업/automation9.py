import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

os.system('pip install --upgrade selenium')
os.system('taskkill /f /im chrome.exe')

print(webdriver.__version__)

options = Options()

user_data = r"C:\Users\DW-PC\AppData\Local\Google\Chrome\User Data"
options.add_argument(f"user-data-dir={user_data}")
options.add_experimental_option("detach", True)  # 화면이 꺼지지 않고 유지
options.add_argument("--start-maximized")  # 최대 크기로 시작
driver = webdriver.Chrome(options=options)


# driver = uc.Chrome(enable_cdp_events=True)

driver.get("https://blog.naver.com/birdiebirgi?categoryNo=6&tab=1")
time.sleep(5)

print("예약완료")