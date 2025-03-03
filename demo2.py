import re
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

# API Key của Screenshot Machine (thay bằng key của bạn)
SCREENSHOT_MACHINE_API_KEY = "a07c8a"

def send_telegram_photo(bot_token, chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"❌ Error sending photo: {response.text}")

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route("/", methods=["HEAD", "GET"])
def keep_alive():
    print("🟢 UptimeRobot ping received!")
    return "", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    print(f"📥 Raw data: {request.data}")
    try:
        alert_message = request.data.decode("utf-8").strip()
        if not alert_message:
            print("⚠️ No message!")
            return jsonify({"error": "No message received"}), 400

        print(f"📥 Message: {alert_message}")

        # Trích xuất thông tin
        chart_match = re.search(r'Chart: (https://www\.tradingview\.com/chart/\?symbol=.*)', alert_message)
        chart_url = chart_match.group(1) if chart_match else None

        timeframe_match = re.search(r'Timeframe: (.*)', alert_message)
        timeframe = timeframe_match.group(1) if timeframe_match else "Unknown"

        # Chụp ảnh bằng Screenshot Machine
        if chart_url:
            screenshot_api_url = f"https://api.screenshotmachine.com/?key={SCREENSHOT_MACHINE_API_KEY}&url={chart_url}&dimension=800x600"
            response = requests.get(screenshot_api_url)
            if response.status_code == 200:
                photo_url = response.url
                print(f"✅ Screenshot captured: {photo_url}")
            else:
                photo_url = None
                print(f"❌ Screenshot error: {response.status_code} - {response.text}")
        else:
            photo_url = None
            print("❌ No chart URL found")

        # Tạo thông điệp với định dạng đẹp hơn
        formatted_message = f"**{alert_message.split('Signal: ')[1].split('\n')[0]}**\n" \
                            f"🌜{syminfo.ticker}🌛\n" \
                            f"Timeframe: {timeframe}\n" \
                            f"{alert_message.split('Time: ')[1]}"

        # Gửi tín hiệu và ảnh
        if "LONG" in alert_message:
            print("🚀 Sending LONG via BOT1")
            if photo_url:
                send_telegram_photo(BOT1_TOKEN, CHAT_ID, photo_url, formatted_message)
            else:
                send_telegram_message(BOT1_TOKEN, CHAT_ID, f"{formatted_message}\n(Ảnh không chụp được)")
        elif "SHORT" in alert_message:
            print("📉 Sending SHORT via BOT2")
            if photo_url:
                send_telegram_photo(BOT2_TOKEN, CHAT_ID, photo_url, formatted_message)
            else:
                send_telegram_message(BOT2_TOKEN, CHAT_ID, f"{formatted_message}\n(Ảnh không chụp được)")

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
