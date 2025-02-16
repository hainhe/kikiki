from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKENS = {
    "LONG": "8082939784:AAEDPeIDJN7VL3RT9D2UhMHfGP2P0n9hwHE",
    "SHORT": "7875194079:AAFcRGt2FN8ahpn1O-TY3rpS5fs3UF94dWA"
}
CHAT_ID = "-4775219722"

def send_telegram_message(bot_token, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    print(f"📤 Sent: {response.status_code}, {response.text}")

@app.route("/", methods=["GET", "HEAD"])
def keep_alive():
    return "", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    message = request.data.decode("utf-8", errors="ignore").strip()
    print(f"📥 Received: {message}")
    
    for key, token in BOT_TOKENS.items():
        if key in message.upper():
            print(f"🚀 Sending {key} signal")
            send_telegram_message(token, message)
            break
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
