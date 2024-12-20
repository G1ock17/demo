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


def update_user_balance(user_id, amount, pm):
    current_balance = fetch_one("SELECT money FROM users WHERE user_id = ?", (user_id,))

    if pm == '+':
        new_balance = current_balance[0] + amount
        execute_query("UPDATE users SET money = ? WHERE user_id = ?", (new_balance, user_id))
    if pm == '-':
        if current_balance and current_balance[0] >= amount:
            new_balance = current_balance[0] - amount
            execute_query("UPDATE users SET money = ? WHERE user_id = ?", (new_balance, user_id))


def change_requisite(user_id, new_requisite):
    execute_query("UPDATE users SET requisites = ? WHERE user_id = ?", (new_requisite, user_id))
    print("Реквизиты пользователя успешно изменены.")


def create_withdrawal_request(user_id, requisite, value):
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query('''INSERT INTO money (requisite, user_id, value, date, status) VALUES (?, ?, ?, ?, ?)''',
                  (requisite, user_id, value, current_date, 0))

    withdrawal_request_id = fetch_one("SELECT last_insert_rowid()")
    if withdrawal_request_id:
        print("Заявка на вывод средств успешно создана.")
        return withdrawal_request_id[0]
    else:
        print("Ошибка при создании заявки на вывод средств.")
        return None


def get_user_applications(user_id):
    withdrawal_requests = fetch_all('''SELECT id FROM money WHERE user_id = ?''', (user_id,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("У пользователя нет заявок на вывод средств.")
        return []


def get_application(id):
    withdrawal_requests = fetch_all('''SELECT * FROM money WHERE id = ?''', (id,))
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


def get_user_limit_value(user_id):
    withdrawal_requests = fetch_all('''SELECT max_value FROM users WHERE user_id = ?''', (user_id,))
    if withdrawal_requests:
        return withdrawal_requests[0][0]
    else:
        return 0


def get_user_requests_value(user_id):
    withdrawal_requests = fetch_all('''SELECT * FROM requests WHERE user_id = ? and status = ?''', (user_id, 0,))
    if withdrawal_requests:
        return len(withdrawal_requests)
    else:
        return 0


def get_user_materials(user_id):
    withdrawal_requests = fetch_all('''SELECT id FROM vins WHERE user_id = ? AND status = ?''', (user_id, 1,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("У пользователя нет заявок на материал.")
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
        print("Фото не найдена в бд.")
        return []


def give_material_user(new_user_id):
    try:
        # Поиск первой строки, где user_id равно NULL
        select_query = "SELECT id FROM vins WHERE user_id IS NULL LIMIT 1"
        row = fetch_one(select_query)

        if row:
            vin_id = row[0]  # fetch_all возвращает список кортежей, берем первый элемент первого кортежа
            # Обновление user_id в найденной строке
            update_query = "UPDATE vins SET user_id = ? WHERE id = ?"
            execute_query(update_query, (new_user_id, vin_id))
            return vin_id
        else:
            return None  # Если нет строк с user_id равным NULL

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


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


def admin_get_info_req(table, id):
    withdrawal_requests = fetch_all(f'''SELECT * FROM {table} WHERE id = ?''', (id,))
    if withdrawal_requests:
        return withdrawal_requests
    else:
        print("Заявка не найдена.")
        return []


def update_status_and_get_user_id(req_type, type_id, status):
    execute_query(f"UPDATE {req_type} SET status = ? WHERE id = ?", (status, type_id))

    user_id = fetch_all(f"SELECT user_id FROM {req_type} WHERE id = ?", (type_id,))

    if user_id:
        return user_id[0][0]
    else:
        return None


def update_status_phone_and_get_user_id(status, phone, user_id, req_type, type_id, ):
    execute_query(
        "UPDATE vins SET status = ?, phone = ?, user_id = ? WHERE id = (SELECT id FROM vins WHERE status = 0 AND user_id IS NULL LIMIT 1)",
        (status, phone, user_id))
    execute_query(f"UPDATE {req_type} SET status = ? WHERE id = ?", (2, type_id))
    if execute_query:
        return True
    else:
        return None


def refusal_of_request(req_type, type_id):
    execute_query(f"UPDATE {req_type} SET status = ? WHERE id = ?", (2, type_id))
    if execute_query:
        return True
    else:
        return None

def get_number_by_id(self, num_id):
    cursor = self.execute("SELECT * FROM `numbers` WHERE `id` = %s", (num_id,))
    return cursor.fetchone()


def give_phone_for_user(user_id):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE numbers SET user_id = ?, status = 1 WHERE status = 0 AND id = (SELECT id FROM numbers WHERE status = 0 LIMIT 1)",
            (user_id,))
        conn.commit()
        cursor.execute("SELECT phone FROM numbers WHERE user_id = ? AND status = 1 ORDER BY id DESC LIMIT 1",
                       (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
