import os
import time
import datetime
import telegram
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By

# 텔레그램 설정
TELEGRAM_TOKEN = "6041435620:AAH-C98ovxjuHmKOFbDM7z-Y8lI88YK1UT4"
TELEGRAM_CHATID = "6055095538"

def send_telegram_message(success, date, room_name):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    if success:
        message = f"성공! {date}, {room_name} 예약 완료."
    else:
        message = f"실패! {date}, {room_name} 예약 실패."
    bot.send_message(chat_id=TELEGRAM_CHATID, text=message)

def is_third_tuesday(date):
    # 오늘이 화요일인지 확인 (월요일: 0, 화요일: 1, …)
    if date.weekday() != 1:
        return False
    # 1일부터 해당 날짜까지의 화요일 개수를 센다.
    tuesday_count = sum(1 for day in range(1, date.day + 1)
                        if datetime.date(date.year, date.month, day).weekday() == 1)
    return tuesday_count == 3

def reserve_meeting_room_once():
    # 대상: DT본부 AI혁신실 회의 (3F 미팅룸 2)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    room_name = "3F 미팅룸 2"
    driver = None
    try:
        # Selenium 업그레이드 및 기존 크롬 프로세스 종료
        os.system('pip install --upgrade selenium')
        os.system('taskkill /f /im chrome.exe')
        print("Selenium version:", webdriver.__version__)
        
        options = Options()
        user_data = r"C:\Users\DW-PC\AppData\Local\Google\Chrome\User Data"
        options.add_argument(f"user-data-dir={user_data}")
        options.add_experimental_option("detach", True)  # 브라우저 종료 방지 (디버깅용)
        options.add_argument("--start-maximized")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://meeting.dongwon.com/usc/mtg/selectUscMtgResveDayList.do")
        driver.implicitly_wait(5)
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
        
        # 날짜 이동: 하루씩 7회 클릭
        for i in range(7):
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
            driver.implicitly_wait(5)
            time.sleep(0.5)
        
        # '예약하기' 버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
        time.sleep(1)
        
        # 예약 정보 입력: 회의 제목, 회의실 분류 및 세부 선택, 시간 선택
        driver.find_element(By.ID, 'mtgSj').send_keys('DT본부 AI혁신실 회의')
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("3F")
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸 2")
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("15:00")
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("17:00")
        time.sleep(0.5)
        
        # 예약 확인
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
        time.sleep(0.5)
        pop = Alert(driver)
        time.sleep(1)
        pop.accept()
        
        send_telegram_message(True, today_str, room_name)
    except Exception as e:
        send_telegram_message(False, today_str, room_name)
        print("Error in reserve_meeting_room_once:", e)
    finally:
        if driver:
            driver.quit()

def reserve_meeting_room_twice():
    # 대상: 1) 동원산업 DT본부 월간회의 (8F 미팅룸2) / 2) DT본부 AI혁신실 회의 (3F 미팅룸 2)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    room_name1 = "8F 미팅룸2"
    room_name2 = "3F 미팅룸 2"
    driver = None
    try:
        # Selenium 업그레이드 및 기존 크롬 프로세스 종료
        os.system('pip install --upgrade selenium')
        os.system('taskkill /f /im chrome.exe')
        print("Selenium version:", webdriver.__version__)
        
        options = Options()
        user_data = r"C:\Users\DW-PC\AppData\Local\Google\Chrome\User Data"
        options.add_argument(f"user-data-dir={user_data}")
        options.add_experimental_option("detach", True)
        options.add_argument("--start-maximized")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://meeting.dongwon.com/usc/mtg/selectUscMtgResveDayList.do")
        driver.implicitly_wait(5)
        time.sleep(3)
        
        # 로그인
        driver.find_element(By.ID, 'id').send_keys('eoaud0012')
        time.sleep(0.5)
        driver.find_element(By.ID, 'password').send_keys('eoaoWkd1!!')
        time.sleep(0.5)
        driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[2]/ul/li[3]/a').click()
        time.sleep(1)
        
        # '오늘' 버튼 클릭 및 날짜 이동
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()
        time.sleep(0.5)
        for i in range(7):
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
            driver.implicitly_wait(5)
            time.sleep(0.5)
        
        # 첫 번째 예약: 동원산업 DT본부 월간회의 (8F 미팅룸2)
        try:
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
            time.sleep(1)
            driver.find_element(By.ID, 'mtgSj').send_keys('동원산업 DT본부 월간회의')
            time.sleep(0.5)
            Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("8F")
            time.sleep(0.5)
            Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸2")
            time.sleep(0.5)
            Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("08:00")
            time.sleep(0.5)
            Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("12:00")
            time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
            time.sleep(0.5)
            pop = Alert(driver)
            time.sleep(1)
            pop.accept()
            send_telegram_message(True, today_str, room_name1)
        except Exception as e:
            send_telegram_message(False, today_str, room_name1)
            print("Error in first reservation in reserve_meeting_room_twice:", e)
        
        # 두 번째 예약: DT본부 AI혁신실 회의 (3F 미팅룸 2)
        try:
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
            time.sleep(1)
            driver.find_element(By.ID, 'mtgSj').send_keys('DT본부 AI혁신실 회의')
            time.sleep(0.5)
            Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("3F")
            time.sleep(0.5)
            Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸 2")
            time.sleep(0.5)
            Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("15:00")
            time.sleep(0.5)
            Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("17:00")
            time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
            time.sleep(0.5)
            pop = Alert(driver)
            time.sleep(1)
            pop.accept()
            send_telegram_message(True, today_str, room_name2)
        except Exception as e:
            send_telegram_message(False, today_str, room_name2)
            print("Error in second reservation in reserve_meeting_room_twice:", e)
    except Exception as e:
        print("Error in reserve_meeting_room_twice overall:", e)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    today = datetime.date.today()
    if is_third_tuesday(today):
        reserve_meeting_room_twice()
    else:
        reserve_meeting_room_once()
