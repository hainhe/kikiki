from flask import Flask, request, jsonify
import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

TRADINGVIEW_URL = "https://www.tradingview.com/chart/"  # Thay đổi link nếu cần

def send_telegram_message(bot_token, chat_id, message, image_path=None):
    """Gửi tin nhắn và ảnh (nếu có) đến Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

    if image_path:
        url_photo = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(image_path, "rb") as photo:
            requests.post(url_photo, data={"chat_id": chat_id}, files={"photo": photo})

def capture_chart(url, save_path="chart.png"):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920x1080")

        # Đường dẫn Chrome binary trên Render (sau khi cài đặt)
        chrome_binary = "/usr/bin/google-chrome"
        options.binary_location = chrome_binary

        # Sử dụng ChromeDriverManager để tự động tải ChromeDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(5)  # Tăng thời gian chờ để đảm bảo TradingView load xong
        driver.save_screenshot(save_path)
        driver.quit()
        return save_path
    except Exception as e:
        print(f"❌ Lỗi chụp màn hình: {e}")
        return None

@app.route("/", methods=["HEAD", "GET"])
def keep_alive():
    """Để Render không bị sleep"""
    print("🟢 UptimeRobot ping received! Keeping Render alive...")
    return "", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """Nhận alert từ TradingView, xử lý và gửi tin nhắn + ảnh đến Telegram"""
    print(f"📥 Headers: {request.headers}")
    print(f"📥 Raw data: {request.data}")

    try:
        alert_message = request.data.decode("utf-8").strip()
        if not alert_message:
            print("⚠️ Không có tin nhắn nhận được!")
            return jsonify({"error": "Không có tin nhắn"}), 400

        print(f"📥 Processed Message: {alert_message}")

        # Chụp màn hình TradingView
        image_path = capture_chart(TRADINGVIEW_URL)

        if "Long" in alert_message:
            print(f"🚀 Gửi tín hiệu LONG bằng BOT1")
            send_telegram_message(BOT1_TOKEN, CHAT_ID, alert_message, image_path)

        if "Short" in alert_message:
            print(f"📉 Gửi tín hiệu SHORT bằng BOT2")
            send_telegram_message(BOT2_TOKEN, CHAT_ID, alert_message, image_path)

    except Exception as e:
        print(f"❌ Lỗi xử lý webhook: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
