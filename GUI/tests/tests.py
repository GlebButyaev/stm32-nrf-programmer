#!/usr/bin/env python3
import configparser
import time
import readchar
import telematic_shell
from tests import e_explorer, mqtt

str_ok = 'ок'
str_error = 'ошибка'


def make_tests(report: dict, shell: telematic_shell, config: configparser, pow_mon: e_explorer, mqtt_client, dev_id) -> int:
    test_ok = True
    try:
        # тест питания 3.3В
        if config.get("TESTS", "dc_3v3_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                print("тест источника питания CPU (3.3 В):")
                dc_3v3 = int(shell.request_average_resp_data("afe vcc", r"(\d+) mV", counter=10)[0])
                print(f"{dc_3v3} мВ", end=', ')
                thres = int(config.get("TESTS", "dc_3v3_min"))
                if dc_3v3 < thres:
                    print(f"напряжение источника питания CPU ниже порога {thres} мВ", end=', ')
                    local_test_ok = False
                thres = int(config.get("TESTS", "dc_3v3_max"))
                if dc_3v3 > thres:
                    print(f"напряжение источника питания CPU превышает порог {thres} мВ", end=', ')
                    local_test_ok = False
                report["dc_3v3"] = dc_3v3
                if local_test_ok:
                    print(str_ok)
                    break
                else:
                    print(str_error + ' для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break


        # Тест питания 10,8 В
        if config.get("TESTS", "dc_vbat_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                print("тест источника питания Vbat (10.8 В):")
                vbat = int(shell.request_average_resp_data("afe vbat", r"(\d+) mV", counter=10)[0])
                print(f"{vbat} мВ", end=', ')
                thres = int(config.get("TESTS", "dc_vbat_min"))
                if vbat < thres:
                    print(f"напряжение батареи ниже порога {thres} мВ", end=', ')
                    local_test_ok = False
                thres = int(config.get("TESTS", "dc_vbat_max"))
                if vbat > thres:
                    print(f"напряжение батареи превышает порог {thres} мВ", end=', ')
                    local_test_ok = False
                report["vbat"] = vbat
                if local_test_ok:
                    print(str_ok)
                    break
                else:
                    print(str_error + ' для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # Тест часов
        if config.get("TESTS", "rtc_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                rtc = str_error
                try:
                    print("тест часов RTC: ", end='')
                    ret = shell.request_and_parse_resp("rtc gettime", r"\d+:\d+:(\d+)")
                    rtc_seconds_b: int = int(ret[0])
                    time.sleep(7.0)
                    ret = shell.request_and_parse_resp("rtc gettime", r"\d+:\d+:(\d+)")
                    rtc_seconds_e: int = int(ret[0])
                    delta = rtc_seconds_e - rtc_seconds_b
                    if delta < 0:
                        delta += 60
                    if 7 <= delta <= 9:
                        rtc = str_ok
                    else:
                        rtc = str_error
                        local_test_ok = False
                except Exception as E:
                    print(str(E))
                    rtc = 'ошибка алгоритма теста'
                    local_test_ok = False
                finally:
                    report["rtc"] = rtc
                    print(f"{rtc}")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # Тест датчика магнитного поля
        if config.get("TESTS", "hall_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                try:
                    print("тест датчика магнитного поля")
                    input("уберите магнит от датчика и нажмите Enter")
                    hall = "ок"
                    res = shell.request_and_parse_resp("afe h", r"absent")
                    if len(res)==0 or res[0] != 'absent':
                        hall = str_error
                        test_ok = False
                    input("поднесите магнит к датчику и нажмите Enter")
                    res = shell.request_and_parse_resp("afe h", r"detected")
                    if len(res)==0 or res[0] != 'detected':
                        hall = str_error
                        local_test_ok = False
                except Exception as E:
                    print(str(E))
                    hall = 'ошибка алгоритма теста'
                    local_test_ok = False
                finally:
                    report["hall"] = hall
                    print(f"{hall}")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # Тест акселерометра
        if config.get("TESTS", "accel_test") == "yes" or config.get("TESTS", "tempr_test") == "yes":
            while True:
                local_test_ok = True
                res = shell.request_average_accel_data()
                if config.get("TESTS", "accel_test") == "yes":
                    report["accel"]={}
                    print("-----------------------------------------------------------------------------------")
                    x_axis_min = int(config.get("TESTS", "x_axis_min"))
                    x_axis_max = int(config.get("TESTS", "x_axis_max"))
                    if x_axis_min < res[0] < x_axis_max:
                        accel_x_axis_res = str_ok
                    else:
                        accel_x_axis_res = str_error
                        local_test_ok = False
                    report["accel"]['x'] = {"val": res[0], "result": accel_x_axis_res}
                    y_axis_min = int(config.get("TESTS", "y_axis_min"))
                    y_axis_max = int(config.get("TESTS", "y_axis_max"))
                    if y_axis_min < res[1] < y_axis_max:
                        accel_y_axis_res = str_ok
                    else:
                        accel_y_axis_res = str_error
                        local_test_ok = False
                    report["accel"]['y'] = {"val": res[1], "result": accel_y_axis_res}
                    z_axis_min = int(config.get("TESTS", "z_axis_min"))
                    z_axis_max = int(config.get("TESTS", "z_axis_max"))
                    if z_axis_min < res[2] < z_axis_max:
                        accel_z_axis_res = str_ok
                    else:
                        accel_z_axis_res = str_error
                        local_test_ok = False
                    report["accel"]['z'] = {"val": res[1], "result": accel_z_axis_res}
                    print(f'Тест акселерометра: x={res[0]}-{accel_x_axis_res}, y={res[1]}-{accel_y_axis_res}, z={res[2]}-{accel_z_axis_res}')
                if config.get("TESTS", "tempr_test") == "yes":
                    print("-----------------------------------------------------------------------------------")
                    print(f'Тест датчика температуры: t={res[3]} ', end='')
                    tempr_min = int(config.get("TESTS", "tempr_min"))
                    tempr_max = int(config.get("TESTS", "tempr_max"))
                    if tempr_min <= res[3] <= tempr_max:
                        t_res = str_ok
                    else:
                        t_res = str_error
                        local_test_ok = False
                    report["t"] = {"val": res[3], "result": t_res}
                    print(t_res)
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # Тест GPS
        if config.get("TESTS", "gps_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                try:
                    # print("тест GPS:")
                    res = shell.request_gps_test_gnss_present(title='тест GPS:', show_resp=True)
                    if res < 0:
                        gps_res = str_error
                        local_test_ok = False
                    else:
                        gps_res = str_ok
                except Exception as E:
                    local_test_ok = False
                    gps_res = str(E)
                finally:
                    report["gps"] = gps_res
                    print(f"{gps_res}")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # Тест связи с RFID
        if config.get("TESTS", "rfid_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                try:
                    print("тест RFID: ")
                    res = shell.request('em4325 status', show_resp=True, wait=3.0)
                    if len(res) > 2:
                        status = int(res[0], 16)
                        if status == 0x00:
                            local_test_ok = False
                            rfid_res = str_error
                        if status & 0xC0 == 0xC0:
                            rfid_res = str_ok
                    else:
                        rfid_res = str_error
                        local_test_ok = False
                except Exception as E:
                    local_test_ok = False
                    rfid_res = str(E)
                finally:
                    report["rfid"] = rfid_res
                    print(f"{rfid_res}")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # Тест связи с nRF (uart эхо тест)
        if config.get("TESTS", "nrf_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                try:
                    print("тест BLE: ")
                    ble_res = str_error
                    res = shell.request('bt tstuart hellow', wait=1)
                    for line in res:
                        if line.find('hellow') > 0:
                            ble_res = str_ok
                            break
                    if not (ble_res == str_ok):
                        local_test_ok = False
                except Exception as E:
                    ble_res = str(E)
                    local_test_ok = False
                finally:
                    report["ble"] = ble_res
                    print(f"{ble_res}")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # Тест ext flash на наличие
        if config.get("TESTS", "extflash_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                try:
                    print("тест flash памяти: ")
                    res = shell.request('extflash jedec', show_resp=True, wait=2.0)
                    if len(res) > 0:
                        if res[0].find('DeviceType 26') > 0:
                            flash_res = str_ok
                        else:
                            flash_res = str_error
                            local_test_ok = False
                except Exception as E:
                    local_test_ok = False
                    flash_res = str(E)
                finally:
                    report["extflash"] = flash_res
                    print(f"{flash_res}")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # power consumption test, start condition ----------------------------------------------------------------------
        have_power_tests: bool = \
           config.get("TESTS", "sleeping_power_test") == "yes" or \
           config.get("TESTS", "running_power_test") == "yes" or \
           config.get("TESTS", "sending_power_test") == "yes"
        if have_power_tests:
            pow_mon.post_cmd("Stop")
            report["power"] = {}  # add empty dict

        # power consumption test (sleep mode) --------------------------------------------------------------------------
        if config.get("TESTS", "sleeping_power_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                print("Тест энергопотребления (режим сна)")
                average_time = int(config.get("TESTS", "sleeping_aver_sec"))
                current_threshold = int(config.get("TESTS", "sleeping_aver_threshold"))
                sleep_time = average_time + 2
                shell.request(f"sleep {sleep_time}")
                time.sleep(0.500)
                ACurrent = int(pow_mon.make_aver_current(average_time))
                if ACurrent > current_threshold:
                    local_test_ok = False
                    consumption_res = "ПРЕВЫШЕН ПОРОГ ПОТРЕБЛННИЯ!!!"
                    report["power"]["sleeping"] = {"status": "overpower", "value": ACurrent}
                    print("ПРЕВЫШЕН ПОРОГ ПОТРЕБЛННИЯ!!!")
                else:
                    consumption_res = "норма"
                    report["power"]["sleeping"] = {"status": str_ok, "value": ACurrent}
                time.sleep(1.500)
                print(f"\tТок потребления в режиме сна = {ACurrent} мкА,  [" + consumption_res + "]")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # power consumption test (running mode) ---------------------------------------------------------------------------
        if config.get("TESTS", "sleeping_power_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                print("тест энергопотребления (рабочий режим)")
                average_time = int(config.get("TESTS", "running_aver_sec"))
                current_threshold = int(config.get("TESTS", "running_aver_threshold"))
                ACurrent = int(pow_mon.make_aver_current(average_time))
                if ACurrent > current_threshold:
                    local_test_ok = False
                    consumption_res = "ПРЕВЫШЕН ПОРОГ ПОТРЕБЛННИЯ!!!"
                    report["power"]["running"] = {"status": "overpower", "value": ACurrent}
                    print("ПРЕВЫШЕН ПОРОГ ПОТРЕБЛННИЯ!!!")
                else:
                    consumption_res = "норма"
                    report["power"]["running"] = {"status": str_ok, "value": ACurrent}
                print(f"\tТок потребления в рабочем режиме = {ACurrent} мкА, [" + consumption_res + "]")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break

        # power consumption test (sending mode) ----------------------------------------------------------------------------
        # дополнительно тест передачи данных на сервер
        if config.get("TESTS", "mqtt_send_receive_test") == "yes":
            mqtt.subscribe(mqtt_client, dev_id)
            #TODO проверить резельтат подключения к MQTT, сообщить об ошибке подключения
        if config.get("TESTS", "sending_power_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                print("Тест энергопотребления (режим передачи данных)")
                average_time = int(config.get("TESTS", "sending_aver_sec"))
                current_threshold = int(config.get("TESTS", "sending_aver_threshold"))
                shell.request("bl_test_job")
                ACurrent = int(pow_mon.make_aver_current(average_time))
                if ACurrent > current_threshold:
                    local_test_ok = False
                    consumption_res = "ПРЕВЫШЕН ПОРОГ ПОТРЕБЛННИЯ!!!"
                    report["power"]["sending"] = {"status": "overpower", "value": ACurrent}
                    print("ПРЕВЫШЕН ПОРОГ ПОТРЕБЛННИЯ!!!")
                else:
                    consumption_res = "норма"
                    report["power"]["sending"] = {"status": str_ok, "value": ACurrent}
                print(f"\tТок потребления в режиме передачи данных = {ACurrent} мкА, [" + consumption_res + "]")
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break
        else:  # if sending_power_test = no
            if config.get("TESTS", "mqtt_send_receive_test") == "yes":
                shell.request("bl_test_job")
        # MQTT (test topic publish ) -----------------------------------------------------------------------------------
        if config.get("TESTS", "mqtt_send_receive_test") == "yes":
            while True:
                local_test_ok = True
                print("-----------------------------------------------------------------------------------")
                print("Тест передачи данных на MQTT")
                try:
                    res: int = mqtt.wait_topic_msg(mqtt_client, 90)
                    mqtt.unsubscribe(mqtt_client, dev_id)
                    if res == 1:
                        report["mqtt"] = str_ok
                        print("Тест передачи данных на MQTT: " + str_ok)
                    else:
                        local_test_ok = False
                        report["mqtt"] = str_error
                        print("Тест передачи данных на MQTT: " + str_error)
                except Exception as E:
                    local_test_ok = False
                    report["mqtt"] = str(E)
                    print(str_error)
                if local_test_ok:
                    break
                else:
                    print('для повтора нажмите - Y\n')
                    key = readchar.readchar().lower()
                    if key != 'y':
                        test_ok = False
                        break
                    else:
                        shell.request("bl_test_job")
        print("telematic shell tests - end")
    except Exception as E:
        test_ok = False
        raise E
    finally:
        return test_ok
