# Sử dụng image Python slim
FROM python:3.11-slim

# Cài đặt các gói cần thiết và Chrome
RUN apt-get update && apt-get install -y wget gnupg2 unzip curl \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# Cài đặt ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# Thiết lập thư mục làm việc
WORKDIR /app
COPY . /app

# Cài đặt các thư viện Python cần thiết
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Chạy ứng dụng qua gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
