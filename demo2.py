from flask import Flask, request
import requests

app = Flask(__name__)

# Mặc định thông tin bot và chat ID
BOT1_TOKEN = '8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE'  # Bot 1 nhận tín hiệu LONG/SHORT
BOT2_TOKEN = '7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA'  # Bot 2 nhận tín hiệu 🥇🥈
CHAT_ID = '-4775219722'  # ID nhóm Telegram nhận tin nhắn

@app.route('/')
def index():
    return "App is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if request.is_json:
            data = request.get_json(force=True)
        else:
            data = {"message": request.data.decode('utf-8')}
        
        print("Received data:", data)
        message = data.get('message', 'No message received')

        # Xử lý từng loại tín hiệu
        if "🚀 LONG 🚀" in message or "🚨 SHORT 🚨" in message:
            send_message_to_telegram(BOT1_TOKEN, message)  # Bot 1 gửi LONG/SHORT

        elif "🥇" in message:
            send_message_to_telegram(BOT2_TOKEN, message)  # Bot 2 gửi Huân chương 1 (🥇)

        elif "🥈" in message:
            send_message_to_telegram(BOT2_TOKEN, message)  # Bot 2 gửi Huân chương 2 (🥈)

    except Exception as e:
        print("Error parsing JSON:", str(e))
        return "Invalid JSON", 400

    return "Webhook received", 200

def send_message_to_telegram(bot_token, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Message sent by {bot_token}:\n{message}")
    else:
        print(f"❌ Failed to send message: {response.text}")

if __name__ == '__main__':
    app.run(port=5000)
