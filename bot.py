#!/usr/bin/env python3
"""
Telegram Bot for КОД УПРАВЛЕНИЯ
Advanced Navigation, Personal Contact, and Group Learning Mode
"""

import os
import sys
import logging
import json
from datetime import datetime
import requests
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
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
        self.bot_username = self.bot_info.get('username', '') if self.bot_info else ''
        self.knowledge_base = self.load_kb()
        logger.info(f"🤖 Bot @{self.bot_username} initialized with {len(self.knowledge_base)} topics")

    def load_kb(self) -> Dict[str, str]:
        """Load knowledge base from file or return default"""
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
        
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading KB: {e}")
        return default_kb

    def save_kb(self):
        """Save knowledge base to file"""
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving KB: {e}")

    def get_me(self) -> Dict[str, Any]:
        try:
            url = f"{self.api_url}/getMe"
            return requests.get(url, timeout=10).json().get('result', {})
        except: return {}

    def get_updates(self, timeout: int = 30) -> list:
        try:
            url = f"{self.api_url}/getUpdates"
            params = {'offset': self.offset, 'timeout': timeout, 'allowed_updates': ['message']}
            data = requests.get(url, params=params, timeout=timeout + 5).json()
            return data.get('result', []) if data.get('ok') else []
        except: return []

    def send_message(self, chat_id: str, text: str, reply_to_id: Optional[int] = None):
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
            if reply_to_id: payload['reply_to_message_id'] = reply_to_id
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Send error: {e}")

    def handle_message(self, update: Dict[str, Any]):
        message = update.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        msg_id = message.get('message_id')
        text = message.get('text', '').strip()
        user = message.get('from', {})
        username = user.get('username', '')

        if not text: return

        # 1. Learning Command: !запомнить [ключ] - [значение]
        if text.startswith('!запомнить') and username == 'aslan_systems':
            try:
                parts = text.replace('!запомнить', '').split('-', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    self.knowledge_base[key] = value
                    self.save_kb()
                    self.send_message(chat_id, f"✅ Тема <b>'{key}'</b> успешно сохранена в базу навигации!", msg_id)
                    return
            except Exception as e:
                logger.error(f"Learning error: {e}")

        # 2. Navigation Logic
        text_lower = text.lower()
        found_responses = []
        
        for key, response in self.knowledge_base.items():
            if key in text_lower:
                found_responses.append(response)

        if found_responses:
            # Combine unique responses
            final_response = "\n\n---\n\n".join(list(set(found_responses)))
            self.send_message(chat_id, final_response, msg_id)
            logger.info(f"📍 Navigation trigger for: {text[:30]}")
        
        # 3. Help trigger
        elif any(word in text_lower for word in ['помощь', 'связь', 'вопрос', 'админ']):
            help_text = f"🤝 Нужна помощь? По всем вопросам навигации и обучения пишите лично: {OWNER_CONTACT}"
            self.send_message(chat_id, help_text, msg_id)

    def run(self):
        logger.info("🚀 Bot is running in Navigation & Learning mode...")
        while True:
            try:
                updates = self.get_updates()
                for update in updates:
                    self.offset = update.get('update_id', 0) + 1
                    if 'message' in update:
                        self.handle_message(update)
            except KeyboardInterrupt: break
            except Exception as e:
                logger.error(f"Loop error: {e}")
                import time
                time.sleep(5)

if __name__ == '__main__':
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()
