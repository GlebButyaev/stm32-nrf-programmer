import paho.mqtt.client as mqtt
import time
from alive_progress import alive_bar
from tests import wagon_001_pb2


_f_get_message: int = 0

def parse_msg_dat(extended_data):
    read_data.ParseFromString(extended_data)
    try:
        extended_data = {
            "device_id": read_data.device_id,
            "pack_id": read_data.pack_id,
            "rwcarfw": read_data.rw_car_fw_version,
            "mestypeid": read_data.mestypeid,
            "packtime": read_data.time,
            "packtime_pars": time.strftime("%d-%m-%Y  %H:%M:%S %z", time.localtime(read_data.time)),
            "location": [float('{:.6f}'.format(read_data.lat/1000000)), float('{:.6f}'.format(read_data.lon/1000000))],
            "velocity": float('{:.3f}'.format(read_data.velocity/10)),#*3600/1000)),
            "direction": float('{:.3f}'.format(read_data.direction/1000)),
            "temperature": read_data.temperature,
            "batmain": read_data.batmain,
            "rssi": read_data.rssi,
            "g_range": read_data.g_range,
            "g_freq": read_data.g_freq,
            "g_time": read_data.g_time,
            "accel_forward":  list(read_data.accel_forward), 
            "accel_vertical":  list(read_data.accel_vertical),
            "accel_transverse": list(read_data.accel_transverse),
            "imsi": read_data.imsi,
            "accel_result": -1,
            "accel_result_txt":"undefine",
            "batgw1": read_data.batgw1,
            "tcargo": float('{:.3f}'.format(read_data.tcargo/1000)),
            "pcargo": float('{:.3f}'.format(read_data.pcargo/1000)),
            "vcargo": float('{:.3f}'.format(read_data.vcargo/1000))
        }

        if len(extended_data['device_id']) < 1:
            raise Exception("to short device_id")
        else:
            return extended_data
            # print(colored(extended_data,'green'))
            # print("\r\n")

    except Exception as err:
        print(f"payload decode error as {err}")


def on_message(client, userdata, msg):
    global _f_get_message
    if not ('testwagon' in msg.topic):
        print('Error topic {}'.format(msg.topic))
        return None

    dbg_log = "mess= " + msg.topic + "\n"
    dbg_log += "receiving date_time: " + time.strftime("%d-%m-%Y  %H:%M:%S", time.localtime()) + "\n"
    
    if 'testdat' in msg.topic:
        dbg_log += str(parse_msg_dat(msg.payload))
        _f_get_message = 1

    dbg_log += "\r\n"
    print(dbg_log)


read_data = wagon_001_pb2.WagonDeviceData()


def connect(host, port, mqtt_user, mqtt_passw) -> mqtt.Client:
    client = mqtt.Client(client_id=mqtt_user)
    # client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(mqtt_user, password=mqtt_passw)
    try:
        client.connect_async(host, port, 60)
        client.loop_start()
    except ConnectionRefusedError as e:
        print(f'Error connect to MQTT: {e}')
    tm = time.perf_counter()
    tmout = 20.0
    elapsed = 0
    with alive_bar(title='MQTT > ждем подключения', length=15,
                   enrich_print=False,
                   monitor_end=False, stats_end=False, elapsed_end=False,
                   receipt=False, receipt_text=False, manual=True) as bar:
        while (not client.is_connected()) and (elapsed < tmout):
            time.sleep(1)
            elapsed = time.perf_counter() - tm
            bar(elapsed / tmout)
    return client


def disconnect(client):
    client.loop_stop()
    return client.disconnect()


def subscribe(client, dev_id):
    global _f_get_message
    topic = f'testwagon/{dev_id}/testdat'
    _f_get_message = 0
    return client.subscribe(topic)


def unsubscribe(client, dev_id):
    global _f_get_message
    topic = f'testwagon/{dev_id}/dat'
    _f_get_message = 0
    return client.unsubscribe(topic)


def wait_topic_msg(client, tmout):
    global _f_get_message
    tm = time.perf_counter()
    with alive_bar(title='MQTT > ждем сообщения от устройства', length=15,
                   enrich_print=False,
                   monitor_end=False, stats_end=False, elapsed_end=False,
                   receipt=False, receipt_text=False, manual=True) as bar:
        elapsed = time.perf_counter() - tm
        while client.is_connected() and (not _f_get_message) and (elapsed < tmout):
            time.sleep(1)
            elapsed = time.perf_counter() - tm
            bar(elapsed / tmout)
    # client.unsubscribe(topic)
    return _f_get_message


# if __name__ == '__main__':
    # client = connect('mqtt.center2m.com', 1883, 'arm3', 'rENDqw')
    # print(client.is_connected())
    # res = subscribe(client, '250510200025677')
    # # res = client.subscribe('testwagon/+/testdat')
    # print(f'subsrcibe to testwagon, result: {res}')
    # res = wait_topic_msg(client, 90)
    # print(f'is message getted {res}')
    # unsubscribe(client, '250510200025677')
    # # client.unsubscribe('testwagon/#')
    # disconnect(client)

##########################################

