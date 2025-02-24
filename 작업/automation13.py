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

def reserve_meeting_room_seminar():
    """
    예약 대상: SE팀 목요세미나
    회의실: 3F 미팅룸 2
    예약 시간: 08:00 ~ 09:00
    사용일: 오늘 기준 일주일 뒤
    """
    use_day_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    room_name = "3F 미팅룸 2"
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

if __name__ == "__main__":
    # 예약할 코드 모두 실행 (원하는 예약만 선택하여 실행 가능)
   reserve_meeting_room_seminar()