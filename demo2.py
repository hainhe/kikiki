from flask import Flask, request, jsonify
import requests
import queue
import threading

app = Flask(__name__)

# Thông tin bot Telegram
BOT1_TOKEN = "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE"
BOT2_TOKEN = "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
CHAT_ID = "-4775219722"

# Hàng đợi tin nhắn
message_queue = queue.Queue()

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# Luồng xử lý tin nhắn từ hàng đợi
def process_queue():
    while True:
        bot_token, message = message_queue.get()  # Lấy tin nhắn từ hàng đợi
        send_telegram_message(bot_token, CHAT_ID, message)
        message_queue.task_done()

# Khởi động luồng xử lý (chạy trong nền)
threading.Thread(target=process_queue, daemon=True).start()

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Headers:", request.headers)
    print("Raw data:", request.data)
    
    try:
        alert_message = request.data.decode("utf-8").strip()
        if not alert_message:
            return jsonify({"error": "No message received"}), 400
    except Exception as e:
        return jsonify({"error": "Failed to read data", "details": str(e)}), 400
    
    # Thêm tin nhắn vào hàng đợi theo thứ tự mong muốn
    if "LONG" in alert_message or "SHORT" in alert_message:
        message_queue.put((BOT1_TOKEN, alert_message))
    
    if "🏅 Huân chương 1" in alert_message:
        message_queue.put((BOT2_TOKEN, "🏅 Huân chương 1"))
    
    if "🏅 Huân chương 2" in alert_message:
        message_queue.put((BOT2_TOKEN, "🏅 Huân chương 2"))

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
