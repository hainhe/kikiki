import re
from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

# API Key của Chart-Img
CHART_IMG_API_KEY = "8RLLVdMVMl7MQ9SuxhU0O5cONpyTGPba1BLbaiYG"

# Hàm gửi ảnh qua Telegram
def send_telegram_photo(bot_token, chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"❌ Error sending photo: {response.text}")

# Hàm gửi tin nhắn văn bản qua Telegram
def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route("/", methods=["HEAD", "GET"])
def keep_alive():
    print("🟢 UptimeRobot ping received! Keeping Render alive...")
    return "", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    print(f"📥 Headers: {request.headers}")
    print(f"📥 Raw data: {request.data}")

    try:
        alert_message = request.data.decode("utf-8").strip()
        if not alert_message:
            print("⚠️ No message received!")
            return jsonify({"error": "No message received"}), 400

        print(f"📥 Processed Message: {alert_message}")

        # Trích xuất symbol
        match = re.search(r'🌜(.*?)🌛', alert_message)
        symbol = match.group(1) if match else "Unknown"

        # Trích xuất dấu thời gian từ thông điệp
        time_match = re.search(r'Time: (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', alert_message)
        if time_match:
            signal_time = datetime.strptime(time_match.group(1), "%Y-%m-%d %H:%M")
            end_time = int(signal_time.timestamp() * 1000)  # Chuyển sang milliseconds
        else:
            end_time = int(datetime.now().timestamp() * 1000)  # Dùng thời gian hiện tại nếu không có

        # Tạo URL chụp ảnh chart với Chart-Img, bao gồm end_time
        chart_img_url = (f"https://api.chart-img.com/v1/tradingview/advanced-chart?"
                         f"key={CHART_IMG_API_KEY}&symbol={symbol}&interval=1m&theme=dark&end_time={end_time}")

        response = requests.get(chart_img_url)
        if response.status_code == 200:
            photo_url = response.url
            print(f"✅ Screenshot captured: {photo_url}")
        else:
            photo_url = None
            print(f"❌ Error capturing screenshot: {response.status_code} - {response.text}")

        # Xác định bot dựa trên tín hiệu
        if "LONG" in alert_message:
            print("🚀 Sending LONG signal via BOT1")
            if photo_url:
                send_telegram_photo(BOT1_TOKEN, CHAT_ID, photo_url, alert_message)
            else:
                send_telegram_message(BOT1_TOKEN, CHAT_ID, f"{alert_message}\n(Ảnh không chụp được)")
        elif "SHORT" in alert_message:
            print("📉 Sending SHORT signal via BOT2")
            if photo_url:
                send_telegram_photo(BOT2_TOKEN, CHAT_ID, photo_url, alert_message)
            else:
                send_telegram_message(BOT2_TOKEN, CHAT_ID, f"{alert_message}\n(Ảnh không chụp được)")

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
