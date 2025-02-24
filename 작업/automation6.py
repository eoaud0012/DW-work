# -*- coding: utf-8 -*-
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

# 프로젝트 총괄 엑셀 파일 열기
try:
    excel = win32com.client.Dispatch("Excel.Application") 
    workbook = excel.Workbooks.Open(r"C:/Users/DW-PC\Desktop/이대명/프로젝트관리/★엔터프라이즈 프로젝트 총괄_2022년(자동).xlsx")
except:
    excel.quit()

# 시트 접근
worksheet = workbook.Worksheets("프로젝트보고서")

# B열 3행 값(최신 프로젝트 보고서 전결일) infile_current_date 저장
infile_current_date = worksheet.cells(2,3).value

# 연도 추출, 월 추출, 일 추출
infile_year = '20' + infile_current_date[:2] 
infile_month = infile_current_date[2:4]
infile_day = infile_current_date[4:6]
infile_count = infile_current_date[7:9]

# 합체 및 '230131' 형태로 변경
infile_current_date_formatted = infile_year + '-' + infile_month + '-' + infile_day


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

# 엑셀 전결일 맨 뒤에 붙는 숫자. -01 -02 -03 ... default 값은 1
count = '01'

# 전결일 String 데이터를 저장하기 위한 리스트
direct_current_date_list = []

# 가장 최근 전결이 난 프로젝트 보고서의 전결날짜와 프로젝트 관리 총괄 파일에 있는 업데이트 날짜와 비교
for i in range(1, 31):
    # 전결일 가져오기
    direct_current_date = driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[+'+str(i)+']/td[8]').text
    





    # 전결일을 리스트에 저장
    direct_current_date_list.append(direct_current_date)

    # 전결일 포맷 변경
    # 문자열을 datetime 객체로 변환
    date_obj = datetime.datetime.strptime(direct_current_date, '%Y-%m-%d %H:%M')

    # 연도, 월, 일 추출
    year = str(date_obj.year)[2:]
    if(int(date_obj.month) > 9):
        month = str(date_obj.month)
    else:
        month = '0' + str(date_obj.month)
    day = date_obj.day
    hour = date_obj.hour

    # 연도, 월, 일, count를 합쳐서 새로운 변수에 할당
    direct_current_date_modified = year + day + '-' + count

    # 새로운 변수가