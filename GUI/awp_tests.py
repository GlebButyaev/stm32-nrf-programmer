#!/usr/bin/env python3
# This is a telematic AWP Python script.

import os
import time
import configparser
import requests
import json
import readchar
from alive_progress import alive_bar

import telematic_shell
from tests import tests, e_explorer, mqtt

# service_url = 'http://127.0.0.1:8000/'
service_url = 'http://172.40.40.1:9090/'
service_api = '-service/api/v1/'
conf_file = 'settings.ini'

clear = lambda: os.system('cls')

def get_device_dwauth(imsi: str) -> dict:
    try:
        headers = {
            'accept': 'application/json',
            # Already added when you pass json=
            # 'Content-Type': 'application/json',
        }
        json_data = {
            "imsi": imsi,
        }
        response = requests.post(service_url + 'dwauth' + service_api, headers=headers, json=json_data)
        if response.ok:
            # device_pass = response.json()["password"]
            return response.json()
    except Exception as E:
        raise E


def post_report(imsi: str, message: str) -> dict:
    try:
        headers = {
            'accept': 'application/json',
            # Already added when you pass json=
            # 'Content-Type': 'application/json',
        }
        json_data = {
            "imsi": imsi,
            "report": message,
        }
        response = requests.post(service_url + 'test' + service_api, headers=headers, json=json_data)
        if not response.ok:
            raise RuntimeError(response.text)
    except Exception as E:
        raise E
    else:
        return response.json()


def main_logic(config: configparser, shell: telematic_shell, report: dict) -> None:

    # STM32 test shell -------------------------------------------------------------------------------------------------
    print("Версия ПО телематики ", end='')
    fw_ver = shell.request("conf fw_vers", show_resp=True)
    if len(fw_ver) > 0:
        report["fw_ver"] = fw_ver[0]
    else:
        raise RuntimeError('Версия ПО SMT32 не определена')

    # определяем версию прошивки модема и imsi -------------------------------------------------------------------------
    modemsw = "не известно"
    dev_id = "не задан"
    try:
        shell.command('gsm init', 'Подключаем модем')
        try:
            modemsw = shell.request_and_parse_resp('gsm atcmd AT+CGMR', r'\+CGMR: (\w+)', 'Читаем версию ПО модема',
                                                   show_resp=False, wait=10.0)[0]
        except Exception as E:
            modemsw = "Ошибка! Невозможно получить версию ПО модема"
            print(str(E))
        try:
            dev_id = shell.request_and_parse_resp('gsm imsi', r'IMSI: (\d+)', 'Читаем IMSI', show_resp=False)
            dev_id = dev_id[0]
        except Exception as E:
            dev_id = "Ошибка! Невозможно получить IMSI, проверте работу модема, SIM чипа"
            print(str(E))
    finally:
        report['modemsw'] = modemsw
        print('Версия ПО модема: ' + modemsw)
        report["dev_id"] = dev_id
        print(f"IMSI: {dev_id}")
        shell.command('gsm off', 'Отключаем модем')


    # Get dwauth -------------------------------------------------------------------------------------------------------
    dwauth: dict = get_device_dwauth(dev_id)
    dev_pass = dwauth['password']
    if len(dev_pass) == 0:
        raise RuntimeError("Ошибка! Не удалось получить пароль для устройства, проверте соединение с сервером")
    else:
        # wait for mqtt pass activated
        with alive_bar(disable=False,
                       title='Активация MQTT', title_length=0,
                       length=15,
                       enrich_print=False,
                       monitor_end=False, stats_end=False, elapsed_end=False,
                       receipt=False, receipt_text=False,
                       manual=False) as bar:
            sleep_cnt = 10
            while sleep_cnt:
                time.sleep(1)
                sleep_cnt -= 1
                bar()

    # Create MQTT connection if need it --------------------------------------------------------------------------------
    mqtt_client = None
    if config.get("TESTS", "mqtt_send_receive_test") == "yes":
        mqtt_login = dwauth['client']
        mqtt_passw = dwauth['client_pwd']
        mqtt_client = mqtt.connect(
            'mqtt.center2m.com', 1883,
            mqtt_login, mqtt_passw
        )

    # STM32 initiate configuration -------------------------------------------------------------------------------------
    if config.get("SETTINGS", "update") == "yes":
        print("\n********************************************************************************************")
        print("инициализация настроек для проведения тестирования - старт")
        try:
            shell.update_cfg('initial.cfg', 'initial', dev_id, dev_pass)
            print("инициализация настроек для проведения тестирования - ок")
            res = "ok"
        except Exception as E:
            res = str(E)
            raise E
        finally:
            report["setcfg1"] = res

    # ==================================================================================================================
    # telematic shell tests --------------------------------------------------------------------------------------------
    print("\n********************************************************************************************")
    print("telematic shell tests - start")
    if config.get("TESTS", "mqtt_send_receive_test") == "yes":
        mqtt.subscribe(mqtt_client, dev_id)

    res = tests.make_tests(report, shell, config, pow_mon, mqtt_client, dev_id)
    if res == False:
        raise RuntimeError("Ошибка! Не менее чем 1 тест завершился с ошибкой")

    # ==================================================================================================================
    # STM32 finalize configuration -------------------------------------------------------------------------------------
    if config.get("SETTINGS", "update") == "yes":
        print("\n********************************************************************************************")
        print("инициализация настроек для складского хранения - старт")
        try:
            shell.update_cfg('final.cfg', 'fanal', dev_id, dev_pass)
            res = "ok"
        except Exception as E:
            res = str(E)
            raise E
        finally:
            report["setcfg2"] = res

        print("инициализация настроек для складского хранения - ok")

    # result -----------------------------------------------------------------------------------------------------------
    report["result"] = "Ok"


