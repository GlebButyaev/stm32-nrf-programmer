#!/usr/bin/env python3
import os
import serial
import time
import re
from alive_progress import alive_bar


def _check_gps_polling(serial, line, req):
    f_need_stop_gps: bool = False
    if line.find('MT3333') >= 0:
        f_need_stop_gps = req.find('gps show 1') < 0
        if f_need_stop_gps:
            print('мониторинг GNSS запущен и мешает проводить тестирование - отключаем!')
        if req.find('gps on') < 0:
            serial.write('gps off\n'.encode())
            serial.readline()  # echo
            serial.readline()  # resp
            serial.write('gps show 0\n'.encode())
            serial.readline()  # echo
            serial.readline()  # resp
    return f_need_stop_gps


class Shell:
    def __init__(self, comport: str):
        self.comport = comport
        self.baudrate = int(115200)
        self.stopbits = int(1)
        self.bytesize = int(8)
        self.timeout = float(1.000)
        self.parity = serial.PARITY_NONE

    def request(self, req: str, title: str = '', show_cmd=False, show_resp=False, wait: float = 1.0, nested=False):
        if wait == 0.0:
            wait = 1.0  # default
        req = req.rstrip('\n')
        bar_title = ''
        if len(title):
            bar_title += title + ': '
        if show_cmd:
            bar_title += req
        req = req + '\n'
        ser = serial.Serial(self.comport, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout)
        ser.flush()
        answer = []
        try:
            ser.write(req.encode())
            ser.readline()  # echo
            stamp = time.perf_counter()
            if wait < 3.0 or nested:
                disable_bar = True
            else:
                disable_bar = False
            f_repeat_q = False
            with alive_bar(disable=disable_bar,
                           title=bar_title, title_length=0,
                           length=15,
                           enrich_print=False,
                           monitor_end=False, stats_end=False, elapsed_end=False,
                           receipt=False, receipt_text=False,
                           manual=True) as bar:
                while True:
                    line = ser.readline().decode('ascii').rstrip('\n')
                    passed = time.perf_counter() - stamp
                    progress = passed / wait
                    if progress > 1.0:
                        progress = 1.0
                    if len(line):
                        if line == '>' or line == '> ':
                            progress = 1.0
                        else:
                            answer.append(line)
                    bar(progress)
                    if progress >= 1.0:
                        # проверка GPS трафика и наличие команды его вызвавшей, отключение если команды не было
                        f_repeat_q = _check_gps_polling(ser, line, req)
                        if f_repeat_q and (not nested):
                            ser.close()
                            break
                        else:
                            f_repeat_q = False
                        if len(line) == 0 and len(answer) == 0:
                            res = "плата не отвечает на запрос: " + req.rstrip('\n')
                            print(res)
                            raise RuntimeError(res)
                        f_show_single_answer = show_resp and (len(answer) == 1)
                        if show_cmd:
                            print(bar_title, end=' >> ' if f_show_single_answer else '\n')
                        elif len(title):
                            print(title, end=': >> ' if f_show_single_answer else '\n')
                        if show_resp:
                            preambule: str = '' if len(answer) == 1 else '>> '
                            for item in answer:
                                print(preambule + item)
                        break
            if f_repeat_q:
                return self.request(req=req, title=title, show_cmd=show_cmd, show_resp=show_resp, wait=wait, nested=True)
        finally:
            ser.close()
        return answer

    def command(self, req, title='', show_cmd=False, show_resp=False):
        if req.find("gsm init") >= 0:
            resp = self.request(req=req, title=title, show_cmd=show_cmd, show_resp=show_resp, wait=25.0)
            for line in resp:
                if line.find("Modem initialization succesfull") >= 0:
                    return line
                if line.find("Modem initialization failed") >= 0:
                    raise RuntimeError("инициализация модема провалена")
        elif req.find("gsm off") >= 0:
            resp = self.request(req=req, title=title, show_cmd=show_cmd, show_resp=show_resp, wait=5.0)
            for line in resp:
                if line.find("GSM modem switch off") >= 0 or \
                        line.find("GSM modem not inited") >= 0:
                    return line
        elif req.find("gsm boot_on") >= 0:
            resp = self.request(req=req, title=title, show_cmd=show_cmd, show_resp=show_resp, wait=15.0)
            for line in resp:
                if line.find("Boot mode ON") >= 0:
                    return line
        elif req.find("gsm boot_off") >= 0:
            resp = self.request(req=req, title=title, show_cmd=show_cmd, show_resp=show_resp, wait=5.0)
            for line in resp:
                if line.find("Boot mode OFF") >= 0:
                    return line
        raise RuntimeError("unknown command: " + req)

    def request_and_parse_resp(self, req, pattern, title='', show_cmd=False, show_resp=False, wait: float=1):
        resp = self.request(req, title=title, show_cmd=show_cmd, show_resp=show_resp, wait=wait)
        for line in resp:
            parsed = re.findall(pattern, line)
            if len(parsed):
                break
        return parsed

    def request_average_resp_data(self, req, pattern, title='', counter: int = 1, show_req=False, show_resp=False):
        summ: int = 0
        if counter == 0:
            counter = 1
        divider = counter
        baselist = self.request_and_parse_resp(req, pattern, title, show_req, show_resp)
        while counter:
            newlist = self.request_and_parse_resp(req, pattern, title, show_req, show_resp)
            for i, x in enumerate(baselist):
                x = int(x) + int(newlist[i])
            counter -= 1
        for i, x in enumerate(baselist):
            x = int(x) / divider
        return baselist

    def request_average_accel_data(self, title='', show_resp=False):
        summ: int = 0
        resp = self.request("accel run", title, show_cmd=False, show_resp=show_resp, wait=5)
        uload_str = resp[0]
        divider = re.findall(r'upload (\d+)', uload_str)
        divider = int(divider[0])
        if divider == 0:
            divider = 1
        int_x = 0
        int_y = 0
        int_z = 0
        int_t = 0
        for i in range(2, len(resp)):
            c, tmp, x, y, z, t = \
            re.findall(r'-> \s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)', resp[i])[0]
            int_x += int(x)
            int_y += int(y)
            int_z += int(z)
            int_t += int(t)
        int_x /= divider
        int_y /= divider
        int_z /= divider
        int_t /= divider
        return [int_x, int_y, int_z, int_t]

    def request_gps_test_gnss_present(self, title='', show_resp=False):
        self.request('gps on', title, show_cmd=True, show_resp=show_resp, wait=2)
        resp = self.request('gps show 1', title, show_cmd=True, show_resp=show_resp, wait=5)
        for i in range(2, len(resp)):
            gga = re.findall(r'\$(\w{2}GGA)', resp[i])
            if len(gga) > 0:
                return 0
        # not need make gps off, function 'request' make it off self
        return -1

    def update_cfg(self, file, title='', dev_id='', dev_pass=''):
        try:
            file_path = 'tests/'
            F = open(file_path + file)
        except OSError:
            RuntimeError(f"ошибка открытия файла настроек: {os.getcwd() + '/' + file_path + file}")
        else:
            s = F.readlines()
            f_conf_changed = False
            for i in range(0, len(s)):
                req = s[i].strip()
                comment_pos = req.find('#')
                if comment_pos >= 0:
                    req = req[:comment_pos]  # delete comment
                equal_sign_pos = req.find('=')
                if equal_sign_pos > 0:
                    # change sign '=' to ' '
                    if req[:equal_sign_pos] == "dev_id":
                        if len(dev_id) > 0:
                            req = "dev_id " + dev_id
                        else:
                            req = req[:equal_sign_pos] + " " + req[equal_sign_pos + 1:]  # change sign '=' to ' '
                    elif req[:equal_sign_pos] == "passw":
                        if len(dev_pass) > 0:
                            req = "passw " + dev_pass.strip()
                        else:
                            req = req[:equal_sign_pos] + " " + req[equal_sign_pos + 1:]  # change sign '=' to ' '
                    else:
                        req = req[:equal_sign_pos] + " " + req[equal_sign_pos + 1:]  # change sign '=' to ' '
                if len(req) > 0:
                    answer = self.request("conf set " + req, title, False, True)
                    f_conf_changed = True
                    # print("\tconf set " + req)
                    if len(answer) == 0:
                        RuntimeError("Error: ответ на 'conf set" + req + " отсутствует!")
            if f_conf_changed:
                self.request("conf save", title, True, True)

    def simcom_prog(self, title) -> str:
        self.request("gsm boot_on", title, True, True)
        mprog = ""
        while mprog.upper() != "Y" and mprog.upper() != "N":
            mprog = input("Дождитесь обновления модема и нажмите:"
                          "\n\t'Y' - в случае успеха или"
                          "\n\t'N' - в случае ошибки.\n")
        self.request("gsm boot_off", title, True, True)
        if mprog.upper() == "N":
            print("Обновление прошивки модема завершилось ОШИБКОЙ!")
            # report["fwupgrade"] = {"modem": "error"}
            # raise RuntimeError("Обновление прошивки модема завершилось ОШИБКОЙ!")
            return "ошибка"
        # report["fwupgrade"] = {"modem": "ok"}
        input("Отключите разъем программирования модема\n  после отключения нажмите Enter")
        print("Перезапуск модема после обновления ПО")
        self.request("gsm init", title, True, True)
        print("Выключение модема")
        self.request("gsm off", title, True, True)
        print("modem SW update - ok")
        return "ок"


