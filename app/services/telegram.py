import requests
import os

# TELEGRAM_BOT_TOKEN = os.getenv(
#     "TELEGRAM_BOT_TOKEN",
#     "PASTE_YOUR_TOKEN_HERE"
# )

def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot8134631262:AAHhYfsvsC0AvbLtJdkTSefBnL2Cc92I5C8/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
