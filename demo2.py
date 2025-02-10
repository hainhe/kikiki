from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Thay thế bằng token của bot Telegram
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"

# Thay thế bằng ID nhóm hoặc người nhận tin nhắn
CHAT_ID1 = "-4775219722"
CHAT_ID2 = "-4775219722"

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()  # Lấy dữ liệu JSON nếu có
        
        if data is None:  # Nếu không có JSON, thử lấy từ form-data
            data = request.form.to_dict()

        if not data:
            return jsonify({"error": "No data received"}), 400

        alert_message = data.get("message", "")

        if "🚀 LONG 🚀" in alert_message:
            send_telegram_message(BOT1_TOKEN, CHAT_ID1, alert_message)
        elif "📢 Theo dõi nến" in alert_message:
            send_telegram_message(BOT2_TOKEN, CHAT_ID2, alert_message)

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
