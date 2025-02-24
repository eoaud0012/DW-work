from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert

# Direct 사이트 접속
driver = webdriver.Chrome("chromedriver") # Webdriver 파일의 경로를 입력

# 3F 회의실 2 접속
# driver.get('https://meeting.dongwon.com/pad.jsp?ip=10.200.31.152') # 이동을 원하는 페이지 주소 입력

# 8F 회의실 2 접속
driver.get('https://meeting.dongwon.com/pad.jsp?ip=10.200.81.161') # 이동을 원하는 페이지 주소 입력
driver.implicitly_wait(5) # 페이지 다 뜰 때 까지 기다림

# 입실하기 
driver.find_element(By.XPATH, '//*[@id="now_div"]/div[2]/ul[2]/li[1]').click()

# 팝업창 제어
pop = Alert(driver)
pop.accept()

# 입실하기 xPath
# //*[@id="now_div"]/div/ul[2]/li[1]
# //*[@id="now_div"]/div[2]/ul[2]/li[1]

# 퇴실하기 xPath
# //*[@id="now_div"]/div/ul[2]/li[2]
# //*[@id="now_div"]/div[2]/ul[2]/li[2]