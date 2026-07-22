import logging
import os
import sqlite3
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, JobQueue

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid getting noise from http.client
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8954284939:AAFEK0kGrpuK7th5VUsM_uG7DU2AYv2YMoM")
SUBSCRIPTION_LINK = "https://t.me/tribute/app?startapp=ep_8xb4yfPbGCTBmvwOgElNJH3tWhUoMOST5JLSWs6aqm9e3GJpgk"
ADMIN_USERNAME = "aslan_systems"

# Database setup
DATABASE_NAME = 'users.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            state TEXT,
            last_interaction TEXT,
            subscription_link_sent TEXT,
            reminders_sent INTEGER DEFAULT 0,
            subscribed BOOLEAN DEFAULT FALSE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            keyword TEXT PRIMARY KEY,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def update_user_data(user_id, state=None, last_interaction=None, subscription_link_sent=None, reminders_sent=None, subscribed=None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    if not get_user_data(user_id):
        cursor.execute('INSERT INTO users (user_id, state, last_interaction) VALUES (?, ?, ?)', 
                       (user_id, state or 'start', last_interaction or datetime.now().isoformat()))
    else:
        updates = []
        params = []
        if state is not None:
            updates.append('state = ?')
            params.append(state)
        if last_interaction is not None:
            updates.append('last_interaction = ?')
            params.append(last_interaction)
        if subscription_link_sent is not None:
            updates.append('subscription_link_sent = ?')
            params.append(subscription_link_sent)
        if reminders_sent is not None:
            updates.append('reminders_sent = ?')
            params.append(reminders_sent)
        if subscribed is not None:
            updates.append('subscribed = ?')
            params.append(subscribed)
        
        if updates:
            query = f'UPDATE users SET {
