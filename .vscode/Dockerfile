# Python 3.9-slim 이미지를 베이스로 사용
FROM python:3.9-slim

# 작업 디렉토리를 /app으로 설정
WORKDIR /app

# 저장소의 모든 파일을 컨테이너의 /app으로 복사
COPY . .

# pip를 최신 버전으로 업그레이드하고 필요한 패키지 설치
RUN pip install --upgrade pip && \
    pip install python-dateutil beautifulsoup4 requests selenium pyperclip

# 기본 실행 커맨드: 작업/automation17-10.py 실행
CMD ["python", "작업/automation17-11.py"]
