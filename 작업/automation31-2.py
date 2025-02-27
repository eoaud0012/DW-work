import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import gspread
from google.oauth2.service_account import Credentials

# ----- Selenium WebDriver 설정 -----
chrome_options = Options()
chrome_options.add_argument("--headless")  # 디버깅 시 headless 모드 비활성화
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()  # 브라우저 창 최대화
wait = WebDriverWait(driver, 10)

# 1. ITSM 로그인 페이지 접속
driver.get("https://dwdesk.dongwon.com/xefc/egene/login_dw.jsp")

# 2. 로그인 처리
USERNAME = "eoaud0012"
id_field = wait.until(EC.presence_of_element_located((By.NAME, "emp_id")))
id_field.clear()
id_field.send_keys(USERNAME)

login_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//input[@type='submit' and @value='로그인']")))
login_button.click()

# 로그인 후 페이지 로딩 대기 (60초)
time.sleep(60)

# 3. PMS 메뉴 선택
pms_menu = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//span[contains(text(), 'PMS')]")))
pms_menu.click()

# 4. 프로젝트 이력 메뉴 선택
project_history_menu = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//span[contains(text(), '프로젝트 이력')]")))
project_history_menu.click()

# 메뉴 선택 후 추가 대기 (10초)
time.sleep(10)

# 5. 기준일 수정 (날짜 입력 방식 개선)
first_date = "20000101"
first_date_input = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "(//input[contains(@class, 'hasDatepicker')])[1]")))
first_date_input.click()  # 클릭하여 활성화
first_date_input.clear()
time.sleep(0.5)
for ch in first_date:
    first_date_input.send_keys(ch)
    time.sleep(0.1)
driver.find_element(By.TAG_NAME, "body").click()
time.sleep(1)

second_date = "21001231"
second_date_input = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "(//input[contains(@class, 'hasDatepicker')])[2]")))
second_date_input.click()
second_date_input.clear()
time.sleep(0.5)
for ch in second_date:
    second_date_input.send_keys(ch)
    time.sleep(0.1)
driver.find_element(By.TAG_NAME, "body").click()
time.sleep(5)

calendar_icon = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//div[@class='atom-group-prepend' and contains(@onclick, 'openCalendar')]")))
calendar_icon.click()
time.sleep(2)

day_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[normalize-space(text())='1']")))
day_button.click()
time.sleep(2)

# 5-1. '조회' 버튼 클릭
search_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[@title='조회']")))
search_button.click()

time.sleep(10)  # 조회 후 그리드 로딩 대기

# 6. 한 페이지당 노출 개수를 20으로 변경 (기본값은 25)
arrow_down_button = wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "div.jqx-icon-arrow-down.jqx-icon")))
driver.execute_script("arguments[0].scrollIntoView(true);", arrow_down_button)
arrow_down_button.click()
time.sleep(2)
option_20 = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//span[normalize-space(text())='20']")))
option_20.click()
time.sleep(3)

driver.execute_script("document.body.style.zoom='90%'")
time.sleep(1)

# 7. 페이지네이션을 이용하여 전체 데이터를 로드하기
collected_row_ids = set()
project_data = []
current_page = 1

while True:
    container = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.jqx-grid-content > div[id^='contenttable']")))
    time.sleep(2)  # 페이지 전환 후 데이터 로드 대기

    data_rows = container.find_elements(By.CSS_SELECTOR, "div[role='row']")
    new_rows_this_page = 0
    for row in data_rows:
        cells = row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")
        if len(cells) >= 8 and cells[1].text.strip() != "":
            project_data.append([cell.text.strip() for cell in cells[:8]])
            new_rows_this_page += 1

    if new_rows_this_page < 20:
        break

    next_page = current_page + 1
    page_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "input.jqx-input.jqx-widget-content.jqx-grid-pager-input.jqx-rc-all")))
    page_input.clear()
    page_input.send_keys(str(next_page))
    page_input.send_keys(Keys.ENTER)
    time.sleep(3)

    current_page = next_page

print("페이지네이션 완료: 전체 데이터 로드됨.")

print("수집된 프로젝트 데이터:")
for row in project_data:
    print(row)

# 8. Google 스프레드시트에 데이터 전송 (B2부터 기록)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(r"C:\Users\DW-PC\API\demianlee-c18e8f2ad88f.json", scopes=scope)
client = gspread.authorize(creds)

try:
    sheet = client.open("★ [PMS] DT본부 프로젝트 평가_250217_평가방식개선_배포용").worksheet("PMS 진척 상황 조회(UI)")
    sheet.clear()
    headers = [["No", "프로젝트명", "계열사", "PM", "시작일", "완료일", "진행단계", "점수"]]
    sheet.update(range_name="B2:I2", values=headers)
    if project_data:
        start_row = 3
        end_row = start_row + len(project_data) - 1
        cell_range = f"B{start_row}:I{end_row}"
        sheet.update(range_name=cell_range, values=project_data)
        print("Google 스프레드시트에 데이터 전송 완료.")
    else:
        print("전송할 데이터가 없습니다.")
except Exception as e:
    print("Google 스프레드시트 연결 오류:", e)

driver.quit()