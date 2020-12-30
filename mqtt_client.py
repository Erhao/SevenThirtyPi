# -*- encoding: utf-8 -*-

import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

from local_config import local_conf
from commands import start_watering
from stpi_config import stpi_config


class MqttClient():

    def __init__(self, client_id):
        self.client = mqtt.Client(client_id)
        self.client.on_message = self.on_message

    # 消息处理函数
    def on_message(self, client, user_data, msg):
        # 浇水命令topic: ‘c2d/watering_req/+/+/+’ （plant_id，openid，timestamp)
        # 例: c2d/watering_req/1/oGhRu5dXuJHs-01JTwYUFQqZD0_U/1600355387
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        plant_id = topic.split('/')[2]
        timestamp = topic.split('/')[4]
        if int(stpi_config.PLANT_ID) != int(plant_id) or not timestamp.isdigit():
            return
        now_timestamp = int(time.time())
        # 命令时效性限制, 2分钟之前的MQTT消息将忽略
        if now_timestamp - int(timestamp) > 120:
            return
        if payload == local_conf.mqtt_payload['WATERING']:
            start_watering()

        return

    def mqtt_connect(self):
        self.client.connect(local_conf.mqtt_broker['HOST'], local_conf.mqtt_broker['PORT'], 60)

    def mqtt_subscribe(self, topic, qos=2):
        self.client.subscribe(topic=topic, qos=qos)
        self.client.loop_forever()

    def mqtt_publish(self, topic, payload, qos=2):
        self.client.publish(topic=topic, payload=payload, qos=qos)
