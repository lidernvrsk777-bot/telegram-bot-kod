#!/usr/bin/env python3
"""
Telegram Bot for КОД УПРАВЛЕНИЯ
Deployed on Render for 24/7 operation
Uses polling method (more reliable than webhooks on free tier)
"""

import os
import sys
import logging
from datetime import datetime
import requests
from typing import Optional, Dict, Any
import openai

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

# Manus AI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.manus.im/v1')

client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

# System prompt for the AI bot
SYSTEM_PROMPT = """Ты — Системный ассистент проекта «КОД УПРАВЛЕНИЯ» — программы обучения управлению кафе за 30 дней.

Твоя роль:
- Отвечать на вопросы о программе, методике и процессе обучения
- Давать глубокие, но лаконичные ответы, фокусируясь на практической пользе
- Быть вежливым, профессиональным и авторитетным консультантом
- Помогать по навигации по модулям программы

О программе:
- Длительность: 30 дней интенсивного обучения
- Фокус: чек-листы, KPI, стандарты сервиса, управление командой
- Результат: систематическое управление кафе вместо хаотичного подхода

Если пользователь просит связаться с человеком или говорит "оператор", "помощь", "человек" — предложи ему написать в канал Telegram: https://t.me/+Lzaw4ImRzoI3Nzky или оставить контакты.

Отвечай на русском языке. Будь кратким, но информативным. Используй форматирование HTML (<b>жирный</b>, <i>курсив</i>) для выделения ключевых моментов."""

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.api_url = f"{TELEGRAM_API_URL}/bot{token}"
        self.offset = 0
        self.user_data: Dict[str, Any] = {}
        logger.info("🤖 Telegram Bot initialized")

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

    def send_message(self, chat_id: str, text: str) -> bool:
        """Send a message to a user"""
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get('ok', False)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def send_typing_action(self, chat_id: str) -> None:
        """Send typing action to show bot is processing"""
        try:
            url = f"{self.api_url}/sendChatAction"
            payload = {'chat_id': chat_id, 'action': 'typing'}
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            logger.debug(f"Failed to send typing action: {e}")

    def generate_response(self, user_message: str, user_id: str) -> str:
        """Generate AI response using Manus AI (OpenAI API)"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return (
                "Извините, сейчас я не могу обработать ваш запрос. 😔\n\n"
                "Пожалуйста, напишите в наш Telegram канал: https://t.me/+Lzaw4ImRzoI3Nzky"
            )

    def handle_message(self, update: Dict[str, Any]) -> None:
        """Process incoming message"""
        try:
            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            user_id = message.get('from', {}).get('id')
            text = message.get('text', '').strip()

            if not chat_id or not text:
                return

            user_name = message.get('from', {}).get('first_name', 'User')
            logger.info(f"📨 Message from {user_name} (ID: {user_id}): {text[:50]}")

            # Show typing indicator
            self.send_typing_action(str(chat_id))

            # Generate response
            response = self.generate_response(text, str(user_id))

            # Send response
            if self.send_message(str(chat_id), response):
                logger.info(f"✅ Response sent to {user_name}")
            else:
                logger.error(f"❌ Failed to send response to {user_name}")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)

    def run(self) -> None:
        """Main bot loop"""
        logger.info("🚀 Starting bot polling...")
        logger.info(f"Bot token: {self.token[:20]}...")
        logger.info(f"Chat ID: {TELEGRAM_CHAT_ID}")

        consecutive_errors = 0
        max_consecutive_errors = 10

        while True:
            try:
                updates = self.get_updates(timeout=30)
                
                if updates:
                    consecutive_errors = 0
                    for update in updates:
                        try:
                            self.offset = update.get('update_id', 0) + 1
                            
                            if 'message' in update:
                                self.handle_message(update)
                        except Exception as e:
                            logger.error(f"Error processing update: {e}")
                
                # Log that we're alive
                logger.debug(f"✓ Polling active... (offset: {self.offset})")

            except KeyboardInterrupt:
                logger.info("⏹️  Bot stopped by user")
                break
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in main loop (attempt {consecutive_errors}/{max_consecutive_errors}): {e}")
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical("Too many consecutive errors. Stopping bot.")
                    break
                # Wait before retrying
                import time
                time.sleep(5)

def main():
    """Entry point"""
    logger.info("=" * 60)
    logger.info("КОД УПРАВЛЕНИЯ — Telegram Bot")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()

if __name__ == '__main__':
    main()
