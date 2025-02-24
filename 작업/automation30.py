import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# 5. 기준일 수정 (datepicker 요소 선택)
first_date_input = wait.until(EC.presence_of_element_located(
    (By.XPATH, "(//input[contains(@class, 'hasDatepicker')])[1]")))
first_date_input.clear()
first_date_input.send_keys("20000101")  # 숫자만 입력하면 자동 '-' 채워짐

second_date_input = wait.until(EC.presence_of_element_located(
    (By.XPATH, "(//input[contains(@class, 'hasDatepicker')])[2]")))
second_date_input.clear()
second_date_input.send_keys("21001231")

# 5-1. '조회' 버튼 클릭
search_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[@title='조회']")))
search_button.click()

# 조회 후 그리드 로딩 대기 (10초)
time.sleep(10)

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

# 6-1. 크롬 웹페이지 배율을 90%로 변경
driver.execute_script("document.body.style.zoom='90%'")
time.sleep(1)

# 7. 페이지네이션을 이용하여 전체 데이터를 로드하기
collected_row_ids = set()
project_data = []
current_page = 1

while True:
    print(f"페이지 {current_page} 데이터 수집 중...")
    # 그리드 컨테이너 재탐색 (페이지마다 id가 달라질 수 있음)
    container = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.jqx-grid-content > div[id^='contenttable']")))
    time.sleep(2)  # 추가 대기

    data_rows = container.find_elements(By.CSS_SELECTOR, "div[role='row']")
    new_rows_this_page = 0
    for row in data_rows:
        row_id = row.get_attribute("id")
        # 두 번째 셀(프로젝트명)이 비어있지 않은 경우에만 수집
        cells = row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")
        if row_id and row_id not in collected_row_ids and len(cells) >= 2 and cells[1].text.strip() != "":
            collected_row_ids.add(row_id)
            # 첫 8개 셀의 텍스트를 수집
            row_text = [cell.text.strip() for cell in cells[:8]]
            project_data.append(row_text)
            new_rows_this_page += 1
    print(f"페이지 {current_page}: 새 행 {new_rows_this_page}개 추가됨.")

    # 페이지 전환: 페이지 번호 입력 필드에 새 페이지 번호 입력 후 ENTER키 전송
    next_page = current_page + 1
    try:
        page_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.jqx-input.jqx-widget-content.jqx-grid-pager-input.jqx-rc-all")))
        print(f"페이지 {current_page}에서 {next_page}로 전환 중(엔터 전송)...")
        page_input.clear()
        page_input.send_keys(str(next_page))
        page_input.send_keys(Keys.ENTER)
        time.sleep(2)  # 페이지 전환 대기

        # 페이지 입력 필드의 값이 새 페이지 번호로 업데이트 되었는지 확인
        new_page_value = page_input.get_attribute("value")
        if new_page_value != str(next_page):
            print("페이지 전환 실패 혹은 마지막 페이지입니다.")
            break
        else:
            current_page = next_page
    except Exception as e:
        print("다음 페이지로 전환 중 오류:", e)
        break

print("페이지네이션 완료: 전체 데이터 로드됨.")

# 7-1. 터미널에 수집된 모든 데이터를 순서대로 출력
print("수집된 프로젝트 데이터:")
for row in project_data:
    print(row)

# 8. Google 스프레드시트에 데이터 전송 (B2부터 기록)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("demainlee-a5dec966352c.json", scope)
client = gspread.authorize(creds)

try:
    sheet = client.open("★ [PMS] DT본부 프로젝트 평가_250217_평가방식개선_배포용").worksheet("PMS 진척 상황 조회(UI)")
    sheet.clear()
    headers = [["No", "프로젝트명", "계열사", "PM", "시작일", "완료일", "진행단계", "점수"]]
    # 헤더는 B2부터 기록
    sheet.update(range_name="B2:I2", values=headers)
    if project_data:
        start_row = 3
        end_row = start_row + len(project_data) - 1
        cell_range = f"B{start_row}:I{end_row}"
        # 웹페이지 순서대로 기록 (순서를 그대로 유지)
        sheet.update(range_name=cell_range, values=project_data)
        print("Google 스프레드시트에 데이터 전송 완료.")
    else:
        print("전송할 데이터가 없습니다.")
except Exception as e:
    print("Google 스프레드시트 연결 오류:", e)

driver.quit()
