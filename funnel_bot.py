
import logging
import os
import sqlite3
import requests
from datetime import datetime, timedelta

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("FUNNEL_TOKEN", "8954284939:AAFEK0kGrpuK7th5VUsM_uG7DU2AYv2YMoM")
API_URL = f"https://api.telegram.org/bot{TOKEN}"
SUBSCRIPTION_LINK = "https://t.me/tribute/app?startapp=ep_8xb4yfPbGCTBmvwOgElNJH3tWhUoMOST5JLSWs6aqm9e3GJpgk"

# Content
GREETING = "Привет! Я бот канала «Код Управления».\n\nЗдесь мы строим системы, которые работают без владельца. Хотите узнать, как выстроить такой бизнес?"
OFFER = f"Готовы начать трансформацию? Оформите подписку здесь: {SUBSCRIPTION_LINK}"

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Error sending message: {e}")

def handle_updates():
    offset = 0
    logger.info("Funnel Bot started...")
    
    while True:
        try:
            url = f"{API_URL}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            response = requests.get(url, params=params, timeout=35).json()
            
            if response.get("ok"):
                for update in response.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        message = update["message"]
                        text = message["text"].lower()
                        chat_id = message["chat"]["id"]
                        
                        if "/start" in text:
                            send_message(chat_id, GREETING)
                            send_message(chat_id, OFFER)
                            
        except Exception as e:
            logger.error(f"Error in Funnel loop: {e}")
            import time
            time.sleep(5)

if __name__ == "__main__":
    handle_updates()
