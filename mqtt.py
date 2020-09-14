# -*- encoding: utf-8 -*-

import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

from local_config import local_conf


# 电磁铁继电器pin
relay_pin = 37
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay_pin, GPIO.OUT)


class MqttClient():

    def __init__(self):
        self.client = mqtt.Client(local_conf.mqtt_broker['CLIENT'])
        self.client.on_message = self.on_message

    # 消息处理函数
    def on_message(self, client, user_data, msg):
        # 继电器闭合
        GPIO.output(relay_pin, 1)
        time.sleep(10)
        GPIO.output(relay_pin, 0)

    def mqtt_connect(self):
        self.client.connect(local_conf.mqtt_broker['HOST'], local_conf.mqtt_broker['PORT'], 60)

    def mqtt_subscribe(self, topic, qos=2):
        self.client.subscribe(topic=topic, qos=qos)
        self.client.loop_forever()


mqtt_cli = MqttClient()

def sub_watering_cmd():
    # 启动mqtt监听
    mqtt_cli.mqtt_connect()
    mqtt_cli.mqtt_subscribe(local_conf.mqtt_broker['SUB_TOPIC'])
