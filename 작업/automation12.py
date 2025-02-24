import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By

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

driver.get("https://meeting.dongwon.com/usc/mtg/selectUscMtgResveDayList.do")
driver.implicitly_wait(5) # 페이지 다 뜰 때 까지 기다림
time.sleep(3)

# 로그인
driver.find_element(By.ID, 'id').send_keys('eoaud0012')
time.sleep(0.5)
driver.find_element(By.ID, 'password').send_keys('eoaoWkd1!!')
time.sleep(0.5)
driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[2]/ul/li[3]/a').click()
time.sleep(1)


# '오늘' 버튼 클릭
driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()
time.sleep(0.5)

# 날짜 하루 이동 X 7
for i in range(0,7):
    driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
    driver.implicitly_wait(5) # 페이지 다 뜰 때 까지 기다림
    time.sleep(0.5)

# '예약하기' 버튼 클릭
driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
time.sleep(1)

# 회의 제목 입력
driver.find_element(By.ID, 'mtgSj').send_keys('동원산업 DT본부 월간회의')
time.sleep(0.5)

# 회의실 분류 선택
Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("8F")
time.sleep(0.5)

# 회의실 세부 선택
Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸2")
time.sleep(0.5)

# 예약 시간 선택
Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("08:00")
time.sleep(0.5)

Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("12:00")
time.sleep(0.5)

# 확인 버튼 클릭
driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
time.sleep(0.5)

# 팝업창 제어
# time.sleep(1)
pop = Alert(driver)
time.sleep(1)
pop.accept()