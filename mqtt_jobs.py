# -*- encoding: utf-8 -*-

import time

from mqtt_client import MqttClient
from soil_moisture import detect_dry_or_wet
from stpi_config import stpi_config
from local_config import local_conf


def sub_watering_cmd():
    # 启动mqtt监听
    mqtt_cli2 = MqttClient('sub_watering_cmd')
    mqtt_cli2.mqtt_connect()
    mqtt_cli2.mqtt_subscribe(local_conf.mqtt_broker['SUB_WATERING_TOPIC'])

def pub_soil_moisture():
    mqtt_cli = MqttClient('pub_soil_moisture')
    mqtt_cli.mqtt_connect()
    soil_moisture = detect_dry_or_wet() or '1'
    print('---------------soil_moisture', soil_moisture)
    topic = local_conf.mqtt_broker['PUB_SOIL_MOISTURE_TOPIC_PREFIX'] +\
        stpi_config.PLANT_ID +\
        '/' +\
        str(int(time.time()))
    mqtt_cli.mqtt_publish(topic, soil_moisture, qos=2)
    print('----------发布成功')
    return