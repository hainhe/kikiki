from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    
    print(f"Sending message to Telegram: {payload}")  # Debug log
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        print(f"⚠️ Telegram Error: {response.status_code}, {response.text}")  # Log lỗi
    else:
        print(f"✅ Message sent successfully: {response.text}")

@app.route("/", methods=["HEAD", "GET"])
def keep_alive():
    print("🟢 UptimeRobot ping received! Keeping Render alive...")
    return "", 200
    
@app.route("/webhook", methods=["POST"])
def webhook():
    print("📥 Webhook received raw data:", request.data)  # In dữ liệu thô
    print("📜 Decoded data:", request.data.decode("utf-8", errors="ignore"))  # In dữ liệu sau khi decode
    
    try:
        alert_message = request.data.decode("utf-8", errors="ignore").strip()
        if not alert_message:
            return jsonify({"error": "No message received"}), 400
    except Exception as e:
        return jsonify({"error": "Failed to read data", "details": str(e)}), 400
    
    print(f"📩 Processed message: {alert_message}")

    if "LONG" in alert_message:
        print("🚀 Sending LONG signal to Telegram")
        send_telegram_message(BOT1_TOKEN, CHAT_ID, alert_message)
    
    if "SHORT" in alert_message:
        print("🚀 Sending SHORT signal to Telegram")
        send_telegram_message(BOT2_TOKEN, CHAT_ID, alert_message)
    
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




# from flask import Flask, request, jsonify
# import requests
# import time

# app = Flask(__name__)

# # Thông tin bot Telegram
# BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
# BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
# CHAT_ID = "-4775219722"

# def send_telegram_message(bot_token, chat_id, message):
#     url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
#     payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
#     requests.post(url, json=payload)

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     print("Headers:", request.headers)
#     print("Raw data:", request.data)
    
#     try:
#         alert_message = request.data.decode("utf-8").strip()  # Đọc dữ liệu thô
#         if not alert_message:
#             return jsonify({"error": "No message received"}), 400
#     except Exception as e:
#         return jsonify({"error": "Failed to read data", "details": str(e)}), 400
    
#     # Xử lý và gửi tin nhắn theo thứ tự mong muốn
#     if "LONG" in alert_message or "SHORT" in alert_message:
#         send_telegram_message(BOT1_TOKEN, CHAT_ID, alert_message)
#         time.sleep(1)  # Chờ để đảm bảo thứ tự gửi đúng
    
#     if "📢 Theo dõi" in alert_message:
#         send_telegram_message(BOT2_TOKEN, CHAT_ID, alert_message)
#         time.sleep(1)  
    
#     return jsonify({"status": "ok"})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
