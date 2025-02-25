# Python 3.10.11-slim 이미지를 베이스로 사용
FROM python:3.10.11-slim

# Chrome 실행에 필요한 패키지와 의존성 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libappindicator3-1 \
    libdbus-1-3 \
    libgconf-2-4 \
    libgtk-3-0 \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Google Chrome 설치
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Chromium-driver 설치 명령어를 제거 (Selenium Manager가 자동으로 드라이버를 관리함)

# Python 의존성 설치
RUN pip install --upgrade pip && \
    pip install python-dateutil beautifulsoup4 requests selenium pyperclip

# 작업 디렉토리 설정
WORKDIR /app

# 저장소의 모든 파일을 컨테이너로 복사
COPY . .

# 스크립트 실행 (예시: 작업/automation17-11.py)
CMD ["python", "작업/automation17-11.py"]
