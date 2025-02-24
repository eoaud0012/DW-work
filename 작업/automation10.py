# import subprocess
# import time
# from pywinauto import Application, timings

# def check_login():
#     # 카카오워크 창이 나타날 때까지 대기
#     app = Application().connect(title='KakaoWork')
#     dlg = app.top_window()

#     # 로그인 상태 확인
#     if dlg.child_window(title="박종성", control_type="ListItem").exists():
#         return True
#     else:
#         return False

# def login(password):
#     # 이미 실행 중인 카카오워크가 있으면 연결, 없으면 실행
#     try:
#         app = Application().connect(title='KakaoWork')
#     except:
#         kakaowork_exe_path = r"C:\Users\DW-PC\AppData\Local\Programs\Kakao Enterprise\KakaoWork\KakaoWork.exe"
#         subprocess.Popen(kakaowork_exe_path)
#         time.sleep(5)  # 카카오워크가 실행되고 창이 나타날 때까지 대기
#         app = Application().connect(title='KakaoWork')

#     dlg = app.top_window()

#     # 로그인 상태 확인
#     if not check_login():
#         # 비밀번호 입력란에 비밀번호 입력
#         dlg["Edit2"].type_keys(password)  # 비밀번호 입력
#         dlg["Button"].click()  # 로그인 버튼 클릭

# def enter_chatroom():
#     # '박종성'과의 대화방 찾아서 들어가기
#     app = Application().connect(title='KakaoWork')
#     dlg = app.top_window()

#     dlg.child_window(title="박종성", control_type="ListItem").click_input(double=True)

# def start_kakaowork():
#     # 카카오워크 실행 파일 경로
#     kakaowork_exe_path = r"C:\Users\DW-PC\AppData\Local\Programs\Kakao Enterprise\KakaoWork\KakaoWork.exe"

#     # 카카오워크 실행
#     subprocess.Popen(kakaowork_exe_path)

# # 카카오워크 실행
# start_kakaowork()

# # 로그인 상태 확인
# if not check_login():
#     # 로그인
#     login("eoaoWkd1!")

# # '박종성'과의 대화방으로 이동
# enter_chatroom()



from pywinauto import Application

# 실행 중인 카카오워크 응용 프로그램에 연결
app = Application(backend="uia").connect(title="카카오워크")

# 컨트롤 구조 출력
app.window().print_control_identifiers()

