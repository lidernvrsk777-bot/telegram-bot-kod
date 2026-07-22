import logging
import os
import requests
import time

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("DOBBY_TOKEN", "8392695497:AAFxZaIBKwgKzurVdClFRGys1LGPCfwZ0H0")
API_URL = f"https://api.telegram.org/bot{TOKEN}"
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
    logger.info("Dobby Bot (Enhanced) started...")
    
    # Send welcome message on start
    send_message(GROUP_CHAT_ID, "Доби на связи! 🫡\nЯ обновил свои алгоритмы и теперь слышу вас лучше. Спрашивайте про модули или пишите 'Доби'!")

    while True:
        try:
            url = f"{API_URL}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            response = requests.get(url, params=params, timeout=35).json()
            
            if response.get("ok"):
                for update in response.get("result", []):
                    offset = update["update_id"] + 1
                    
                    # Handle both private and group messages
                    message = update.get("message") or update.get("channel_post")
                    if message and "text" in message:
                        text = message["text"].lower()
                        chat_id = message["chat"]["id"]
                        logger.info(f"Received message in {chat_id}: {text}")
                        
                        response_text = None
                        
                        # Check keywords
                        if "доби" in text:
                            response_text = "Я здесь! Чем могу помочь? 😊"
                        
                        for key, val in KNOWLEDGE_BASE.items():
                            if key in text:
                                response_text = val
                                break
                        
                        if "связь" in text or "автор" in text or "аслан" in text:
                            response_text = KNOWLEDGE_BASE["связь"]
                            
                        if response_text:
                            send_message(chat_id, response_text)
                            
        except Exception as e:
            logger.error(f"Error in Dobby loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    handle_updates()
