import sqlite3
from datetime import datetime

db_path = 'database/db.db'


def execute_query(query, params=()):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()


def fetch_one(query, params=()):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()


def check_new_user(user_id):
    existing_user = fetch_one('''SELECT * FROM users WHERE user_id = ?''', (user_id,))
    return existing_user is None


def add_user(user_id):
    current_date = datetime.now()
    execute_query('''INSERT INTO users (user_id, sub_status, date, money) VALUES (?, ?, ?, ?)''',
                  (user_id, 0, current_date, 0))


def add_phone(user_id, phone):
    execute_query('''UPDATE users SET phone=? WHERE user_id=?''', (phone, user_id))


def switch_sub_status(user_id):
    execute_query('''UPDATE users SET sub_status=? WHERE user_id=?''', (0, user_id))


def get_sub_status(user_id):
    result = fetch_one('''SELECT sub_status FROM users WHERE user_id = ?''', (user_id,))
    return result[0] if result else None


def get_user_phone(user_id):
    result = fetch_one('''SELECT phone FROM users WHERE user_id = ?''', (user_id,))
    return result[0] if result else None


def get_user_information(user_id):
    return fetch_one('''SELECT user_id, date, money, requisites FROM users WHERE user_id = ?''', (user_id,))


def subtract_from_balance(user_id, amount):
    try:
        # Устанавливаем соединение с базой данных
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Получаем текущий баланс пользователя
            cursor.execute("SELECT money FROM users WHERE user_id = ?", (user_id,))
            current_balance = cursor.fetchone()

            # Если пользователь найден и у него достаточно средств
            if current_balance and current_balance[0] >= amount:
                new_balance = current_balance[0] - amount
                # Обновляем баланс пользователя
                cursor.execute("UPDATE users SET money = ? WHERE user_id = ?", (new_balance, user_id))
                conn.commit()
                print(f"Сумма {amount} успешно списана со счета пользователя {user_id}.")
            else:
                print(f"Ошибка: пользователь {user_id} не найден или недостаточно средств на счету.")

    except sqlite3.Error as e:
        print(f"Ошибка при списании средств: {e}")


def change_requisite(user_id, new_requisite):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET requisites = ? WHERE user_id = ?", (new_requisite, user_id))
            conn.commit()

        print("Реквизиты пользователя успешно изменены.")
    except sqlite3.Error as e:
        print(f"Ошибка при изменении реквизитов: {e}")


def create_withdrawal_request(user_id, requisite, value):
    try:
        # Устанавливаем соединение с базой данных
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Получаем текущую дату и время
            current_date = datetime.now()

            # Создаем заявку на вывод средств
            cursor.execute('''INSERT INTO out_money (requisite, user_id, value, date, status)
                              VALUES (?, ?, ?, ?, ?)''', (requisite, user_id, value, current_date, 0))
            conn.commit()

            # Получаем id только что созданной заявки
            cursor.execute("SELECT last_insert_rowid()")
            withdrawal_request_id = cursor.fetchone()[0]

            print("Заявка на вывод средств успешно создана.")
            return withdrawal_request_id
    except sqlite3.Error as e:
        print(f"Ошибка при создании заявки на вывод средств: {e}")
        return None


def get_user_applications(user_id):
    try:
        # Устанавливаем соединение с базой данных
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Получаем все заявки пользователя по его user_id
            cursor.execute('''SELECT * FROM out_money WHERE user_id = ?''', (user_id,))
            withdrawal_requests = cursor.fetchall()

            if withdrawal_requests:
                return withdrawal_requests
            else:
                print("У пользователя нет заявок на вывод средств.")
    except sqlite3.Error as e:
        print(f"Ошибка при получении заявок на вывод средств: {e}")

