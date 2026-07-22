#!/usr/bin/env python3
"""
Telegram Bot: ДОБИ (Debug Mode)
Navigation, Personal Contact, and Group Learning Mode
"""

import os
import sys
import logging
import json
from datetime import datetime
import requests
from typing import Optional, Dict, Any, List

# Configure logging to be very verbose
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8392695497:AAFxZaIBKwgKzurVdClFRGys1LGPCfwZ0H0')
TELEGRAM_API_URL = 'https://api.telegram.org'
OWNER_CONTACT = "@aslan_systems"
DB_FILE = "knowledge_base.json"

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.api_url = f"{TELEGRAM_API_URL}/bot{token}"
        self.offset = 0
        self.bot_info = self.get_me()
        self.bot_username = self.bot_info.get('username', '') if self.bot_info else 'DobbyBot'
        self.knowledge_base = self.load_kb()
        logger.info(f"🤖 Доби @{self.bot_username} готов к отладке!")

    def load_kb(self) -> Dict[str, str]:
        default_kb = {
            "модуль 1": "📍 <b>Модуль 1: Фундамент и стандарты сервиса</b>\nВ этом блоке мы разбираем базу: как создать стандарты, которые работают без вашего участия.",
            "модуль 2": "📍 <b>Модуль 2: Управление персоналом</b>\nНайм, адаптация и мотивация команды. Как сделать так, чтобы сотрудники горели делом.",
            "модуль 3": "📍 <b>Модуль 3: Финансовый учет</b>\nЦифры, KPI и аналитика. Учимся видеть реальную прибыль и управлять издержками.",
            "модуль 4": "📍 <b>Модуль 4: Маркетинг</b>\nПривлечение гостей и работа с лояльностью. Как сделать кафе популярным в городе.",
            "модуль 5": "📍 <b>Модуль 5: Масштабирование</b>\nДелегирование и подготовка к открытию новых точек.",
            "автор": f"👨‍💼 <b>Aslan Uzhakhov</b> — системный консультант.\nСвязаться лично: {OWNER_CONTACT}",
            "программа": "📚 <b>Программа «КОД УПРАВЛЕНИЯ»</b> — это 30 дней трансформации вашего бизнеса из хаоса в систему.",
            "связь": f"🤝 По всем вопросам пишите лично автору: {OWNER_CONTACT}",
            "оператор": f"📞 Для связи с оператором напишите: {OWNER_CONTACT}"
        }
        return default_kb

    def get_me(self) -> Dict[str, Any]:
        try:
            url = f"{self.api_url}/getMe"
            return requests.get(url, timeout=10).json().get('result', {})
        except: return {}

    def get_updates(self, timeout: int = 30) -> list:
        try:
            url = f"{self.api_url}/getUpdates"
            params = {'offset': self.offset, 'timeout': timeout}
            response = requests.get(url, params=params, timeout=timeout + 5)
            data = response.json()
            if not data.get('ok'):
                logger.error(f"Telegram API Error: {data.get('description')}")
                return []
            return data.get('result', [])
        except Exception as e:
            logger.error(f"Network Error: {e}")
            return []

    def send_message(self, chat_id: str, text: str, reply_to_id: Optional[int] = None):
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
            if reply_to_id: payload['reply_to_message_id'] = reply_to_id
            r = requests.post(url, json=payload, timeout=10)
            logger.info(f"📤 Sent to {chat_id}: {r.status_code}")
        except Exception as e:
            logger.error(f"Send Error: {e}")

    def handle_message(self, update: Dict[str, Any]):
        message = update.get('message', {})
        if not message:
            # Handle edited messages or other updates
            message = update.get('edited_message', {})
        
        chat = message.get('chat', {})
        chat_id = chat.get('id')
        chat_title = chat.get('title', 'Private')
        msg_id = message.get('message_id')
        text = message.get('text', '').strip()
        user = message.get('from', {})
        username = user.get('username', 'unknown')

        if not chat_id: return

        logger.info(f"📩 [{chat_title} ({chat_id})] {username}: {text[:50]}")

        # Learning Command
        if text.startswith('!запомнить') and username == 'aslan_systems':
            try:
                parts = text.replace('!запомнить', '').split('-', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    self.knowledge_base[key] = value
                    self.send_message(chat_id, f"✅ Доби запомнил тему <b>'{key}'</b>!", msg_id)
                    return
            except: pass

        text_lower = text.lower()
        
        # Identity Logic
        if "доби" in text_lower:
            if any(word in text_lower for word in ['привет', 'здравствуй', 'ку', 'хай']):
                self.send_message(chat_id, "Привет! Доби к вашим услугам! 😊 Чем могу помочь?", msg_id)
                return
            elif any(word in text_lower for word in ['спасибо', 'благодарю', 'красавчик', 'умница']):
                self.send_message(chat_id, "Всегда рад помочь! Доби счастлив быть полезным! ✨", msg_id)
                return

        # Navigation Logic
        found_responses = []
        for key, response in self.knowledge_base.items():
            if key in text_lower:
                found_responses.append(response)

        if found_responses:
            final_response = "\n\n---\n\n".join(list(set(found_responses)))
            self.send_message(chat_id, final_response, msg_id)

    def run(self):
        logger.info("🚀 Доби заступает на дежурство...")
        while True:
            try:
                updates = self.get_updates()
                for update in updates:
                    self.offset = update.get('update_id', 0) + 1
                    self.handle_message(update)
            except KeyboardInterrupt: break
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                import time
                time.sleep(5)

if __name__ == '__main__':
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()
