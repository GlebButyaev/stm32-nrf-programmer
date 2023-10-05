#!/usr/bin/env python3
# This is a telematic AWP Python script.

import os
import time
import configparser
import requests
import json
import readchar
import telematic_shell
from alive_progress import alive_bar
from prog.proghelper import stmprog, nrfprog

# service_url = 'http://127.0.0.1:8000/'
service_url = 'http://172.40.40.1:9090/'
service_api = '-service/api/v1/'
conf_file = 'settings.ini'

clear = lambda: os.system('cls')


def post_report(imsi: str, message: str):
    try:
        headers = {
            'accept': 'application/json',
            # Already added when you pass json=
            # 'Content-Type': 'application/json',
        }
        json_data = {
            'imsi': imsi,
            'report': message,
        }
        response = requests.post(service_url + 'prog' + service_api, headers=headers, json=json_data)
        if not response.ok:
            raise RuntimeError(response.text)
    except Exception as E:
        raise E
    else:
        return response.json()


def main_logic(config: configparser, shell: telematic_shell, report: dict) -> None:
    report["progfw"] = {}  # add empty dict
    # STM32 programming ------------------------------------------------------------------------------------------------
    if config.get("PROGRAMMING", "stm_prog") == "yes":
        while True:
            try:
                print("\n********************************************************************************************")
                print("Программирование STM32")
                stmprog(report, config)
            except Exception as E:
                print(f'------------------------------------\
                \nВо время программирования STM32 возникла ошибка "{str(E)}"\
                \nДля повторения нажмите - Y: ')
                key = readchar.readchar().lower()
                if key =='y':
                    continue
                raise E
            else:
                break

    # nRF programming --------------------------------------------------------------------------------------------------
    if config.get("PROGRAMMING", "nrf_prog") == "yes":
        while True:
            try:
                print("\n********************************************************************************************")
                print("Программирование nRF")
                nrfprog(report, config)
            except Exception as E:
                print(f'------------------------------------\
                \nВо время программирования nRF возникла ошибка "{str(E)}",\
                \nдля повторения нажмите - Y: ')
                key = readchar.readchar().lower()
                if key =='y':
                    continue
                raise E
            else:
                break

    # stm and/or nrf programming ending procedure
    if config.get("PROGRAMMING", "stm_prog") == "yes" or \
            config.get("PROGRAMMING", "nrf_prog") == "yes":
        print("\n********************************************************************************************")
        input("Внимание! Отключите питание, отключите программаторы (ST-Link и J-Link), нажмите Enter")
        # time.sleep(3)
        print("\n********************************************************************************************")
        input("Внимание! Подключите питание, нажмите Enter")
        with alive_bar(title='Ожидаем запуска телематики ', title_length=0,
                       length=15,
                       #enrich_print=False,
                       monitor_end=False, stats_end=False, elapsed_end=False,
                       receipt=False, receipt_text=False,
                       manual=True) as bar:
            wait_tm = 0
            while wait_tm < 25:
                time.sleep(0.5)
                wait_tm += 0.5
                bar(wait_tm/25)

    # STM32 test shell -------------------------------------------------------------------------------------------------
    print("\n********************************************************************************************")
    print("Версия ПО телематики ", end='')
    fw_ver = shell.request("conf fw_vers", show_resp=True)
    if len(fw_ver) > 0:
        report["fw_ver"] = fw_ver[0]
    else:
        raise RuntimeError('Версия ПО SMT32 не определена')

    # modem SW update --------------------------------------------------------------------------------------------------
    if config.get("PROGRAMMING", "modem_prog") == "yes":
        print("\n********************************************************************************************")
        print("modem SW update - started")
        try:
            res = shell.simcom_prog()
        except Exception as E:
            res = str(E)
        finally:
            report["fwupgrade"] = {"modem": res}

    # определяем версию прошивки модема и imsi -------------------------------------------------------------------------
    print("\n********************************************************************************************")
    modemsw = "не известно"
    dev_id = "не задан"
    try:
        shell.command('gsm init')
        try:
            modemsw = shell.request_and_parse_resp('gsm atcmd AT+CGMR', r'\+CGMR: (\w+)', wait=10.0)[0]
        except Exception as E:
            modemsw = "Ошибка! Невозможно получить версию ПО модема"
            print(str(E))
        try:
            dev_id = shell.request_and_parse_resp('gsm imsi', r'IMSI: (\d+)')
            dev_id = dev_id[0]
        except Exception as E:
            dev_id = "Ошибка! Невозможно получить IMSI, проверте работу модема, SIM чипа"
            print(str(E))
    finally:
        report['modemsw'] = modemsw
        print('Версия ПО модема: ' + modemsw)
        report["dev_id"] = dev_id
        print(f"imsi {dev_id}")
        shell.command('gsm off')

    # result -----------------------------------------------------------------------------------------------------------
    report["result"] = "Ok"


# ======================================================================================================================
if __name__ == '__main__':
    report = {"time": time.ctime()}
    try:
        config = configparser.ConfigParser()
        config.read(conf_file)

        service_url = config.get("COMMUNICATIONS", "author_center_url") + '/'

        pow_mon_server_addr = config.get("COMMUNICATIONS", "pmon_url")

        comport = config.get("COMMUNICATIONS", "comport")
        shell = telematic_shell.Shell(comport)

        # АРМ осносной код ---------------------------------------------------------------------------------------------
        print("\n********************************************************************************************")
        print("* Автоматизированное рабочее местро (АРМ) по программированию\n")
        username = os.getlogin()

        while True:
            try:
                tmstamp = time.perf_counter()
                print('Установите устройство на стенд, подайте питание на устройство')
                input('по готовности - нажмите Enter\n')
                report.clear()
                report["operator"] = username
                main_logic(config, shell, report)
            except Exception as E:
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
            print("Отчет: " + json_str)
            try:
                resp = post_report(imsi, json_str)
                print('Отчет', end=' ')
                if 'imsi' in resp:
                    print(f'по устройству {resp["imsi"]}', end=' ')
                print('сохранен')
            except Exception as E:
                print('Ошибка сохранения результата работы: ' + str(E))
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
