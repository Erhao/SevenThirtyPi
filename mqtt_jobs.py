# -*- encoding: utf-8 -*-

import time

from mqtt_client import MqttClient
from soil_moisture import detect_dry_or_wet
from stpi_config import stpi_config
from local_config import local_conf
from DHT11 import get_temp_humi


def sub_watering_cmd():
    """ 启动mqtt监听 """

    mqtt_cli2 = MqttClient('sub_watering_cmd')
    mqtt_cli2.mqtt_connect()
    mqtt_cli2.mqtt_subscribe(local_conf.mqtt_broker['SUB_WATERING_TOPIC'])


def pub_soil_moisture():
    """ 发布土壤湿度信息 """

    mqtt_cli = MqttClient('pub_soil_moisture')
    mqtt_cli.mqtt_connect()
    soil_moisture = detect_dry_or_wet() or '1'
    topic = local_conf.mqtt_broker['PUB_SOIL_MOISTURE_TOPIC_PREFIX'] +\
        stpi_config.PLANT_ID +\
        '/' +\
        str(int(time.time()))
    mqtt_cli.mqtt_publish(topic, soil_moisture, qos=2)
    return


def pub_temp_humi():
    """ 发布温湿度信息 """

    temp, humi = get_temp_humi()
    if not temp and not humi:
        return
    mqtt_cli = MqttClient('pub_soil_moisture')
    mqtt_cli.mqtt_connect()
    topic = local_conf.mqtt_broker['PUB_TEMP_HUMI_TOPIC_PREFIX'] +\
        stpi_config.PLANT_ID +\
        '/' +\
        str(int(time.time()))
    payload = str(int(temp)) + '_' + str(int(humi))
    mqtt_cli.mqtt_publish(topic, payload, qos=2)
    return
