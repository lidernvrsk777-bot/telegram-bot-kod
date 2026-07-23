
import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from flask import Flask
from threading import Thread

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask for Render Health Check
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Tokens
DOBBY_TOKEN = "8392695497:AAFxZaIBKwgKzurVdClFRGys1LGPCfwZ0H0"
FUNNEL_TOKEN = "8954284939:AAFEK0kGrpuK7th5VUsM_uG7DU2AYv2YMoM"

# Knowledge Base
KNOWLEDGE_BASE = {
    "модуль 1": "<b>📍 Модуль 1: Фундамент Системы</b>\n\nВ этом модуле мы разбираем, как перестать тянуть всё на себе и начать строить бизнес, который работает по правилам. \n\nВы узнаете:\n— Как оцифровать текущие процессы\n— Как найти 'дыры', куда утекают деньги и время\n— Как выстроить скелет управления.",
    "модуль 2": "<b>📍 Модуль 2: Команда и Делегирование</b>\n\nУчимся управлять людьми так, чтобы они работали на результат.\n\nВ программе:\n— Как нанимать 'своих' людей\n— Как ставить задачи, чтобы их не переделывать\n— Как создать систему мотивации.",
    "модуль 3": "<b>📍 Модуль 3: Финансы и Прибыль</b>\n\nРазбираемся с цифрами без головной боли.\n\nРезультат модуля:\n— Понятная финансовая модель вашего бизнеса\n— Умение видеть прибыль за кучей отчетов.",
    "автор": "<b>Об авторе: Аслан Ужахов</b>\n\n15 лет в управлении. В канале «Код Управления» делится только тем, что проверил на собственном опыте.\n\nЛичный контакт: @aslan_systems",
    "связь": "Для связи с Асланом пишите сюда: @aslan_systems",
    "помощь": "Я Доби! Ваша навигация. 🫡\n\nЯ могу рассказать про:\n— Модули программы (напишите 'модуль 1', 'модуль 2' или 'модуль 3')\n— Автора проекта\n— Как связаться с поддержкой\n\nПросто напишите ваш вопрос!"
}

# Funnel Content
SUBSCRIPTION_LINK = "https://t.me/tribute/app?startapp=ep_8xb4yfPbGCTBmvwOgElNJH3tWhUoMOST5JLSWs6aqm9e3GJpgk"
WELCOME_TEXT = "<b>Привет! Я — проводник в мир системного управления.</b> 🚀\n\nХотите узнать, как выстроить систему и наконец выдохнуть? Напишите <b>«Да»</b>!"
BENEFITS_TEXT = "<b>В канале «Код Управления» вас ждут:</b>\n\n✅ Инструменты управления\n✅ Разборы кейсов HoReCa\n✅ Психология команд\n✅ Финансовая система\n\nГотовы к первому шагу? Напишите <b>«Хочу»</b>!"
OFFER_TEXT = f"<b>Ваш путь начинается здесь.</b> 📍\n\n🔗 <b>Подписка:</b> <a href='{SUBSCRIPTION_LINK}'>Перейти к оплате</a>\n\nВопросы? Пишите @aslan_systems."

# --- DOBBY BOT LOGIC ---
async def dobby_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.lower()
    logger.info(f"Dobby received: {text}")
    
    response = None
    if "доби" in text:
        response = KNOWLEDGE_BASE["помощь"]
    
    for key, val in KNOWLEDGE_BASE.items():
        if key in text:
            response = val
            break
            
    if any(word in text for word in ["аслан", "автор"]):
        response = KNOWLEDGE_BASE["автор"]
        
    if any(word in text for word in ["связь", "написать", "контакт"]):
        response = KNOWLEDGE_BASE["связь"]

    if response:
        await update.message.reply_text(response, parse_mode='HTML')

# --- FUNNEL BOT LOGIC ---
async def funnel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode='HTML')

async def funnel_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.lower()
    logger.info(f"Funnel received: {text}")
    
    if "да" in text:
        await update.message.reply_text(BENEFITS_TEXT, parse_mode='HTML')
    elif "хочу" in text or "подробнее" in text:
        await update.message.reply_text(OFFER_TEXT, parse_mode='HTML')
    else:
        await update.message.reply_text("Напишите <b>«Да»</b>, чтобы продолжить!", parse_mode='HTML')

# --- MAIN RUNNER ---
async def run_bots():
    dobby_app = ApplicationBuilder().token(DOBBY_TOKEN).build()
    funnel_app = ApplicationBuilder().token(FUNNEL_TOKEN).build()

    dobby_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), dobby_handle_message))
    funnel_app.add_handler(CommandHandler("start", funnel_start))
    funnel_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), funnel_handle_message))

    # Start Flask in a separate thread
    Thread(target=run_flask, daemon=True).start()

    # Start both bots
    await asyncio.gather(
        dobby_app.initialize(),
        funnel_app.initialize(),
        dobby_app.start(),
        funnel_app.start(),
        dobby_app.updater.start_polling(drop_pending_updates=True),
        funnel_app.updater.start_polling(drop_pending_updates=True)
    )
    
    logger.info("Unified bots with Flask health check started...")
    while True: await asyncio.sleep(1000)

if __name__ == '__main__':
    try:
        asyncio.run(run_bots())
    except KeyboardInterrupt:
        pass
