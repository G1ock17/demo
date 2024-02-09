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
    cursor.execute('''UPDATE users SET sub_status=? WHERE user_id=?''', (0, user_id))
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


def add_log(column):
    cursor.execute(f'''SELECT {column} FROM logs WHERE id = ?''', (1,))
    result = cursor.fetchone()
    print(result[0])
    if result:
        cursor.execute(f'''UPDATE logs SET {column}=? WHERE id=?''', (int(result[0]) + 1, 1,))
        conn.commit()
    else:
        return


def get_info_logs():
    cursor.execute('''SELECT requests, answers FROM logs WHERE id = ?''', (1,))
    result = cursor.fetchone()

    if result:
        return result
    else:
        return None


def get_answers_logs():
    cursor.execute('SELECT date, user_id, message FROM reply')
    rows = cursor.fetchall()
    for row in rows:
        print(rows[0], rows[1], rows[2])
        return row


def add_answer_logs(user_id, message):
    current_date = datetime.now()
    cursor.execute('''INSERT INTO reply (user_id, message, date) VALUES (?, ?, ?)''', (user_id, message, current_date))
    conn.commit()


def clear_logs():
    cursor.execute(f'''UPDATE logs SET requests=?, answers=? WHERE id=?''', (1,))
    conn.commit()

