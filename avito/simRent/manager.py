from threading import Thread, Timer
from multiprocessing import Queue
from os.path import exists
import platform
import re
import time
from serial.tools import list_ports as prtlst
from app.sms import SMS
from app.db import Storage
# Идентификатор компьютера для нескольких симбанков
computer = platform.node()

def info_num(port):
    """Определитель номера"""
    try:
        hub = SMS(port)
        num = hub.get_number()
        del hub  # закрываем порт чтоб не блокировать
    except Exception:
        num = False
    if num and num.isnumeric():
        return computer, port, num


def info_sms(rec):
    """Проверка смс и времени аренды"""
    delta = int(rec['end_time']) - int(time.time())
    finish = False # признак необходимости удаления номера из БД
    reply = None
    id = None
    db = Storage()
    # Проверка заявок на звонки
    # Проверка заявок на ussd

    # проверка смс
    hub = SMS(rec['port'])
    sms = hub.get_sms_list()
    # Совершаем звонки если есть

    del hub  # закрываем порт чтоб не блокировать
    if sms:
        reply = '\n'.join(sms)

    if reply:
        id = db.add_message(rec['phone'], rec['user_id'], reply)
        if finish:
            db.end_rent(rec['id'])
    db.close()

    if id:
        pass
        #Timer(25, db.update_status(id)).start()



# постановщик в очередь
def wrapper(func, arg, q):
    q.put(func(arg))


# многопоточный обработчик
def queue_process(func, nums):
    q_out = Queue()
    my_list = []
    # готовим очередь
    for p in nums:
        Thread(target=wrapper, args=(func, p, q_out)).start()
    # заполняем номерами
    for _ in range(len(nums)):
        elem = q_out.get()
        if elem:
            my_list.append(elem)

    return my_list


def get_nums(detected):
    db_ports = [row['port'] for row in detected]
    print('Кол-во портов с определенными номерами:', len(db_ports))
    ports = [x for x in get_ports_list() if x not in db_ports]
    print(f'Кол-во портов с не определенными номерами: {len(ports)}')
    if ports:
        print(f'Найдены порты с неопределнными номерами {ports}')
        return queue_process(info_num, ports)


def check_rented(nums):
    if nums:
        return queue_process(info_sms, nums)


def natural_key(string_):
    """ Ключи для натуральной сортировки See https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def get_ports_list():
    # подготовка списка портов для работы
    path_to_file = "ports.txt"
    # если есть файл читаем из него
    if exists(path_to_file):
        with open(path_to_file, "r") as filestream:
            content = filestream.read()
            pl = content.strip(" ,").split(",")
    else: # иначе берем по списку портов в системе
        pl = list(p.name for p in prtlst.comports())
        pl.sort(key=natural_key)

    return pl


def process_rented():
    """Обработка арендованных портов"""
    Timer(15, process_rented).start()
    db = Storage()
    numbers = db.get_rented(computer)
    db.close()
    print(f"Проверяем СМС: по {len(numbers)} номерам")
    check_rented(numbers)


def detect_numbers():
    """Определние новых номеров"""
    Timer(15, detect_numbers).start()
    db = Storage()
    numbers = get_nums(db.get_ports(computer))
    if numbers:
        print(f"Определили еще номеров: {len(numbers)}")
        db.fill_numbers(numbers)
    db.close()



if __name__ == "__main__":
    # Первичный сканнинг номеров, заполнение БД
    print("Чистим номера")
    db = Storage()
    db.clean_finished()
    db.close()
    # повторяющиеся процессы
    # anti_spam()
    process_rented()
    detect_numbers()
