from flask import Flask, request, jsonify
import requests
import time
import os
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re

app = Flask(__name__)

# Telegram Bot Tokens
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

# Cấu hình Chrome cho Selenium
CHROME_PATH = "/usr/bin/google-chrome-stable"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = CHROME_PATH  # Chỉ định Chrome Portable

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)


def send_telegram_message(bot_token, chat_id, message, image_path=None):
    """Gửi tin nhắn và ảnh (nếu có) đến Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

    if image_path:
        url_photo = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(image_path, "rb") as photo:
            requests.post(url_photo, data={"chat_id": chat_id}, files={"photo": photo})


def capture_chart_screenshot(chart_url):
    """Chụp màn hình biểu đồ từ TradingView"""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(chart_url)
        time.sleep(5)  # Đợi trang load xong
        image_path = "chart_screenshot.png"
        driver.save_screenshot(image_path)
        return image_path
    finally:
        driver.quit()


def extract_signal(message):
    """Lấy loại tín hiệu từ thông báo"""
    if "Long" in message:
        return "LONG"
    elif "Short" in message:
        return "SHORT"
    return None


def extract_chart_url(message):
    """Trích xuất URL biểu đồ từ TradingView"""
    match = re.search(r"Chart URL: (https://www\.tradingview\.com/chart/[^ ]+)", message)
    return match.group(1) if match else None


@app.route("/", methods=["HEAD", "GET"])
def keep_alive():
    return "", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """Nhận tín hiệu từ TradingView và xử lý"""
    try:
        alert_message = request.data.decode("utf-8").strip()
        if not alert_message:
            return jsonify({"error": "No message received"}), 400

        print(f"📩 Received Alert: {alert_message}")

        signal = extract_signal(alert_message)
        chart_url = extract_chart_url(alert_message)

        print(f"🔍 Extracted Signal: {signal}")
        print(f"🔗 Extracted Chart URL: {chart_url}")

        image_path = None
        if chart_url:
            image_path = capture_chart_screenshot(chart_url)
            print(f"📸 Captured Screenshot: {image_path}")

        if signal == "LONG":
            send_telegram_message(BOT1_TOKEN, CHAT_ID, alert_message, image_path)
        elif signal == "SHORT":
            send_telegram_message(BOT2_TOKEN, CHAT_ID, alert_message, image_path)
        else:
            return jsonify({"error": "Unknown signal type"}), 400

    except Exception as e:
        error_message = traceback.format_exc()
        print(f"❌ Error in webhook: {error_message}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
