#!/bin/bash
echo "🔹 Cài đặt Chrome cho môi trường Render..."

# Tải Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
if [ $? -ne 0 ]; then
  echo "❌ Lỗi: Không tải được Chrome."
  exit 1
fi

# Cập nhật package index
apt-get update
if [ $? -ne 0 ]; then
  echo "❌ Lỗi: Không cập nhật được package index."
  exit 1
fi

# Cài đặt Chrome
apt-get install -y ./google-chrome-stable_current_amd64.deb
if [ $? -ne 0 ]; then
  echo "❌ Lỗi: Không cài đặt được Chrome."
  exit 1
fi

# Xóa file .deb
rm google-chrome-stable_current_amd64.deb
echo "✅ Chrome đã được cài đặt thành công!"

# Kiểm tra phiên bản Chrome
google-chrome --version
