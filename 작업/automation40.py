from playwright.sync_api import sync_playwright
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def run(playwright):
    # 브라우저 실행 (headless 모드)
    browser = playwright.chromium.launch(headless=True)
    # 최대화 대신 넓은 viewport 설정 (원하는 해상도로 조정 가능)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # 1. ITSM 로그인 페이지 접속
    page.goto("https://dwdesk.dongwon.com/xefc/egene/login_dw.jsp")

    # 2. 로그인 처리
    USERNAME = "eoaud0012"
    page.wait_for_selector("input[name='emp_id']")
    page.fill("input[name='emp_id']", USERNAME)
    page.wait_for_selector("input[type='submit'][value='로그인']")
    page.click("input[type='submit'][value='로그인']")

    # 로그인 후 페이지 로딩 대기 (60초)
    time.sleep(60)

    # 3. PMS 메뉴 선택
    page.wait_for_selector("xpath=//span[contains(text(), 'PMS')]", timeout=10000)
    page.click("xpath=//span[contains(text(), 'PMS')]")

    # 4. 프로젝트 이력 메뉴 선택
    page.wait_for_selector("xpath=//span[contains(text(), '프로젝트 이력')]", timeout=10000)
    page.click("xpath=//span[contains(text(), '프로젝트 이력')]")
    time.sleep(10)

    # 5. 기준일 수정
    # 첫번째 날짜 입력 (예: "20000101")
    first_date = "20000101"
    first_date_selector = "xpath=(//input[contains(@class, 'hasDatepicker')])[1]"
    page.wait_for_selector(first_date_selector)
    page.click(first_date_selector)
    page.fill(first_date_selector, "")
    time.sleep(0.5)
    # 각 문자별로 입력 (delay=100ms로 타이핑)
    page.type(first_date_selector, first_date, delay=100)
    # body 클릭하여 blur 이벤트 발생
    page.click("body")
    time.sleep(1)

    # 두번째 날짜 입력 (예: "21001231")
    second_date = "21001231"
    second_date_selector = "xpath=(//input[contains(@class, 'hasDatepicker')])[2]"
    page.wait_for_selector(second_date_selector)
    page.click(second_date_selector)
    page.fill(second_date_selector, "")
    time.sleep(0.5)
    page.type(second_date_selector, second_date, delay=100)
    page.click("body")
    time.sleep(5)

    # 달력 아이콘 클릭
    calendar_icon_xpath = "xpath=//div[@class='atom-group-prepend' and contains(@onclick, 'openCalendar')]"
    page.wait_for_selector(calendar_icon_xpath)
    page.click(calendar_icon_xpath)
    time.sleep(2)

    # 달력 UI에서 "1" 일 선택
    day_button_xpath = "xpath=//a[normalize-space(text())='1']"
    page.wait_for_selector(day_button_xpath)
    page.click(day_button_xpath)
    time.sleep(2)

    # 5-1. '조회' 버튼 클릭
    search_button_xpath = "xpath=//button[@title='조회']"
    page.wait_for_selector(search_button_xpath)
    page.click(search_button_xpath)
    time.sleep(10)

    # 6. 한 페이지당 노출 개수를 20으로 변경
    arrow_down_selector = "div.jqx-icon-arrow-down.jqx-icon"
    page.wait_for_selector(arrow_down_selector)
    # 요소가 화면에 보이도록 스크롤
    page.evaluate("element => element.scrollIntoView()", page.query_selector(arrow_down_selector))
    page.click(arrow_down_selector)
    time.sleep(2)
    option_20_xpath = "xpath=//span[normalize-space(text())='20']"
    page.wait_for_selector(option_20_xpath)
    page.click(option_20_xpath)
    time.sleep(3)

    # 6-1. 웹페이지 배율을 90%로 변경
    page.evaluate("document.body.style.zoom='90%'")
    time.sleep(1)

    # 7. 페이지네이션을 이용하여 전체 데이터 로드
    project_data = []
    current_page = 1

    while True:
        container_selector = "div.jqx-grid-content > div[id^='contenttable']"
        page.wait_for_selector(container_selector)
        time.sleep(2)  # 페이지 전환 후 데이터 로드 대기

        # 그리드 내 모든 행 선택
        rows = page.query_selector_all(f"{container_selector} div[role='row']")
        new_rows_this_page = 0
        for row in rows:
            cells = row.query_selector_all("div[role='gridcell']")
            if len(cells) >= 8:
                # 각 셀의 텍스트를 리스트로 추출
                cell_texts = [cell.inner_text().strip() for cell in cells[:8]]
                if cell_texts[1] != "":
                    project_data.append(cell_texts)
                    new_rows_this_page += 1

        # 새 데이터 행이 20개 미만이면 마지막 페이지로 판단
        if new_rows_this_page < 20:
            break

        # 다음 페이지로 전환 (페이지 번호 입력 후 엔터)
        current_page += 1
        page_input_selector = "input.jqx-input.jqx-widget-content.jqx-grid-pager-input.jqx-rc-all"
        page.wait_for_selector(page_input_selector)
        page.fill(page_input_selector, "")
        page.fill(page_input_selector, str(current_page))
        page.keyboard.press("Enter")
        time.sleep(3)

    print("페이지네이션 완료: 전체 데이터 로드됨.")
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
        sheet.update("B2:I2", headers)
        if project_data:
            start_row = 3
            end_row = start_row + len(project_data) - 1
            cell_range = f"B{start_row}:I{end_row}"
            sheet.update(cell_range, project_data)
            print("Google 스프레드시트에 데이터 전송 완료.")
        else:
            print("전송할 데이터가 없습니다.")
    except Exception as e:
        print("Google 스프레드시트 연결 오류:", e)

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
