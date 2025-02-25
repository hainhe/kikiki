from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

# API Key của APIFlash (thay bằng key thật của bạn)
APIFLASH_API_KEY = "314801dee3834f189467fee984cba673"

# Hàm gửi ảnh qua Telegram
def send_telegram_photo(bot_token, chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"❌ Error sending photo: {response.text}")

# Hàm gửi tin nhắn văn bản qua Telegram (dự phòng nếu không chụp được ảnh)
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

        # Phân tích thông điệp alert
        lines = alert_message.split("\n")
        signal = lines[0].split(": ")[1]  # "Long" hoặc "Short"
        chart_url = lines[1].split(": ")[1]  # URL biểu đồ

        # Chụp ảnh biểu đồ bằng APIFlash
        apiflash_url = f"https://api.apiflash.com/v1/urltoimage?access_key={APIFLASH_API_KEY}&url={chart_url}&format=png&width=1280&height=720"
        response = requests.get(apiflash_url)
        if response.status_code == 200:
            photo_url = response.url  # URL ảnh từ APIFlash
            print(f"✅ Screenshot captured: {photo_url}")
        else:
            photo_url = None
            print(f"❌ Error capturing screenshot: {response.status_code} - {response.text}")

        # Gửi tín hiệu Long qua BOT1
        if "Long" in signal:
            print(f"🚀 Sending LONG signal via BOT1")
            if photo_url:
                send_telegram_photo(BOT1_TOKEN, CHAT_ID, photo_url, alert_message)
            else:
                send_telegram_message(BOT1_TOKEN, CHAT_ID, f"{alert_message}\n(Ảnh không chụp được)")

        # Gửi tín hiệu Short qua BOT2
        if "Short" in signal:
            print(f"📉 Sending SHORT signal via BOT2")
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
