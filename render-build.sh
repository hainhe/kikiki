#!/bin/bash
echo "🔹 Cài đặt Chrome cho môi trường Render..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update
apt-get install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
echo "✅ Chrome đã được cài đặt thành công!"
