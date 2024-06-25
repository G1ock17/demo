import sqlite3

class Storage:
    def __init__(self):
        # Подключение к базе данных SQLite
        self.connection = sqlite3.connect('C:/Users/zzkkd/OneDrive/Desktop/forClient/database/db.db')
        self.connection.row_factory = sqlite3.Row  # Позволяет обращаться к столбцам по имени
        self.connection.execute("PRAGMA foreign_keys = 1")  # Включить поддержку внешних ключей
        self.connection.commit()

    def close(self):
        self.connection.close()

    def end_rent(self, row_id):
        """Завершение аренды по id"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE numbers SET status=2 WHERE id=?", (row_id,))
        cursor.execute("""
        INSERT INTO history (port, phone, user_id, start_time, end_time)
        SELECT port, phone, user_id, start_time, end_time
        FROM numbers WHERE id=?
        """, (row_id,))
        self.connection.commit()
        return cursor.lastrowid

    def get_ports(self, comp):
        """Список портов с номерами"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT port, phone, status FROM numbers WHERE computer=? ORDER BY port", (comp,))
        return cursor.fetchall()

    def clean_all(self, comp):
        """Очистка всех номеров от данного симбанка"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM numbers WHERE computer=?", (comp,))
        self.connection.commit()

    def clean_finished(self):
        """Очистка таблицы номеров WHERE end_time < текущий UNIX_TIMESTAMP"""
        cursor = self.connection.cursor()

        cursor.execute("""
        DELETE FROM numbers WHERE end_time > 0 AND end_time < strftime('%s','now')
        """)
        self.connection.commit()

    def fill_numbers(self, records):
        cursor = self.connection.cursor()
        cursor.executemany("""
        INSERT INTO numbers (computer, port, phone) VALUES (?,?,?)
        ON CONFLICT(port) DO UPDATE SET phone=excluded.phone
        """, records)
        self.connection.commit()
        return cursor.lastrowid

    def add_message(self, phone, user_id, msg):
        """Добавление текста для отправки пользователю"""
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO messages (phone, user_id, message, status) VALUES (?,?,?,?)",
                       (phone, user_id, msg, 0))  # Устанавливаем status в 0 при вставке
        self.connection.commit()
        return cursor.lastrowid

    def get_rented(self, comp):
        """Получение данных арендованных номеров"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM numbers WHERE status=1 AND computer=?", (comp,))
        return cursor.fetchall()

    def get_calls(self, num):
        """Получение данных заявок на звонок"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM calls WHERE number_id=?", (num,))
        result = cursor.fetchall()
        cursor.execute("DELETE FROM calls WHERE number_id=?", (num,))
        self.connection.commit()
        return result

    def get_ussd(self, num):
        """Получение данных заявок на ussd"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM ussd WHERE number_id=?", (num,))
        result = cursor.fetchall()
        cursor.execute("DELETE FROM ussd WHERE number_id=?", (num,))
        self.connection.commit()
        return result

    def get_messages(self):
        """Получение непрочитанных сообщений"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT messages.id, messages.user_id, messages.phone, 
                   users.user_name, messages.message
            FROM messages 
            JOIN users USING (user_id) 
            WHERE messages.status = 0;
        """)
        return cursor.fetchall()

    def set_read_msg(self, msg_id):
        """Пометить сообщение прочитанным"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE messages SET status = 1 WHERE id = ?", (msg_id,))
        self.connection.commit()
