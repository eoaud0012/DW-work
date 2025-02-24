import time
from random import randint 
from SRT import SRT
from SRT import SeatType
import asyncio
import telegram_module

TELEGRAM_TOKEN = "6041435620:AAH-C98ovxjuHmKOFbDM7z-Y8lI88YK1UT4"
TELEGRAM_CHATID = "6055095538"

srt = SRT("2287599141", "eoaoWkd1!") #
dep = '대전'
arr = '수서'
date = '20250302' # 날짜 (yyyymmdd)
tr_time = '210000' # 시간 (HHMMSS)

# 기차 검색
trains = srt.search_train(dep, arr, date, tr_time, available_only=False)
# 매진이야

print(*trains, sep='\n')
# 결과 :  [[SRT] 11월 06일, 수서~부산(20:00~22:23) 특실 매진, 일반실 .....
train_num = input("몇 번째 기차를 예매하시겠어요?(0번부터 시작)")
train_num = int(train_num)


flag = False
i = 0

# 루프 시작
while flag == False:
    # 예약가능이됏어
    try:
        i += 1
        trains = srt.search_train(dep, arr, date, tr_time, available_only=False)
        time.sleep(randint(1, 3))
        print(f"{i}번째 시도")
        reservation = srt.reserve(trains[train_num], special_seat=SeatType.GENERAL_ONLY)
        print(reservation)
        str_reservation = str(reservation)
        asyncio.run(telegram_module.bot.send_message(chat_id = TELEGRAM_CHATID, text=f"[SRT] 예약 완료!\n{reservation}"))
        flag = True
        
    except:
        pass
        
# 결과 : [SRT] 11월 06일, 수서~부산(22:40~01:07) 52400원(1석), 구입기한 11월 06일 22:36