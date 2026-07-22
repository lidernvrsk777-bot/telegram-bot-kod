#!/usr/bin/env python3
"""
Telegram Bot for КОД УПРАВЛЕНИЯ
Optimized for Group chats and Instant responses
Works without external AI for maximum reliability
"""

import os
import sys
import logging
from datetime import datetime
import requests
from typing import Optional, Dict, Any

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
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '7423566451')
TELEGRAM_API_URL = 'https://api.telegram.org'

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.api_url = f"{TELEGRAM_API_URL}/bot{token}"
        self.offset = 0
        self.bot_info = self.get_me()
        self.bot_username = self.bot_info.get('username', '') if self.bot_info else ''
        logger.info(f"🤖 Telegram Bot initialized as @{self.bot_username}")

    def get_me(self) -> Dict[str, Any]:
        """Get bot information"""
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=10)
            return response.json().get('result', {})
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            return {}

    def get_updates(self, timeout: int = 30) -> list:
        """Fetch new messages from Telegram"""
        try:
            url = f"{self.api_url}/getUpdates"
            params = {
                'offset': self.offset,
                'timeout': timeout,
                'allowed_updates': ['message']
            }
            response = requests.get(url, params=params, timeout=timeout + 5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('ok'):
                return data.get('result', [])
            else:
                logger.error(f"Telegram API error: {data.get('description')}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get updates: {e}")
            return []

    def send_message(self, chat_id: str, text: str, reply_to_message_id: Optional[int] = None) -> bool:
        """Send a message to a user or group"""
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            if reply_to_message_id:
                payload['reply_to_message_id'] = reply_to_message_id
                
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get('ok', False)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def generate_static_response(self, user_message: str) -> Optional[str]:
        """Generate response based on built-in knowledge base"""
        msg = user_message.lower()
        
        # 1. Greetings
        if any(word in msg for word in ['привет', 'здравствуй', 'начать', 'start', 'hello', 'hi']):
            return (
                "👋 <b>Добро пожаловать в проект «КОД УПРАВЛЕНИЯ»!</b>\n\n"
                "Я ваш системный ассистент. Я помогу вам разобраться в программе обучения управлению кафе за 30 дней.\n\n"
                "<b>Что вас интересует?</b>\n"
                "• 📚 О программе\n"
                "• 🎯 Результаты обучения\n"
                "• 👨‍💼 Об авторе (Aslan Uzhakhov)\n"
                "• 🛠 Модули программы\n"
                "• 🤝 Помощь оператора\n\n"
                "Просто напишите ваш вопрос!"
            )

        # 2. About Program
        if any(word in msg for word in ['программа', 'обучение', 'курс', 'что это', 'подробности']):
            return (
                "📚 <b>О программе «КОД УПРАВЛЕНИЯ»</b>\n\n"
                "Это интенсивная 30-дневная программа для владельцев и управляющих кафе/кофеен.\n\n"
                "<b>Основные направления:</b>\n"
                "1. Систематизация всех процессов.\n"
                "2. Внедрение чек-листов и стандартов.\n"
                "3. Управление командой и KPI.\n"
                "4. Финансовый контроль и прибыльность.\n\n"
                "<b>Формат:</b> Практические задания, готовые шаблоны и обратная связь."
            )

        # 3. Results
        if any(word in msg for word in ['результат', 'выгода', 'зачем', 'что получу']):
            return (
                "🎯 <b>Ваши результаты через 30 дней:</b>\n\n"
                "✅ <b>Порядок:</b> Управление по системе, а не по интуиции.\n"
                "✅ <b>Прибыль:</b> Рост показателей за счет контроля издержек.\n"
                "✅ <b>Команда:</b> Сотрудники знают свои задачи и работают на результат.\n"
                "✅ <b>Свобода:</b> Бизнес работает стабильно даже в ваше отсутствие.\n\n"
                "Вы перейдете от тушения пожаров к стратегическому развитию."
            )

        # 4. Modules / Navigation
        if any(word in msg for word in ['модули', 'навигация', 'блоки', 'чему учат', 'этапы']):
            return (
                "🛠 <b>Модули программы:</b>\n\n"
                "📍 <b>Модуль 1:</b> Фундамент и стандарты сервиса.\n"
                "📍 <b>Модуль 2:</b> Управление персоналом и мотивация.\n"
                "📍 <b>Модуль 3:</b> Финансовый учет и аналитика.\n"
                "📍 <b>Модуль 4:</b> Маркетинг и привлечение гостей.\n"
                "📍 <b>Модуль 5:</b> Масштабирование и делегирование.\n\n"
                "Каждый модуль включает в себя конкретные инструменты для внедрения."
            )

        # 5. Author
        if any(word in msg for word in ['автор', 'аслан', 'uzhakhov', 'кто ведет']):
            return (
                "👨‍💼 <b>Об авторе — Aslan Uzhakhov</b>\n\n"
                "Системный консультант и эксперт по масштабированию ресторанного бизнеса.\n\n"
                "• Помог десяткам заведений выстроить систему управления.\n"
                "• Автор методики, превращающей хаотичное кафе в прибыльную сеть.\n"
                "• Специалист по автоматизации и контролю качества."
            )

        # 6. Operator / Help
        if any(word in msg for word in ['оператор', 'помощь', 'человек', 'связаться', 'менеджер', 'вопрос']):
            return (
                "🤝 <b>Нужна помощь человека?</b>\n\n"
                "Вы можете задать свой вопрос или связаться с нами напрямую:\n"
                "👉 <b>Наш канал:</b> https://t.me/+Lzaw4ImRzoI3Nzky\n\n"
                "Оставьте ваш контакт или напишите в личные сообщения администратору канала."
            )

        # 7. Default for other queries
        return (
            "🤔 <b>Я вас понял!</b>\n\n"
            "Я — ассистент программы «КОД УПРАВЛЕНИЯ».\n\n"
            "Я могу рассказать подробнее о:\n"
            "• Программе обучения\n"
            "• Результатах\n"
            "• Модулях\n"
            "• Авторе\n\n"
            "Если ваш вопрос требует участия человека, напишите <b>'оператор'</b>."
        )

    def handle_message(self, update: Dict[str, Any]) -> None:
        """Process incoming message"""
        try:
            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            message_id = message.get('message_id')
            text = message.get('text', '').strip()
            chat_type = message.get('chat', {}).get('type')

            if not chat_id or not text:
                return

            # In groups, only respond if mentioned or if it's a command
            is_private = chat_type == 'private'
            is_mentioned = f"@{self.bot_username}" in text
            
            # Simple keyword matching for groups even without mention
            keywords = ['программа', 'код управления', 'аслан', 'результат', 'модуль', 'помощь', 'оператор']
            contains_keyword = any(k in text.lower() for k in keywords)

            if is_private or is_mentioned or contains_keyword:
                # Remove bot mention from text for cleaner processing
                clean_text = text.replace(f"@{self.bot_username}", "").strip()
                
                response = self.generate_static_response(clean_text)
                if response:
                    self.send_message(str(chat_id), response, reply_to_message_id=message_id)
                    logger.info(f"✅ Replied in {chat_type} chat {chat_id}")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)

    def run(self) -> None:
        """Main bot loop"""
        logger.info("🚀 Starting bot polling (Static Mode)...")
        
        while True:
            try:
                updates = self.get_updates(timeout=30)
                if updates:
                    for update in updates:
                        self.offset = update.get('update_id', 0) + 1
                        if 'message' in update:
                            self.handle_message(update)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                import time
                time.sleep(5)

if __name__ == '__main__':
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()
