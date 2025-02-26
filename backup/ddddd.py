# dddd.py에서 각 기능을 함수로 변경>

# -*- coding: utf-8 -*-
import time
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


def open_brower():
    driver = webdriver.Chrome("chromedriver")
    return driver


def login(driver, login_id, login_psw):
    driver.get('https://etk.srail.co.kr/cmc/01/selectLoginForm.do')
    driver.implicitly_wait(15)
    driver.find_element(By.ID, 'srchDvNm01').send_keys(str(login_id))
    driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys(str(login_psw))
    driver.find_element(By.XPATH, '//*[@id="login-form"]/fieldset/div[1]/div[1]/div[2]/div/div[2]/input').click()
    driver.implicitly_wait(5)
    return driver

# 예약 가능 여부를 체크할 기차의 숫자를 설정할 변수 (변수명 num_trains_to_check), 기본값 2
def search_train(driver, dpt_stn, arr_stn, dpt_dt, dpt_tm, num_trains_to_check=6, want_reserve=False):
    is_booked = False # 예약 완료 되었는지 확인용
    cnt_refresh = 0 # 새로고침 회수 기록

    driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do') # 기차 조회 페이지로 이동
    driver.implicitly_wait(5)
    # 출발지/도착지/출발날짜/출발시간 입력
    elm_dpt_stn = driver.find_element(By.ID, 'dptRsStnCdNm')
    elm_dpt_stn.clear()
    elm_dpt_stn.send_keys(dpt_stn) # 출발지
    elm_arr_stn = driver.find_element(By.ID, 'arvRsStnCdNm')
    elm_arr_stn.clear()
    elm_arr_stn.send_keys(arr_stn) # 도착지
    elm_dptDt = driver.find_element(By.ID, "dptDt")
    driver.execute_script("arguments[0].setAttribute('style','display: True;')", elm_dptDt)
    Select(driver.find_element(By.ID,"dptDt")).select_by_value(dpt_dt) # 출발날짜
    elm_dptTm = driver.find_element(By.ID, "dptTm")
    driver.execute_script("arguments[0].setAttribute('style','display: True;')", elm_dptTm)
    Select(driver.find_element(By.ID, "dptTm")).select_by_visible_text(dpt_tm) # 출발시간

    print("기차를 조회합니다")
    print(f"출발역:{dpt_stn} , 도착역:{arr_stn}\n날짜:{dpt_dt}, 시간: {dpt_tm}시 이후\n{num_trains_to_check}개의 기차 중 예약")
    print(f"예약 대기 사용: {want_reserve}")

    driver.find_element(By.XPATH, "//input[@value='조회하기']").click() # 조회하기 버튼 클릭
    driver.implicitly_wait(5)
    time.sleep(1)

    while True:
        for i in range(1, num_trains_to_check+1):
            # 일반좌석 column 확인
            standard_seat = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7)").text
            # 예약대기 column 확인
            reservation = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(8)").text
          
            if "예약하기" in standard_seat:
                print("예약 가능 클릭")
                driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7) > a").click() #CSS Selector로 변경
                driver.implicitly_wait(3)

                if driver.find_elements(By.ID, 'isFalseGotoMain'):
                    is_booked = True
                    print("예약 성공")
                    break
                else:
                    print("잔여석 없음. 다시 검색")
                    driver.back() # 뒤로가기
                    driver.implicitly_wait(5)

            # 예약대기가 설정되어 있고, 예약대기의 신청하기 버튼이 활성화되어 있을 경우 클릭
            if want_reserve:
                if "신청하기" in reservation:
                    print("예약 대기 완료")
                    driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(8) > a").click()
                    is_booked = True
                    break

        if not is_booked:
            time.sleep(randint(0, 1)) #2~4초 랜덤으로 기다리기

            # 다시 조회하기
            
            submit = driver.find_element(By.XPATH, "//input[@value='조회하기']")
            driver.execute_script("arguments[0].click();", submit)
            cnt_refresh += 1
            print(f"새로고침 {cnt_refresh}회")
            driver.implicitly_wait(10)
            time.sleep(0.5)
        else:
            break
    return driver


if __name__ == "__main__":
    driver = open_brower()
    driver = login(driver, '2287599141', 'eoaoWkd1!') # 회원 번호, 비밀번호
    search_train(driver, "수서", "부산", "20220908", "18", want_reserve=True)