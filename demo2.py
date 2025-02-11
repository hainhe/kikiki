from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    print(f"Sent message: {message}, Status Code: {response.status_code}")  # Log kết quả gửi

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Headers:", request.headers)
    print("Raw data:", request.data)
    
    try:
        alert_message = request.data.decode("utf-8").strip()  # Đọc dữ liệu thô
        if not alert_message:
            return jsonify({"error": "No message received"}), 400
    except Exception as e:
        return jsonify({"error": "Failed to read data", "details": str(e)}), 400
    
    messages_to_send = []

    # Xử lý theo thứ tự mong muốn
    if "LONG" in alert_message or "SHORT" in alert_message:
        messages_to_send.append((BOT1_TOKEN, alert_message))
    
    if "🏅" in alert_message:
        messages_to_send.append((BOT2_TOKEN, alert_message))
    
    if "🥈" in alert_message:
        messages_to_send.append((BOT2_TOKEN, alert_message))

    # Gửi tin nhắn theo đúng thứ tự
    for bot_token, message in messages_to_send:
        send_telegram_message(bot_token, CHAT_ID, message)
        time.sleep(1)  # Chờ 1 giây để tránh giới hạn tốc độ

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
