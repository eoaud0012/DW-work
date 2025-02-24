import os
import time
import datetime
import telegram
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By

def is_third_tuesday(date):
    # 오늘이 화요일인지 확인 (월요일: 0, 화요일: 1, …)
    if date.weekday() != 1:
        return False
    # 1일부터 해당 날짜까지의 화요일 개수를 센다.
    tuesday_count = sum(1 for day in range(1, date.day + 1)
                        if datetime.date(date.year, date.month, day).weekday() == 1)
    return tuesday_count == 3

# 텔레그램 설정
TELEGRAM_TOKEN = "6041435620:AAH-C98ovxjuHmKOFbDM7z-Y8lI88YK1UT4"
TELEGRAM_CHATID = "6055095538"

def send_telegram_message(success, use_day_str, room_name, time_slot):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    message = f"{'성공' if success else '실패'}! {use_day_str} ({time_slot}), {room_name} 예약 {'완료' if success else '실패'}."
    bot.send_message(chat_id=TELEGRAM_CHATID, text=message)

def ensure_logged_in(driver):
    try:
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a')
        print("이미 로그인된 상태입니다.")
    except Exception:
        print("로그인 필요. 로그인 진행합니다.")
        driver.find_element(By.ID, 'id').send_keys('eoaud0012')
        time.sleep(0.5)
        driver.find_element(By.ID, 'password').send_keys('eoaoWkd1!!')
        time.sleep(0.5)
        driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[2]/ul/li[3]/a').click()
        time.sleep(1)

def start_chrome_with_default_profile():
    os.system('pip install --upgrade selenium')
    os.system('taskkill /f /im chrome.exe')
    print("Selenium version:", webdriver.__version__)

    options = Options()
    user_data = r"C:\Users\DW-PC\AppData\Local\Google\Chrome\User Data"
    options.add_argument(f"user-data-dir={user_data}")
    options.add_argument('--profile-directory="Default"')
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get("https://meeting.dongwon.com/usc/mtg/selectUscMtgResveDayList.do")
    driver.implicitly_wait(5)
    time.sleep(3)
    return driver

def reserve_meeting_room_seminar():
    use_day_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    room_name = "3F 미팅룸 2 (SE팀 목요세미나)"
    time_slot = "08:00 ~ 09:00"
    driver = None

    try:
        driver = start_chrome_with_default_profile()
        ensure_logged_in(driver)
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()
        time.sleep(0.5)
        for _ in range(7):
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
            time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
        time.sleep(1)
        driver.find_element(By.ID, 'mtgSj').send_keys('SE팀 목요세미나')
        Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("3F")
        Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸 2")
        Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("08:00")
        Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("09:00")
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
        time.sleep(1)
        Alert(driver).accept()
        send_telegram_message(True, use_day_str, room_name, time_slot)
    except Exception as e:
        send_telegram_message(False, use_day_str, room_name, time_slot)
        print("Error in reserve_meeting_room_seminar:", e)
    finally:
        if driver:
            driver.quit()

def reserve_meeting_room_twice():
    use_day_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    room_name1 = "8F 미팅룸2 (DT본부 월간회의)"
    time_slot1 = "08:00 ~ 12:00"
    room_name2 = "3F 미팅룸 2 (AI혁신실 회의)"
    time_slot2 = "15:00 ~ 17:00"
    driver = None

    try:
        driver = start_chrome_with_default_profile()
        ensure_logged_in(driver)
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()
        time.sleep(0.5)
        for _ in range(7):
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
            time.sleep(0.5)
        # 첫 번째 예약
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
        time.sleep(1)
        driver.find_element(By.ID, 'mtgSj').send_keys('DT본부 월간회의')
        Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("8F")
        Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸 2")
        Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("08:00")
        Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("12:00")
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
        time.sleep(1)
        Alert(driver).accept()
        send_telegram_message(True, use_day_str, room_name1, time_slot1)
        # 두 번째 예약
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
        time.sleep(1)
        driver.find_element(By.ID, 'mtgSj').send_keys('AI혁신실 회의')
        Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("3F")
        Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸 2")
        Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("15:00")
        Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("17:00")
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
        time.sleep(1)
        Alert(driver).accept()
        send_telegram_message(True, use_day_str, room_name2, time_slot2)
    except Exception as e:
        print("Error in reserve_meeting_room_twice:", e)
    finally:
        if driver:
            driver.quit()

def reserve_meeting_room_once():
    use_day_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    room_name = "3F 미팅룸 2 (AI혁신실 회의)"
    time_slot = "15:00 ~ 17:00"
    driver = None

    try:
        driver = start_chrome_with_default_profile()
        ensure_logged_in(driver)
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()
        time.sleep(0.5)
        for _ in range(7):
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
            time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
        time.sleep(1)
        driver.find_element(By.ID, 'mtgSj').send_keys('AI혁신실 회의')
        Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("3F")
        Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸 2")
        Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("15:00")
        Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("17:00")
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
        time.sleep(1)
        Alert(driver).accept()
        send_telegram_message(True, use_day_str, room_name, time_slot)
    except Exception as e:
        send_telegram_message(False, use_day_str, room_name, time_slot)
        print("Error in reserve_meeting_room_once:", e)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    DEBUG_MODE = True
    if DEBUG_MODE:
        # 디버그 모드: 현재 날짜를 기준으로 예약 함수를 자동으로 호출합니다.
        today = datetime.date.today()
        weekday = today.weekday()  # Monday=0, Tuesday=1, ...
        if weekday == 3:
            reserve_meeting_room_seminar()
        elif weekday == 1:
            if is_third_tuesday(today):
                reserve_meeting_room_twice()
            else:
                reserve_meeting_room_once()
        else:
            print("오늘은 예약 대상 요일이 아닙니다.")
    else:
        # 디버그 모드가 아닐 경우에도 동일한 조건으로 예약 함수가 실행됩니다.
        today = datetime.date.today()
        weekday = today.weekday()
        if weekday == 3:
            reserve_meeting_room_seminar()
        elif weekday == 1:
            if is_third_tuesday(today):
                reserve_meeting_room_twice()
            else:
                reserve_meeting_room_once()
        else:
            print("오늘은 예약 대상 요일이 아닙니다.")
