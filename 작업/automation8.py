from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert

# Direct 사이트 접속
driver = webdriver.Chrome("chromedriver") # Webdriver 파일의 경로를 입력
driver.get('https://meeting.dongwon.com/usc/mtg/selectUscMtgResveDayList.do') # 이동을 원하는 페이지 주소 입력
driver.implicitly_wait(5) # 페이지 다 뜰 때 까지 기다림

# 로그인
driver.find_element(By.ID, 'id').send_keys('eoaud0012')
driver.find_element(By.ID, 'password').send_keys('eoaoWkd1!!!')
driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[2]/ul/li[3]/a').click()

# '오늘' 버튼 클릭
driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()

# 날짜 하루 이동 X 7
for i in range(0,7):
    driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
    driver.implicitly_wait(5) # 페이지 다 뜰 때 까지 기다림

# '예약하기' 버튼 클릭
driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()

# 회의 제목 입력
driver.find_element(By.ID, 'mtgSj').send_keys('SAP 데이터플랫폼 회의')

# 회의실 분류 선택
Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("4F")

# 회의실 세부 선택
Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("Pacific Ocean(태평양)")

# 예약 시간 선택
Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("14:00")
Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("16:00")

# 확인 버튼 클릭
driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()

# 팝업창 제어
pop = Alert(driver)
pop.accept()