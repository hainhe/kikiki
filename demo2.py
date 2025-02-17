from flask import Flask, request, jsonify
import requests
import traceback
import re
import time
import os

# Thêm các thư viện để chụp ảnh màn hình với Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Thông tin bot Telegram của bạn
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

def send_telegram_message(bot_token, chat_id, message, image_path=None):
    """
    Gửi tin nhắn hoặc ảnh qua Telegram.
    Nếu image_path có tồn tại thì gửi ảnh kèm caption, nếu không thì gửi text message.
    """
    if image_path and os.path.exists(image_path):
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(image_path, "rb") as photo:
            data = {"chat_id": chat_id, "caption": message, "parse_mode": "Markdown"}
            files = {"photo": photo}
            requests.post(url, data=data, files=files)
    else:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

def extract_signal(alert_message):
    """
    Trích xuất tín hiệu từ alert.
    Giả sử alert có dạng:
    Signal: Long
    Chart URL: https://www.tradingview.com/chart/?symbol=...
    """
    if "Long" in alert_message or "long" in alert_message:
        return "LONG"
    elif "Short" in alert_message or "short" in alert_message:
        return "SHORT"
    else:
        return None

def extract_chart_url(alert_message):
    """
    Trích xuất URL chart từ alert.
    Sử dụng regex để tìm phần sau 'Chart URL:'.
    """
    match = re.search(r"Chart URL:\s*(\S+)", alert_message)
    if match:
        return match.group(1)
    return None

def capture_chart_screenshot(chart_url):
    """
    Sử dụng Selenium để mở URL chart và chụp ảnh màn hình.
    Chú ý: Trên Render, bạn cần đảm bảo có sẵn Chrome và chromedriver.
    """
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Nếu cần, bạn có thể chỉ định đường dẫn chromedriver:
    # driver = webdriver.Chrome(executable_path="/path/to/chromedriver", options=options)
    driver = webdriver.Chrome(options=options)
    
    driver.set_window_size(1280, 720)
    driver.get(chart_url)
    
    # Đợi trang tải (có thể tăng thời gian nếu cần)
    time.sleep(5)
    
    screenshot_path = "chart_screenshot.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()
    return screenshot_path

@app.route("/", methods=["HEAD", "GET"])
def keep_alive():
    print("🟢 UptimeRobot ping received! Keeping Render alive...")
    return "", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        alert_message = request.data.decode("utf-8").strip()
        print("Received alert:", alert_message)

        if not alert_message:
            return jsonify({"error": "No message received"}), 400

        # Trích xuất tín hiệu và URL chart từ alert
        signal = extract_signal(alert_message)
        chart_url = extract_chart_url(alert_message)

        print("Extracted signal:", signal)
        print("Extracted chart URL:", chart_url)

        image_path = None
        if chart_url:
            image_path = capture_chart_screenshot(chart_url)
            print("Captured image path:", image_path)

        # Gửi tin nhắn qua bot phù hợp
        if signal == "LONG":
            send_telegram_message(BOT1_TOKEN, CHAT_ID, alert_message, image_path)
        elif signal == "SHORT":
            send_telegram_message(BOT2_TOKEN, CHAT_ID, alert_message, image_path)
        else:
            return jsonify({"error": "Unknown signal type"}), 400

    except Exception as e:
        error_message = traceback.format_exc()
        print("Error in webhook:", error_message)
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
