import time
import datetime
import pyautogui
import win32com.client
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
time.sleep(1)

# Select 메뉴 선택 -> 날짜별 조회 클릭
select_menu = driver.find_element(By.ID, 'kind')
driver.execute_script("arguments[0].setAttribute('style','display: True;')", select_menu)
Select(driver.find_element(By.ID, 'kind')).select_by_value("WORKDT")

time.sleep(3)

# 내부 스크롤 바 맨 아래로 
itemlist = driver.find_element(By.CLASS_NAME, 'partlist_menu')
driver.execute_script("arguments[0].scrollBy(0,2500)",itemlist)

# selClass409 : 23/01/31 , seClass410 : 23/02/13
# 2/13일자로 상신된 프로젝트 보고서 목록 클릭

# 프로젝트 총괄 엑셀 파일 열기
try:
    excel = win32com.client.Dispatch("Excel.Application") 
    workbook = excel.Workbooks.Open(r"C:/Users/DW-PC\Desktop/이대명/프로젝트관리/★엔터프라이즈 프로젝트 총괄_2022년(자동).xlsx")
except:
    excel.quit()

# 시트 접근
worksheet = workbook.Worksheets("프로젝트보고서")

report_index = 410
while True:
    try:
        driver.find_element(By.ID, 'selClass'+str(report_index)).click()
        report_count = driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[2]/ul/li['+str(report_index)+']/span[2]')
        for count_num in range(0, int(report_count)):
            driver.find_element(By.ID, 'selClass'+str(report_index)).click()
            insert_row = 3
            worksheet.Rows(insert_row).Insert()
    except:
        break
    report_index += 1

# 2/13일자에 상신된 프로젝트 보고서 개수 저장
# 프로젝트보고서 목록이 하나밖에 없을 때
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr/td[3]/p/a
# 프로젝트보고서 모곡이 두 개 이상일 때
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[1]/td[3]/p/a
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[2]/td[3]/p/a
