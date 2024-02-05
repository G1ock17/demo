from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentTypes
from main import dp, bot
from data import config
import sqlite3
from datetime import datetime


conn = sqlite3.connect('database/db.db')
cursor = conn.cursor()


def check_new_user(user_id):
    cursor.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,))
    existing_user = cursor.fetchone()
    if existing_user:
        return False
    else:
        return True


def add_user(user_id):
    current_date = datetime.now()
    cursor.execute('''INSERT INTO users (user_id, sub_status, date) VALUES (?, ?, ?)''', (user_id, 0, current_date))
    conn.commit()


def add_phone(user_id, phone):
    cursor.execute('''UPDATE users SET phone=? WHERE user_id=?''', (phone, user_id))
    conn.commit()


def switch_sub_status(user_id):
    cursor.execute('''UPDATE users SET sub_status=? WHERE user_id=?''', (1, user_id))
    conn.commit()


def get_sub_status(user_id):
    cursor.execute('''SELECT sub_status FROM users WHERE user_id = ?''', (user_id,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None


def get_user_phone(user_id):
    cursor.execute('''SELECT phone FROM users WHERE user_id = ?''', (user_id,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None