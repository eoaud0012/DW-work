# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time

# SRT 사이트 접속
driver = webdriver.Chrome("chromedriver") # Webdriver 파일의 경로를 입력
driver.get('https://etk.srail.co.kr/cmc/01/selectLoginForm.do') # 이동을 원하는 페이지 주소 입력
driver.implicitly_wait(15) # 페이지 다 뜰 때 까지 기다림

# 로그인
driver.find_element(By.ID, 'srchDvNm01').send_keys('2287599141') # 회원번호
driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys("eoaoWkd1!") # 비밀번호
driver.find_element(By.XPATH, '//*[@id="login-form"]/fieldset/div[1]/div[1]/div[2]/div/div[2]/input').click()
driver.implicitly_wait(5)

# 기차 조회 페이지로 이동
driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
driver.implicitly_wait(5)

# 출발지 입력
dep_stn = driver.find_element(By.ID, 'dptRsStnCdNm')
dep_stn.clear() 
dep_stn.send_keys("수서")

# 도착지 입력
arr_stn = driver.find_element(By.ID, 'arvRsStnCdNm')
arr_stn.clear()
arr_stn.send_keys("부산")

# 날짜 드롭다운 리스트 보이게
elm_dptDt = driver.find_element(By.ID, "dptDt")
driver.execute_script("arguments[0].setAttribute('style','display: True;')", elm_dptDt)

# 2022년 09월 08일 기차 선택
Select(driver.find_element(By.ID,"dptDt")).select_by_value("20220908")

# 출발 시간
elm_dptTm = driver.find_element(By.ID, "dptTm")
driver.execute_script("arguments[0].setAttribute('style','display: True;')", elm_dptTm)
Select(driver.find_element(By.ID, "dptTm")).select_by_visible_text("18")

# 조회하기 버튼 클릭
driver.find_element(By.XPATH,"//input[@value='조회하기']").click()

# 조회 결과 중 상위 두 개의 기차의 일반실에 "예약하기" 버튼이 활성화 되어 있는 경우를 확인
for i in range(1, 3):
    standard_seat = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7)").text
    
    # '예약하기'가 활성화 되어있을 경우 예약 버튼 클릭하기
    if "예약하기" in standard_seat:
        print("예약 가능")        
        driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div/div[3]/div[1]/form/fieldset/div[6]/table/tbody/tr[{i}]/td[7]/a/span").click()
        
        # CSS Selector 사용시 예약하기 대신 좌석선택이 눌러지는 문제가 있어 XPATH로 변경
        # driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7) > a").click()


# 매진일 경우 새로고침
reserved = False

while True:
    for i in range(1, 5): # 상위 4개 기차 확인
        standard_seat = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7)").text

        if "예약하기" in standard_seat:
            print("예약 가능")       
            driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div/div[3]/div[1]/form/fieldset/div[6]/table/tbody/tr[{i}]/td[7]/a/span").click()
            reserved = True
            break

    if not reserved:
        # 5초 기다리기
        time.sleep(5)
        
        # 다시 조회하기
        submit = driver.find_element(By.XPATH, "//input[@value='조회하기']")
        driver.execute_script("arguments[0].click();", submit)
        print("새로고침")

        driver.implicitly_wait(10)
        time.sleep(1)
    else:
        break