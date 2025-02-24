# -*- coding: utf-8 -*-
import time
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

# 가장 최근 전결이 난 프로젝트 보고서의 전결날짜와 프로젝트 관리 총괄 파일에 있는 업데이트 날짜와 비교
# 프로젝트 총괄 엑셀 파일 열기

try:
    excel = win32com.client.Dispatch("Excel.Application") 
    workbook = excel.Workbooks.Open(r"C:/Users/DW-PC\Desktop/이대명/프로젝트관리/★엔터프라이즈 프로젝트 총괄_2022년(자동).xlsx")
except:
    excel.quit()
    driver.quit()

# 시트 접근
worksheet = workbook.Worksheets("프로젝트보고서")

# C열 3행 값(최신 프로젝트 보고서 프로젝트 코드) infile_current_project_code 저장
infile_current_project_code = worksheet.cells(3,3).value

# D열 3행 값(최신 프로젝트 보고서 프로젝트 상신 상태) infile_current_project_status 저장
infile_current_project_status = worksheet.cells(4,3).value

# F열 3행 값(최신 프로젝트 보고서 프로젝트 이름) infile_current_project_name 저장
infile_current_project_name = worksheet.cells(6,3).value

# 프로젝트 이름, 코드 출력
print("엑셀 파일 내 작성된 마지막 프로젝트는 " + infile_current_project_name +'('+"infile_current_project_code"+')'+ "입니다.", end='\n')
print('프로젝트 상신 상태는 '+infile_current_project_status+' 입니다.')

# 전자결재 - 업무문서함 - 프로젝트보고서 - 완료함에서 상신된 보고서 카운트 개수 세기(목록 30개씩 출력 시)
try:
    count = 0

    # 프로젝트 목록에서 맨 상위 프로젝트부터 차례대로 클릭
    for i in range(1, 31):
        
        # 목록 중 한 개 클릭
        driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr['+str(i)+']/td[3]/p/a').click()
        
        # 제목 가져오기
        web_uploaded_report_code = driver.find_element(By.ID, "Prjno").text

        # 프로젝트 상신 상태 가져오기
        if(driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[1]').text == "●"):
            web_uploaded_report_status = "계획"
        elif(driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[1]').text == "●"):
            web_uploaded_report_status = "변경"
        else:
            web_uploaded_report_status = "완료"


        # 프로젝트 이름 가져오기
        web_uploaded_report_name = driver.find_element(By.ID, "Pjname").click()
        
        if(infile_current_project_code == web_uploaded_report_code and
           infile_current_project_name == web_uploaded_report_name and
           infile_current_project_status == web_uploaded_report_status):
            print("이미 프로젝트 보고서가 모두 업데이트되어 있습니다. 프로그램을 종료합니다.\n")
            excel.quit()
            driver.quit()
        else:
            pass

    # 새롭게 상신된 보고서 개수만큼 총괄 파일 업데이트 진행
    for j in range(1, i+1):
        driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr['+str(i)+']/td[3]/p/a').click()

        # 팝업창(상신 의견창) 제어
        # 크롬 탭 개수 가져오기
        window_tabs = driver.window_handles

        # 팝업창(상신 의견창)이 한 개라도 있으면
        if(len(window_tabs) > 1):
            # 상신 의견창이 남아있는 동안
            while(len(window_tabs < 1)):
                # 팝업창 하나하나씩
                driver.switch_to_window(1)
                # 닫기
                driver.close()
            # 원래 화면 이동
            driver.switch_to_window(0)

        # 보고서 종류 확인
        if(driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[1]').text == "●"):
            report_type = "계획"
        elif(driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[1]').text == "●"):
            report_type = "변경"
        else:
            report_type = "완료"
except:
    workbook.Close(SaveChanges=0)
    excel.quit()
    driver.quit()

# 구분(계획, 변경, 완료)
# 계획보고서
# /html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[1] == ●
# 변경보고서
# /html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[2] == ●
# 완료보고서
# /html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[3] == ●


        
        

    

    


# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[1]/td[3]/p/a


# Direct -> 업무문서함 -> 완료함 제목 순서
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[1]/td[3]/p/a
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[2]/td[3]/p/a
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[3]/td[3]/p/a
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[30]/td[3]/p/a

# Direct -> 
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[1]/td[8]
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[2]/td[8]


# driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div/form/div/div/div/div/div[1]/div/div[2]/div[2]/div/input[3]").click()
# pyautogui.hotkey("ctrl", "a")
# pyautogui.press("delete")
# pyperclip.copy("2022-08-01")
# pyautogui.hotkey('ctrl', 'v')

# driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div/form/div/div/div/div/div[1]/div/div[2]/div[2]/div/input[4]").click()
# pyautogui.hotkey("ctrl", "a")
# pyautogui.press("delete")
# pyperclip.copy("2022-08-31")
# pyautogui.hotkey('ctrl', 'v')


# 프로젝트 상신 상태 中 '계획' 글씨 위치
# /html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[1]
# /html/body/form/div[3]/div/div[1]/div[3]/div[2]/div/div/table[6]/tbody/tr[2]/td[1]/div/span[1]

# 프로젝트 전결일 순서
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[1]/td[8]
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[2]/td[8]
# /html/body/form/div[3]/div/div/div[4]/div/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/listhtml/table/tbody/tr[30]/td[8]