# ======================================================================================================================
if __name__ == '__main__':
    report = {"time": time.ctime()}
    try:
        config = configparser.ConfigParser()
        config.read(conf_file)

        service_url = config.get("COMMUNICATIONS", "author_center_url") + '/'

        comport = config.get("COMMUNICATIONS", "comport")
        shell = telematic_shell.Shell(comport)

        pow_mon_server_addr = config.get("COMMUNICATIONS", "pmon_url")
        if config.get("TESTS", "sleeping_power_test") == "yes" or \
           config.get("TESTS", "running_power_test") == "yes" or \
           config.get("TESTS", "sending_power_test") == "yes":
            pow_mon = e_explorer.PowMon(pow_mon_server_addr)  # проверка оборудования и подключений
            pow_mon.test_connection()  # проверка подключения к серверу монитора питания
        else:
            pow_mon = 'none'
        # АРМ осносной код ---------------------------------------------------------------------------------------------
        print("\n********************************************************************************************")
        print(  "* Автоматизированное рабочее местро (АРМ) по конфигурированию и тестированию\n")
        username = os.getlogin()

        while True:
            try:
                tmstamp = time.perf_counter()
                print('Установите устройство на стенд, подайте питание на устройство')
                input('по готовности - нажмите Enter\n')
                print("-----------------------------------------------------------------------------------")
                report.clear()
                report["operator"] = username
                main_logic(config, shell, report)
            except Exception as E:
                print("-----------------------------------------------------------------------------------")
                result = str(E)
                print(result)
                report["result"] = result
            print("\n********************************************************************************************")
            try:
                json_str = json.dumps(report, ensure_ascii=False).encode('utf-8')
            except Exception as E:
                json_str = '{"error": "make json error ' + str(E) + '"}'
                json_str = json_str.encode('utf-8')
                print("Encoding report:\n" + str(report) + "\nError:\n" + str(E))
            try:
                imsi = report["dev_id"]
            except Exception as E:
                imsi = "0"
            json_str = json_str.decode()
            print("json string: " + json_str)
            try:
                resp = post_report(imsi, json_str)
                print('Отчет', end=' ')
                if 'imsi' in resp:
                    print(f'по устройству {resp["imsi"]}', end=' ')
                print('сохранен')
            except Exception as E:
                print('Ошибка сохранения отчета: ' + str(E))
                raise E
            try:
                print('Работа с устройством ' + imsi + ' завершена')
            except:
                print('Работа с устройством завершена с ошибкой!')
            print(f'Затрачено {time.perf_counter() - tmstamp} секунд')
            print("\n********************************************************************************************")
            print('Отключите питание устройства, снимите устройство со стенда')
            print('Для продолжения работы нажмите - Y,\n')
            key = readchar.readchar().lower()
            if key != 'y':
                break
            config.read(conf_file)
            clear()
    except Exception as E:
        # print(str(E))
        exit(E)
