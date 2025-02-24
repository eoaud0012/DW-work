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

def send_telegram_message(success, use_day_str, room_name):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    if success:
        message = f"성공! {use_day_str}, {room_name} 예약 완료."
    else:
        message = f"실패! {use_day_str}, {room_name} 예약 실패."
    bot.send_message(chat_id=TELEGRAM_CHATID, text=message)

def is_third_tuesday(date):
    """
    달의 첫째 날부터 해당 날짜까지의 화요일 개수를 세어,
    오늘이 셋째 화요일이면 True, 아니면 False를 반환
    """
    if date.weekday() != 1:  # 화요일이 아니면
        return False
    tuesday_count = sum(1 for day in range(1, date.day + 1)
                        if datetime.date(date.year, date.month, day).weekday() == 1)
    return tuesday_count == 3

def reserve_meeting_room_seminar():
    """
    [목요일 예약]
    예약 대상: SE팀 목요세미나
    회의실: 3F 미팅룸 2
    예약 시간: 08:00 ~ 09:00
    사용일: 오늘 기준 일주일 뒤
    """
    use_day_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    room_name = "3F 미팅룸 2 (SE팀 목요세미나)"
    driver = None
    try:
        # Selenium 업데이트 및 기존 크롬 프로세스 종료
        os.system('pip install --upgrade selenium')
        os.system('taskkill /f /im chrome.exe')
        print("Selenium version:", webdriver.__version__)
        
        # Chrome 옵션 설정 (사용자 프로파일 지정)
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
        
        # '오늘' 버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()
        time.sleep(0.5)
        
        # 날짜 이동 (하루씩 7회 클릭 → 사용일 일주일 뒤)
        for i in range(7):
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
            driver.implicitly_wait(5)
            time.sleep(0.5)
        
        # '예약하기' 버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
        time.sleep(1)
        
        # 예약 정보 입력
        driver.find_element(By.ID, 'mtgSj').send_keys('SE팀 목요세미나')
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "lcSe")).select_by_visible_text("3F")
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "mtgPlaceId")).select_by_visible_text("미팅룸 2")
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "resveBeginTm")).select_by_visible_text("08:00")
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "resveEndTm")).select_by_visible_text("09:00")
        time.sleep(0.5)
        
        # 확인 버튼 클릭 및 팝업 제어
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div[1]/div[2]/ul/li[2]/a').click()
        time.sleep(0.5)
        pop = Alert(driver)
        time.sleep(1)
        pop.accept()
        
        send_telegram_message(True, use_day_str, room_name)
    except Exception as e:
        send_telegram_message(False, use_day_str, room_name)
        print("Error in reserve_meeting_room_seminar:", e)
    finally:
        if driver:
            driver.quit()

def reserve_meeting_room_once():
    """
    [화요일 예약 – 비셋째 화요일]
    예약 대상: DT본부 AI혁신실 회의
    회의실: 3F 미팅룸 2
    예약 시간: 15:00 ~ 17:00
    사용일: 오늘 기준 일주일 뒤
    """
    use_day_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    room_name = "3F 미팅룸 2 (AI혁신실 회의)"
    driver = None
    try:
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
        
        # '오늘' 버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()
        time.sleep(0.5)
        
        # 날짜 이동 (하루씩 7회 클릭)
        for i in range(7):
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
            driver.implicitly_wait(5)
            time.sleep(0.5)
        
        # '예약하기' 버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[6]/div[2]/ul/li/a').click()
        time.sleep(1)
        
        # 예약 정보 입력
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
        
        send_telegram_message(True, use_day_str, room_name)
    except Exception as e:
        send_telegram_message(False, use_day_str, room_name)
        print("Error in reserve_meeting_room_once:", e)
    finally:
        if driver:
            driver.quit()

def reserve_meeting_room_twice():
    """
    [화요일 예약 – 셋째 화요일]
    첫 번째 예약: 동원산업 DT본부 월간회의 (8F 미팅룸2, 08:00~12:00)
    두 번째 예약: DT본부 AI혁신실 회의 (3F 미팅룸 2, 15:00~17:00)
    사용일: 오늘 기준 일주일 뒤
    """
    use_day_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    room_name1 = "8F 미팅룸2 (DT본부 월간회의)"
    room_name2 = "3F 미팅룸 2 (AI혁신실 회의)"
    driver = None
    try:
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
        
        # '오늘' 버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[5]/div/a').click()
        time.sleep(0.5)
        
        # 날짜 이동 (하루씩 7회 클릭)
        for i in range(7):
            driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[4]/ul/li[3]/a').click()
            driver.implicitly_wait(5)
            time.sleep(0.5)
        
        # 첫 번째 예약: 동원산업 DT본부 월간회의
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
            send_telegram_message(True, use_day_str, room_name1)
        except Exception as e:
            send_telegram_message(False, use_day_str, room_name1)
            print("Error in first reservation in reserve_meeting_room_twice:", e)
        
        # 두 번째 예약: DT본부 AI혁신실 회의
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
            send_telegram_message(True, use_day_str, room_name2)
        except Exception as e:
            send_telegram_message(False, use_day_str, room_name2)
            print("Error in second reservation in reserve_meeting_room_twice:", e)
    except Exception as e:
        print("Error in reserve_meeting_room_twice overall:", e)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    today = datetime.date.today()
    weekday = today.weekday()  # Monday=0, Tuesday=1, ..., Thursday=3, etc.
    
    if weekday == 3:
        # 목요일: 세미나 예약
        reserve_meeting_room_seminar()
    elif weekday == 1:
        # 화요일: 예약 조건에 따라
        if is_third_tuesday(today):
            reserve_meeting_room_twice()
        else:
            reserve_meeting_room_once()
    else:
        print("오늘은 예약 대상 요일이 아닙니다.")