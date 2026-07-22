
import logging
import os
import sqlite3
import requests
from datetime import datetime

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("DOBBY_TOKEN", "8392695497:AAFxZaIBKwgKzurVdClFRGys1LGPCfwZ0H0")
API_URL = f"https://api.telegram.org/bot{TOKEN}"
ADMIN_USERNAME = "aslan_systems"
GROUP_CHAT_ID = -1002381005898

# Knowledge Base (Modules)
KNOWLEDGE_BASE = {
    "модуль 1": "<b>Модуль 1: Фундамент Системы</b>\nКак перестать тушить пожары и начать строить систему, которая работает без вас.",
    "модуль 2": "<b>Модуль 2: Команда и Делегирование</b>\nКак подбирать людей и ставить задачи так, чтобы их не нужно было переделывать.",
    "модуль 3": "<b>Модуль 3: Финансы и Прибыль</b>\nКак выстроить финансовую систему и наконец увидеть реальные деньги в бизнесе.",
    "автор": "Автор проекта — <b>Аслан Ужахов</b>. 15 лет опыта в управлении и бизнесе.",
    "связь": "Для связи с Асланом пишите в личку: @aslan_systems",
    "помощь": "Я Доби! Я помогу тебе с навигацией. Просто напиши номер модуля или спроси о программе."
}

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Error sending message: {e}")

def handle_updates():
    offset = 0
    logger.info("Dobby Bot started...")
    
    # Send welcome message on start
    send_message(GROUP_CHAT_ID, "Всем привет! Я Доби! 🫡\nЯ ваш системный ассистент. Я помогу вам с навигацией по модулям и отвечу на вопросы.\nПросто напишите 'Доби' или номер модуля!")

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
                        
                        # Logic for Dobby
                        response_text = None
                        if "доби" in text:
                            response_text = "Я здесь! Чем могу помочь? 😊"
                        
                        for key, val in KNOWLEDGE_BASE.items():
                            if key in text:
                                response_text = val
                                break
                        
                        if "связь" in text or "автор" in text:
                            response_text = KNOWLEDGE_BASE["связь"]
                            
                        if response_text:
                            send_message(chat_id, response_text)
                            
        except Exception as e:
            logger.error(f"Error in Dobby loop: {e}")
            import time
            time.sleep(5)

if __name__ == "__main__":
    handle_updates()
