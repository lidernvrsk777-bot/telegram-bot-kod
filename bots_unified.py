
import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import openai

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tokens
DOBBY_TOKEN = "8392695497:AAFxZaIBKwgKzurVdClFRGys1LGPCfwZ0H0"
FUNNEL_TOKEN = "8954284939:AAFEK0kGrpuK7th5VUsM_uG7DU2AYv2YMoM"

# AI Config
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-manus-ai-placeholder")
openai.api_base = "https://api.manus.im/v1"

# Knowledge Base for AI
SYSTEM_PROMPT = """
Ты — Доби, системный ассистент проекта «Код Управления» Аслана Ужахова.
Твоя задача: помогать участникам группы с навигацией по модулям и отвечать на вопросы о программе.

Информация о проекте:
- Модуль 1: Фундамент системы, оцифровка процессов, поиск 'дыр' в бизнесе.
- Модуль 2: Команда и делегирование, найм, мотивация, постановка задач.
- Модуль 3: Финансы и прибыль, финмодель, стратегический рост.
- Автор: Аслан Ужахов (15 лет в управлении).
- Личный контакт Аслана: @aslan_systems.

Твой стиль: вежливый, профессиональный, системный. Если тебя благодарят — отвечай взаимностью. Если спрашивают про модули — давай краткую и полезную информацию.
"""

# Funnel Content
SUBSCRIPTION_LINK = "https://t.me/tribute/app?startapp=ep_8xb4yfPbGCTBmvwOgElNJH3tWhUoMOST5JLSWs6aqm9e3GJpgk"
WELCOME_TEXT = "<b>Привет! Я — проводник в мир системного управления.</b> 🚀\n\nЕсли вы здесь, значит вы чувствуете, что бизнес забирает слишком много сил. Хотите узнать, как выстроить систему? Напишите <b>«Да»</b>!"
BENEFITS_TEXT = "<b>В канале «Код Управления» вас ждут:</b>\n\n✅ Инструменты управления\n✅ Разборы кейсов HoReCa\n✅ Психология команд\n✅ Финансовая система\n\nГотовы к первому шагу? Напишите <b>«Хочу»</b>!"
OFFER_TEXT = f"<b>Ваш путь начинается здесь.</b> 📍\n\n🔗 <b>Подписка:</b> <a href='{SUBSCRIPTION_LINK}'>Перейти к оплате</a>\n\nВопросы? Пишите @aslan_systems."

# --- DOBBY BOT LOGIC ---
async def dobby_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.lower()
    
    # Check if Dobby should respond (name mention or keywords)
    keywords = ["доби", "модуль", "аслан", "автор", "программа", "помощь", "связь"]
    if any(k in text for k in keywords):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": update.message.text}
                ]
            )
            reply = response.choices[0].message.content
            await update.message.reply_text(reply, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"AI Error: {e}")
            await update.message.reply_text("Доби на связи! Пожалуйста, напишите @aslan_systems для уточнения деталей.")

# --- FUNNEL BOT LOGIC ---
async def funnel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode='HTML')

async def funnel_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "да" in text:
        await update.message.reply_text(BENEFITS_TEXT, parse_mode='HTML')
    elif "хочу" in text or "подробнее" in text:
        await update.message.reply_text(OFFER_TEXT, parse_mode='HTML')
    else:
        await update.message.reply_text("Напишите <b>«Да»</b>, чтобы узнать о пользе канала!", parse_mode='HTML')

# --- MAIN RUNNER ---
async def run_bots():
    dobby_app = ApplicationBuilder().token(DOBBY_TOKEN).build()
    funnel_app = ApplicationBuilder().token(FUNNEL_TOKEN).build()

    # Handlers
    dobby_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), dobby_handle_message))
    funnel_app.add_handler(CommandHandler("start", funnel_start))
    funnel_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), funnel_handle_message))

    # Start both
    await asyncio.gather(
        dobby_app.initialize(),
        funnel_app.initialize(),
        dobby_app.start(),
        funnel_app.start(),
        dobby_app.updater.start_polling(),
        funnel_app.updater.start_polling()
    )
    
    logger.info("Both bots are running unified...")
    while True: await asyncio.sleep(1000)

if __name__ == '__main__':
    asyncio.run(run_bots())
