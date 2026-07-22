
import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("FUNNEL_TOKEN", "8954284939:AAFEK0kGrpuK7th5VUsM_uG7DU2AYv2YMoM")
SUBSCRIPTION_LINK = "https://t.me/tribute/app?startapp=ep_8xb4yfPbGCTBmvwOgElNJH3tWhUoMOST5JLSWs6aqm9e3GJpgk"

# Content
WELCOME_TEXT = """
<b>Привет! Я — проводник в мир системного управления.</b> 🚀

Если вы здесь, значит вы чувствуете, что бизнес забирает слишком много сил, а результат не радует так, как должен. 

<b>Канал «Код Управления» создан специально для:</b>
— Владельцев бизнеса, которые устали тянуть всё на себе
— Руководителей, которые хотят выстроить прозрачную систему
— Тех, кто хочет расти, а не просто выживать в операционке

Я помогу вам разобраться, как превратить хаос в четкий механизм.

Хотите узнать, что именно вы получите внутри? Напишите <b>«Да»</b>!
"""

BENEFITS_TEXT = """
<b>В канале «Код Управления» вас ждут:</b>

✅ <b>Конкретные инструменты:</b> Скрипты, чек-листы и шаблоны, которые можно внедрить за 15 минут.
✅ <b>Разборы кейсов:</b> Реальный опыт управления в сфере HoReCa и ритейла.
✅ <b>Психология бизнеса:</b> Как читать людей за 2 минуты и строить сильные команды.
✅ <b>Финансовая грамотность:</b> Как видеть реальную прибыль, а не просто цифры в обороте.

<b>Главное:</b> Никакой теории. Только то, что Аслан Ужахов проверил за 15 лет в управлении.

Готовы сделать первый шаг к свободе? 👇
"""

OFFER_TEXT = f"""
<b>Ваш путь к системному бизнесу начинается здесь.</b> 📍

Оформите подписку на закрытый канал «Код Управления» и получите доступ ко всем материалам сразу.

🔗 <b>Оформить подписку:</b> <a href="{SUBSCRIPTION_LINK}">Перейти к оплате</a>

После оплаты вы автоматически получите доступ к каналу. Если возникнут вопросы — пишите @aslan_systems.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(WELCOME_TEXT, parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles messages in the funnel."""
    text = update.message.text.lower()
    
    if "да" in text or "хочу" in text or "подробнее" in text:
        await update.message.reply_text(BENEFITS_TEXT, parse_mode='HTML')
        await asyncio.sleep(2)
        await update.message.reply_text(OFFER_TEXT, parse_mode='HTML')
    else:
        await update.message.reply_text("Напишите <b>«Да»</b>, чтобы узнать подробнее о пользе канала!", parse_mode='HTML')

async def main():
    """Starts the bot."""
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logger.info("Funnel Bot is starting...")
    await application.run_polling()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
