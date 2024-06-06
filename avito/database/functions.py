import sqlite3
from datetime import datetime

db_path = 'database/db.db'


def execute_query(query, params=()):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка выполнения запроса: {e}")


def fetch_one(query, params=()):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return None


def fetch_all(query, params=()):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return None


def check_new_user(user_id):
    existing_user = fetch_one('''SELECT * FROM users WHERE user_id = ?''', (user_id,))
    return existing_user is None


def add_user(user_id, user_name):
    if check_new_user(user_id):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_query('''INSERT INTO users (user_id, user_name, sub_status, date, money) VALUES (?, ?, ?, ?, ?)''',
                      (user_id, user_name, 0, current_date, 0))
    else:
        print(f"Пользователь с ID {user_id} уже существует.")


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
    current_balance = fetch_one("SELECT money FROM users WHERE user_id = ?", (user_id,))

    if current_balance and current_balance[0] >= amount:
        new_balance = current_balance[0] - amount
        execute_query("UPDATE users SET money = ? WHERE user_id = ?", (new_balance, user_id))
        print(f"Сумма {amount} успешно списана со счета пользователя {user_id}.")
    else:
        print(f"Ошибка: пользователь {user_id} не найден или недостаточно средств на счету.")


def change_requisite(user_id, new_requisite):
    execute_query("UPDATE users SET requisites = ? WHERE user_id = ?", (new_requisite, user_id))
    print("Реквизиты пользователя успешно изменены.")


def create_withdrawal_request(user_id, requisite, value):
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query('''INSERT INTO out_money (requisite, user_id, value, date, status) VALUES (?, ?, ?, ?, ?)''',
                  (requisite, user_id, value, current_date, 0))

    withdrawal_request_id = fetch_one("SELECT last_insert_rowid()")
    if withdrawal_request_id:
        print("Заявка на вывод средств успешно создана.")
        return withdrawal_request_id[0]
    else:
        print("Ошибка при создании заявки на вывод средств.")
        return None


def get_user_applications(user_id):
    withdrawal_requests = fetch_all('''SELECT id FROM out_money WHERE user_id = ?''', (user_id,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("У пользователя нет заявок на вывод средств.")
        return []


def get_application(id):
    withdrawal_requests = fetch_all('''SELECT * FROM out_money WHERE id = ?''', (id,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("Заявка не найдена.")
        return []


def add_request(user_id):
    query = '''INSERT INTO requests (user_id, date, status) VALUES (?, ?, ?)'''
    params = (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
    execute_query(query, params)
    print(f"Заявка от пользователя {user_id} на получение материала успешно создана.")


def get_user_requests_status(user_id):
    withdrawal_requests = fetch_all('''SELECT id FROM requests WHERE user_id = ? AND status = ?''', (user_id, 0,))
    if withdrawal_requests:
        return None
    else:
        return True


def get_user_materials(user_id):
    withdrawal_requests = fetch_all('''SELECT id FROM vins WHERE user_id = ? AND status = ?''', (user_id, 0,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("У пользователя нет заявок на вывод средств.")
        return None


def get_material(id):
    withdrawal_requests = fetch_all('''SELECT * FROM vins WHERE id = ?''', (id,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("Заявка не найдена.")
        return []


def get_material_patch(id):
    withdrawal_requests = fetch_all('''SELECT patch FROM photo WHERE vin_id = ?''', (id,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("Заявка не найдена в бд.")
        return []


def add_link_if_not_exists(user_id, link):
    withdrawal_requests = fetch_all("SELECT * FROM anc WHERE link = ?", (link,))

    if withdrawal_requests:
        return None
    else:
        query = "INSERT INTO anc (user_id, date, link, status) VALUES (?, ?, ?, ?)"
        params = (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), link, 0)
        execute_query(query, params)


def admin_get_req(table):
    withdrawal_requests = fetch_all(f'''SELECT id FROM {table} WHERE status = ?''', (0,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("Ошибка в бд")
        return None
