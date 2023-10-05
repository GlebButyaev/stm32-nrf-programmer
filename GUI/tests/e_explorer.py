#!/usr/bin/env python3
import time
import requests
from alive_progress import alive_bar


class PowMon:
    def __init__(self, url):
        self.url = url

    def test_connection(self):
        try:
            resp = requests.get(self.url + "/uMeter")
        except requests.ConnectionError as E:
            print("Проверка подключения к серверу монитора питания - ошибка!")
            print("Вероятная причина - не запущена программа EnergyExplorer или зоблокирован TCP порт")
            exit(E)
        return resp

    def post_cmd(self, command: str):
        # try:
        resp = requests.post(self.url + "/uMeter." + command)
        # except requests.ConnectionError as E:
        #     exit(E)
        return resp


    def make_aver_current(self, average_time: int):
        # print("uMeter.Start")
        resp = self.post_cmd("Start")
        if resp.ok:
            # print(f"ждем {average_time} секунд")
            with alive_bar(average_time) as bar:
                while average_time:
                    bar()
                    time.sleep(1)
                    average_time = average_time - 1
            # print("uMeter.GetCurData")
            resp = requests.get(self.url + "/uMeter.GetCurData")
            if resp.ok:
                uMeterCurVal = resp.json()
                # print(uMeterCurVal)
                avercurrent = int(uMeterCurVal['uAH_in']) * 3600000 / int(uMeterCurVal['time_ms'])
                # print("aver = " + str(avercurrent))
                # print("uMeter.Stop")
                self.post_cmd("Stop")
                return avercurrent
        return 0
