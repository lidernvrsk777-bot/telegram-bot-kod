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

# System prompt for the AI bot
SYSTEM_PROMPT = """Ты — Системный ассистент проекта «КОД УПРАВЛЕНИЯ» — программы обучения управлению кафе за 30 дней.

Твоя роль:
- Отвечать на вопросы о программе, методике и процессе обучения
- Давать глубокие, но лаконичные ответы, фокусируясь на практической пользе
- Быть вежливым, профессиональным и авторитетным консультантом

О программе:
- Длительность: 30 дней интенсивного обучения
- Фокус: чек-листы, KPI, стандарты сервиса, управление командой
- Результат: систематическое управление кафе вместо хаотичного подхода

Если пользователь просит связаться с человеком или говорит "оператор", "помощь", "человек" — предложи ему написать в канал Telegram или оставить контакты.

Отвечай на русском языке. Будь кратким, но информативным."""


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
        """Generate AI response using simple logic (no external API needed)"""
        message_lower = user_message.lower()
        
        # Check for operator/human request
        if any(word in message_lower for word in ['оператор', 'человек', 'помощь', 'связь', 'менеджер']):
            return (
                "🤝 <b>Вам нужна помощь человека?</b>\n\n"
                "Вы можете:\n"
                "• Написать в наш Telegram канал: https://t.me/+Lzaw4ImRzoI3Nzky\n"
                "• Оставить свой контакт, и мы свяжемся с вами\n\n"
                "Или я могу помочь вам прямо сейчас — задайте ваш вопрос! 😊"
            )
        
        # Program-related questions
        if any(word in message_lower for word in ['программа', 'обучение', '30 дней', 'курс', 'стоимость', 'цена']):
            return (
                "📚 <b>О программе «КОД УПРАВЛЕНИЯ»</b>\n\n"
                "Это интенсивная 30-дневная программа обучения для владельцев кафе и кофеен.\n\n"
                "<b>Что вы получите:</b>\n"
                "✓ Чек-листы для ежедневного управления\n"
                "✓ Систему KPI и метрик\n"
                "✓ Стандарты сервиса\n"
                "✓ Методы управления командой\n"
                "✓ Пошаговую систему масштабирования\n\n"
                "<b>Результат:</b> Систематическое управление вместо хаоса.\n\n"
                "Хотите узнать больше? Напишите нам в канал! 👉 https://t.me/+Lzaw4ImRzoI3Nzky"
            )
        
        # Benefits/Results questions
        if any(word in message_lower for word in ['результат', 'выгода', 'получу', 'достигну', 'результаты']):
            return (
                "🎯 <b>Результаты за 30 дней</b>\n\n"
                "После прохождения программы вы:\n"
                "✓ Систематизируете управление кафе\n"
                "✓ Повысите прибыльность на 15-30%\n"
                "✓ Снизите текучесть персонала\n"
                "✓ Улучшите качество сервиса\n"
                "✓ Получите независимость от своего присутствия\n"
                "✓ Сможете масштабировать бизнес\n\n"
                "Главное — вы перейдёте от интуитивного управления к системному подходу."
            )
        
        # Greeting
        if any(word in message_lower for word in ['привет', 'привет!', 'hi', 'hello', 'привет', 'как дела', 'что нового']):
            return (
                "👋 <b>Добро пожаловать!</b>\n\n"
                "Я — Системный ассистент проекта «КОД УПРАВЛЕНИЯ».\n\n"
                "Я помогу вам разобраться с программой обучения управлению кафе за 30 дней.\n\n"
                "<b>Что вас интересует?</b>\n"
                "• О программе\n"
                "• Результаты\n"
                "• Об авторе\n"
                "• Как начать\n\n"
                "Или просто задайте ваш вопрос! 😊"
            )
        
        # About author
        if any(word in message_lower for word in ['автор', 'aslan', 'асланн', 'асланн', 'кто', 'об авторе']):
            return (
                "👨‍💼 <b>Об авторе — Aslan Uzhakhov</b>\n\n"
                "Системный консультант и бизнес-тренер с опытом в управлении сетями кафе и кофеен.\n\n"
                "Aslan разработал методику «КОД УПРАВЛЕНИЯ» на основе собственного опыта масштабирования бизнеса.\n\n"
                "<b>Специализация:</b>\n"
                "• Управление персоналом\n"
                "• Финансовый контроль\n"
                "• Стандартизация процессов\n"
                "• Масштабирование кафе и кофеен\n\n"
                "Его система помогла десяткам владельцев перейти от хаотичного управления к системному подходу."
            )
        
        # Default response
        return (
            "🤔 Интересный вопрос!\n\n"
            "Я — ассистент программы «КОД УПРАВЛЕНИЯ» — системы обучения управлению кафе за 30 дней.\n\n"
            "Я могу помочь вам с информацией о:\n"
            "• Программе обучения\n"
            "• Результатах и выгодах\n"
            "• Методике и подходе\n"
            "• Об авторе Aslan Uzhakhov\n\n"
            "Если вам нужна помощь человека, напишите 'оператор' или свяжитесь с нами в канале: https://t.me/+Lzaw4ImRzoI3Nzky"
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
