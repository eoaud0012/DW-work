import time
import datetime
import pyautogui
import pyperclip
import win32com.client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Direct 사이트 접속
driver = webdriver.Chrome("chromedriver") # Webdriver 파일의 경로를 입력
driver.get('https://direct.dongwon.com/WebSite/Login.aspx') # 이동을 원하는 페이지 주소 입력
driver.implicitly_wait(5) # 페이지 다 뜰 때 까지 기다림

# 로그인
driver.find_element(By.ID, 'txtPC_LoginID').send_keys('eoaud0012')
driver.find_element(By.ID, 'txtPC_LoginPWTemp').click()
pyperclip.copy('eoaoWkd1!!!')
ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
driver.find_element(By.XPATH, '/html/body/form/div[3]/div[1]/div/div[1]/div/dl/dd[2]/a/em').click()

# 전자결재 - 업무문서함 - 프로젝트보고서 - 완료함 이동
driver.get('https://direct.dongwon.com/WebSite/Approval/List.aspx?system=Approval&alias=P.APPROVAL.APPROVAL&mnid=134')
driver.get('https://direct.dongwon.com/WebSite/Approval/ListBD.aspx?system=Approval&uid=%42%44%5f%45%5f%36%30%5f%30%30%31%5f%30%31_COMPLETE&location=BizDoc&mode=COMPLETE&label=%ec%99%84%eb%a3%8c%ec%9d%bc%ec%9e%90&location_name=%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%EB%B3%B4%EA%B3%A0%EC%84%9C')

select_menu = driver.find_element(By.ID, 'kind')
driver.execute_script("arguments[0].setAttribute('style','display: True;')", select_menu)
Select(driver.find_element(By.ID, 'kind')).select_by_value("WORKDT")

time.sleep(3)
itemlist = driver.find_element(By.CLASS_NAME, 'partlist_menu')
driver.execute_script("arguments[0].scrollBy(0,2500)",itemlist)

driver.find_element(By.ID, 'selClass409').click()