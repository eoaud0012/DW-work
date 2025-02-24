import datetime

# 주어진 문자열 데이터
date_str = '2023-02-21 15:54'

# 문자열을 datetime 객체로 변환
date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M')

# 연도, 월, 일, 시, 분 추출
year = str(date_obj.year)[2:]
if(int(date_obj.month) > 9):
    month = str(date_obj.month)
else:
    month = '0' + str(date_obj.month)
day = str(date_obj.day)
hour = date_obj.hour
minute = date_obj.minute

# 결과 출력
# print(year, month, day, hour, minute)
print(year+month+day+'-'+'01')