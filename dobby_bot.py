
import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("DOBBY_TOKEN", "8392695497:AAFxZaIBKwgKzurVdClFRGys1LGPCfwZ0H0")
GROUP_CHAT_ID = -1002381005898

# Knowledge Base
KNOWLEDGE_BASE = {
    "модуль 1": "<b>📍 Модуль 1: Фундамент Системы</b>\n\nВ этом модуле мы разбираем, как перестать тянуть всё на себе и начать строить бизнес, который работает по правилам, а не по настроению. \n\nВы узнаете:\n— Как оцифровать текущие процессы\n— Как найти 'дыры', куда утекают деньги и время\n— Как выстроить скелет управления.",
    "модуль 2": "<b>📍 Модуль 2: Команда и Делегирование</b>\n\nУчимся управлять людьми так, чтобы они работали на результат, а не просто 'отсиживали' часы.\n\nВ программе:\n— Как нанимать 'своих' людей\n— Как ставить задачи, чтобы их не переделывать\n— Как создать систему мотивации, которая реально работает.",
    "модуль 3": "<b>📍 Модуль 3: Финансы и Прибыль</b>\n\nРазбираемся с цифрами без головной боли.\n\nРезультат модуля:\n— Понятная финансовая модель вашего бизнеса\n— Умение видеть прибыль за кучей отчетов\n— Инструменты для стратегического роста.",
    "автор": "<b>Об авторе: Аслан Ужахов</b>\n\n15 лет в управлении. Прошел путь от операционного менеджера до владельца бизнеса. В канале «Код Управления» делится только тем, что проверил на собственном опыте и миллионных бюджетах.\n\nЛичный контакт: @aslan_systems",
    "связь": "Для связи с Асланом и по вопросам обучения пишите сюда: @aslan_systems",
    "программа": "<b>Программа «Код Управления»</b> состоит из 3-х ключевых модулей, которые превращают хаос в систему. Мы работаем над фундаментом, командой и финансами.\n\nХотите узнать подробнее про конкретный модуль? Просто напишите его номер!",
    "помощь": "Я Доби! Ваша навигация в мире системного бизнеса. 🫡\n\nЯ могу рассказать про:\n— Модули программы (напишите 'модуль 1', 'модуль 2' или 'модуль 3')\n— Автора проекта\n— Как связаться с поддержкой\n\nПросто напишите ваш вопрос!"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text("Всем привет! Я Доби! 🫡\nЯ ваш системный ассистент. Помогу найти ответы на любые вопросы по программе 'Код Управления'!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes all incoming messages."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    logger.info(f"Received message: {text} in chat {update.message.chat_id}")

    response = None

    # Priority 1: Direct mention of Dobby
    if "доби" in text:
        if any(word in text for word in ["привет", "здравствуй", "ку"]):
            response = "Приветствую! Доби к вашим услугам. Чем могу помочь? 😊"
        elif any(word in text for word in ["спасибо", "благодарю"]):
            response = "Всегда рад помочь! Если будут еще вопросы — я здесь. 🫡"
        else:
            response = KNOWLEDGE_BASE["помощь"]

    # Priority 2: Keywords from Knowledge Base
    for key, val in KNOWLEDGE_BASE.items():
        if key in text:
            response = val
            break

    # Priority 3: Special keywords for Aslan
    if any(word in text for word in ["аслан", "автор", "кто ведет"]):
        response = KNOWLEDGE_BASE["автор"]
    
    if any(word in text for word in ["связь", "контакт", "написать"]):
        response = KNOWLEDGE_BASE["связь"]

    if response:
        await update.message.reply_text(response, parse_mode='HTML')

async def main():
    """Starts the bot."""
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logger.info("Dobby Bot is starting...")
    
    # Run the bot
    await application.run_polling()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
