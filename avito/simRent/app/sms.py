# https://github.com/jonamat/sim-modem
import serial
import time
MIN_LEN = 100
ITERATION = 5


def decode16(resp):
    resp = resp.strip('"')
    try:
        return bytes.fromhex(resp).decode('utf-16-be')
    except ValueError:
        return resp


class ClientError(Exception):
    """Класс для генерации ошибок работы скрипта"""
    pass


class SerialComm:
    """Класс коммуникации с оборудованием"""
    def __init__(
        self,
        address,
        baudrate=115200,
        timeout=3,
        at_cmd_delay=0.1,
        on_error=None,
        byte_encoding="ISO-8859-1",
    ):
        self.port = address
        self.at_cmd_delay = at_cmd_delay
        self.on_error = on_error
        self.byte_encoding = byte_encoding
        self.modem_serial = serial.Serial(
            port=address,
            baudrate=baudrate,
            timeout=timeout,
        )

    def send(self, cmd) -> str or None:
        self.modem_serial.write(cmd.encode(self.byte_encoding) + b"\r")
        time.sleep(self.at_cmd_delay)

    def send_raw(self, cmd):
        self.modem_serial.write(cmd)
        time.sleep(self.at_cmd_delay)

    def read_lines(self) -> list:
        read = self.modem_serial.readlines()
        for i, line in enumerate(read):
            read[i] = line.decode(self.byte_encoding).strip()
        if not read or read[-1] != "OK":
            #print(f"Ошибка команды порт {self.port}")
            return
        return read

    def read_raw(self, size: int):
        return self.modem_serial.read(size)

    def read_all(self):
        response = self.modem_serial.readall()
        return str(response)

    def close(self):
        self.modem_serial.close()


class SMS:
    """Класс для работы с симбанком через команды"""
    def __init__(self, port):
        self.port = port
        self.comm = SerialComm(port)

    def __del__(self):
        if hasattr(self, 'comm'):
            self.comm.close()

    def send_ussd(self, com):
        command = 'AT+CUSD=1,"' + com + '",15'
        self.comm.send(command)
        cnt = 0
        while True:
            cnt += 1
            if cnt > ITERATION:
                break
            read = self.comm.read_raw(1024)
            if len(read) == 0:
                continue
            else:
                resp = read.decode(self.comm.byte_encoding).strip()
                if '+CUSD:' in resp:
                    resp = resp[:resp.rfind('"')]
                    resp = resp[resp.rfind('"') + 1:]
                    return decode16(resp)

    def check_sim(self):
        self.comm.send("AT+CPIN?")
        resp = self.comm.read_lines()
        return resp and 'READY' in resp[1]

    def get_oper(self):
        self.comm.send("AT+COPS?")
        resp = self.comm.read_lines()
        block = resp[1].split(",")
        if len(block) < 3:
            return "unknown"
        return block[2].strip('"').lower()

    def get_phone_cmun(self):
        self.comm.send("AT+CNUM")
        resp = self.comm.read_lines()
        if resp[1] == 'OK':
            return

        return resp[1].split(",")[1].strip('"')

    def get_myphone(self):
        self.comm.send("AT+CPBR=1,2")
        resp = self.comm.read_lines()
        if '"myphone"' in resp[1]:
            return resp[1].split(",")[1].strip('"')

    def ring(self, phone):
        self.comm.send("ATD"+phone+';')
        resp = self.comm.read_lines()
        return resp

    def get_number(self):
        if not self.check_sim():
            return
        # чистим память смс
        self.clear_sms()
        # пробуем быстрое получение номера
        p = self.get_phone_cmun()
        # иначе через оператора
        if not p:
            oper = self.get_oper()
            if "mts" in oper:
                p = self.clear_num(self.send_ussd('*111*0887#'))
                if not p:
                    p = self.get_sms_long()
                #p = self.send_ussd('*887#')
            elif "megafon" in oper:
                p = self.send_ussd('*205#')
            elif "beeline" in oper:
                # команда для d-mobile
                p = self.clear_num(self.send_ussd('*132*111#'))
                if not p:
                    p = self.clear_num(self.send_ussd('*110*10#'))
                    if not p:
                        p = self.get_sms_long()
            elif "tele2" in oper:
                p = self.send_ussd('*201#')
            elif "yota" in oper:
                p = self.send_ussd('*103#')
        # если нет смотрим в памяти симки
        if not p:
            p = self.get_myphone()

        return self.clear_num(p)

    @staticmethod
    def clear_num(num):
        if not num:
            return "Ошибка получения номера"
        emp_str = ""
        for m in num:
            if m.isdigit():
                emp_str = emp_str + m
                # если номер набрали, считаем пора заканчивать (для случая нескольких номеров)
                if len(emp_str) == 11:
                    return emp_str
        # если номер короткий значит ошибка
        if len(emp_str) < 10:
            return

        return "7" + emp_str if len(emp_str) < 11 else emp_str

    def get_sms_long(self):
        iter = 1
        while True:
            if iter > ITERATION:
                return False # для запроса повторной смс
            sms = self.get_sms_last()
            if sms:
                return sms
            iter += 1
            time.sleep(5)

    def sms_mode(self):
        self.comm.send("AT+CMGF=1")

    def clear_sms(self):
        self.sms_mode()
        self.comm.send("AT+CMGD=1,4")
        self.comm.read_lines()

    def get_sms_last(self):
        smslist = self.get_sms_list()
        if not smslist:
            return
        return smslist[-1]

    def get_sms_list(self):
        self.sms_mode()
        self.comm.send('AT+CMGL="REC UNREAD"')
        read = self.comm.read_lines()
        if not read:
            return
        # убираем все незначащее
        sms_lines = [x for x in read if len(x) > MIN_LEN]
        sms_list = []
        # ищем строки с содержимым смс
        for l in sms_lines:
            sms = None
            if ',' in l:
                blocks = [x for x in l.split(',') if len(x) > MIN_LEN]
                if blocks:
                    sms = decode16(blocks[0])
            else:
                sms = decode16(l)

            if sms:
                sms_list.append(sms)

        return sms_list

    def get_number_async(self):
        pass


if __name__ == "__main__":
    port = input('Введите порт')
    sim = SMS(port)
    print(sim.get_number())
