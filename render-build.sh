#!/bin/bash

# Cập nhật package index
apt-get update

# Cài đặt các phụ thuộc cần thiết
apt-get install -y wget unzip

# Cài đặt Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Cài đặt ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+' | head -1)
wget -N https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# Dọn dẹp file tạm
rm google-chrome-stable_current_amd64.deb chromedriver_linux64.zip
