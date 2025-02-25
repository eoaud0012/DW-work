# Python 3.9-slim 이미지를 베이스로 사용
FROM python:3.9-slim

# Chrome 실행에 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome 설치
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Chrome 버전에 맞는 ChromeDriver 설치
# 예를 들어, Chrome 114 버전에 맞는 chromedriver를 설치 (Chrome 버전은 컨테이너 내에서 'google-chrome --version'으로 확인 가능)
ENV CHROMEDRIVER_VERSION 114.0.5735.90
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Python 의존성 설치
RUN pip install --upgrade pip && \
    pip install python-dateutil beautifulsoup4 requests selenium pyperclip

# 작업 디렉토리 설정
WORKDIR /app

# 저장소의 모든 파일을 컨테이너로 복사
COPY . .

# 스크립트 실행 (예시: 작업/automation17-11.py)
CMD ["python", "작업/automation17-11.py"]
