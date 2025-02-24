import mysql.connector
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --------------------------------------
# 1. MariaDB 연결 및 데이터 조회
# --------------------------------------
db_config = {
    'host': '172.20.13.41',         # MariaDB 호스트
    'port': 3306,                   # MariaDB 포트
    'user': 'egene61',              # 사용자명
    'password': 'e61?gus12#$',      # 비밀번호
    'database': 'egene61'           # 데이터베이스명
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

query = """
SELECT 
    e.PMS_ID,                -- PMS ID
    e.PMS_COD_ID3,           -- 프로젝트 코드
    e.PMS_REQ_TITLE,         -- 프로젝트명
    org.ORG_NAME AS 계열사,  -- 계열사명 (ecf_org의 org_name)
    e.PMS_COST,              -- 투자비
    emp.emp_name AS 임직원명, -- PM의 그룹웨어 이름 (ecf_employee의 emp_name)
    e.PMS_ACTSTART_DTTM,     -- 프로젝트 시작일
    e.PMS_ACTFINISH_DTTM,    -- 프로젝트 완료일
    e.PMS_PST_CNT_GRD,       -- 기능 확보 점수
    e.PMS_PST_CNT,           -- 기능수
    e.PMS_IN_PST_CNT,        -- 일정 준수 기능 수
    e.PMS_CUS_SAT_GRD,       -- 고객평가 점수
    e.PMS_PST_GRD,           -- 기능평가 점수
    e.PMS_QUAL_GRD,          -- 품질 점수
    e.PMS_RES_GRD,           -- 적기 대응 점수
    e.PMS_PLAN1_DTTM,        -- 분석/설계 목표일
    e.PMS_PLAN1_FIN_DTTM,    -- 분석/설계 완료일
    e.PMS_PLAN2_DTTM,        -- 개발 완료 목표일
    e.PMS_PLAN2_FIN_DTTM,    -- 개발 완료일
    e.PMS_PLAN3_DTTM,        -- 오픈 목표일
    e.PMS_ACT6_DTTM          -- 오픈 완료일
FROM eso_pms e
LEFT JOIN ecf_org org ON e.PMS_CUSTOMER = org.ORG_ID
LEFT JOIN ecf_employee emp ON e.PMS_ITPM_EMP_ID = emp.emp_id
WHERE e.PMS_ID IN (
    SELECT PMS_ID
    FROM eso_pms
    WHERE PMS_REQ_TITLE NOT LIKE 'CM%'
)
"""

cursor.execute(query)
data = cursor.fetchall()
cursor.close()
conn.close()

# --------------------------------------
# 2. DB 데이터 전처리: 각 셀을 문자열로 변환하고,
#    타임스탬프(길이 14인 문자열)는 'YYYY-MM-DD' 형식으로 변경,
#    데이터가 없으면 '-'로 대체
#
# 타임스탬프 변환이 필요한 인덱스: 6, 7, 15, 16, 17, 18, 19, 20
# --------------------------------------
timestamp_indices = [6, 7, 15, 16, 17, 18, 19, 20]
processed_data = []
for row in data:
    new_row = []
    for idx, cell in enumerate(row):
        cell_str = str(cell) if cell is not None else ""
        if idx in timestamp_indices and cell_str and len(cell_str) == 14:
            try:
                dt = datetime.strptime(cell_str, "%Y%m%d%H%M%S")
                cell_str = dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        if not cell_str:
            cell_str = "-"
        new_row.append(cell_str)
    processed_data.append(new_row)

# --------------------------------------
# 3. Google 스프레드시트 API 인증 및 "파이썬2" 워크시트 지정
# --------------------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("demianlee-a5dec966352c.json", scope)
client = gspread.authorize(creds)

spreadsheet_name = "★ [PMS] DT본부 프로젝트 평가_250217_평가방식개선_배포용"
sheet = client.open(spreadsheet_name).worksheet("PMS 진척 상황 조회(DB)")
sheet.clear()

# --------------------------------------
# 4. 구글 시트에 데이터 업데이트 (B2부터 헤더, B3부터 데이터)
# --------------------------------------
def col_num_to_letter(n):
    """1-indexed 열 번호를 열 문자(A, B, C, …)로 변환"""
    result = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

# SQL 쿼리에서 조회한 21개 컬럼에 맞춘 헤더 설정
headers = [
    "PMS ID",
    "프로젝트코드",
    "프로젝트명",
    "계열사",
    "투자비",
    "PM",
    "프로젝트 시작일",
    "프로젝트 완료일",
    "기능 확보 점수",
    "기능수",
    "일정 준수 기능 수",
    "고객평가 점수",
    "기능평가 점수",
    "품질 점수",
    "적기 대응 점수",
    "분석/설계 목표일",
    "분석/설계 완료일",
    "개발 완료 목표일",
    "개발 완료일",
    "오픈 목표일",
    "오픈 완료일"
]

start_col_letter = "B"
num_columns = len(headers)
end_col_index = 2 + num_columns - 1  # 시작열(B:2)부터 num_columns 만큼
end_col_letter = col_num_to_letter(end_col_index)

# 헤더 업데이트 (예: B2:V2)
header_range = f"{start_col_letter}2:{end_col_letter}2"
sheet.update(header_range, [headers])

# 데이터 업데이트 (B3부터 기록)
if processed_data:
    data_start_row = 3
    data_end_row = data_start_row + len(processed_data) - 1
    data_range = f"{start_col_letter}{data_start_row}:{end_col_letter}{data_end_row}"
    sheet.update(data_range, processed_data)

print("MariaDB 데이터가 성공적으로 Google 스프레드시트 'PMS 진척 상황 조회(DB)' 시트에 업데이트되었습니다!")
