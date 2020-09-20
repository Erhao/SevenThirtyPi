# -*- encoding: utf-8 -*-

""" 机械控制命令 """

import time
import RPi.GPIO as GPIO


# 出水控制电磁铁继电器pin
relay_pin = 37
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay_pin, GPIO.OUT)


def start_watering():
    GPIO.output(relay_pin, 1)
    time.sleep(15)
    GPIO.output(relay_pin, 0)
