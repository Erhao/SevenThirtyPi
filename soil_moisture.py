# -*- encoding: utf-8 -*-

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)

soil_moisture_pin = 36
GPIO.setup(soil_moisture_pin, GPIO.IN)


def detect_dry_or_wet():
    if GPIO.input(soil_moisture_pin) == GPIO.LOW:
        return '1'
    return '0'