# local tests
if __name__ == '__main__':
    test_alive_bar = False
    test_telematic_shell = False
    test_bt_shell = False
    test_request_and_parse_resp = True
    #
    if test_alive_bar:
        with alive_bar(disable=False, title="bar_title", title_length=0,
                       length=10,
                       enrich_print=False,
                       monitor_end=False, stats_end=False, elapsed_end=False,
                       receipt=False, receipt_text=True,
                       manual=True) as bar:
            stamp = time.perf_counter()
            while True:
                passed = time.perf_counter() - stamp
                progress = passed / 1.0
                if progress >= 1.0:
                    progress = 1.0
                    bar.text = 'test msg'
                    bar(progress)
                    print('progress reach 100%')
                    break
                bar(progress)
        print('next text')
    #
    if test_telematic_shell:
        shell = Shell('COM3')
        fw_ver = shell.request("conf fw_vers", "Версия ПО телематики", show_cmd=True, show_resp=True)
        if len(fw_ver) > 0:
            print("Версия ПО телематики ", fw_ver[0])
        else:
            raise RuntimeError('Версия ПО SMT32 не определена')
        #
        res = shell.request_gps_test_gnss_present('test GNSS', True)
        print(res)
        #
        res = shell.request_average_accel_data('тест датчика ускорений', True)
        print(res)
    #
    if test_bt_shell:
        shell = Shell('COM3')
        ble_res = "ошибка"
        try:
            print("тест BLE: ")
            res = shell.request('bt tstuart hellow', wait=2.0)
            for line in res:
                if line.find('hellow') > 0:
                    ble_res = 'ок'
                    break
        except Exception as E:
            ble_res = str(E)
        finally:
            print(f"{ble_res}")
            if not (ble_res == 'ok'):
                test_ok = False
    #
    if test_request_and_parse_resp:
        shell = Shell('COM3')
        res = shell.request_and_parse_resp("afe h", r"absent")
        print(res)
