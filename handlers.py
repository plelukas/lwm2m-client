#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# when resource is both readable and writable
# then specify optional argument for a method to distinguish between reads and writes
# writable handler MUST return True or False in order to tell if it completed successfully or not

import time, sys
import RPi.GPIO as GPIO
import Adafruit_DHT

BuzzerPin = 17  # pin11 physical
DHT11Pin = 27  # pin13 physical
GasPin = 26  # pin37 physical

GPIO.setmode(GPIO.BCM)

def buzzer_setup():
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.output(BuzzerPin, GPIO.LOW)

def buzzer_on():
    GPIO.output(BuzzerPin, GPIO.HIGH)

def buzzer_off():
    GPIO.output(BuzzerPin, GPIO.LOW)

buzzer_setup()
def beep(x):
    try:
        buzzer_on()
        time.sleep(x)
    finally:
        buzzer_off()
        time.sleep(0.01)

def DHT11_adafruit():
    for i in range(0, 5):
        humidity, temperature = Adafruit_DHT.read_retry(11, DHT11Pin)  # GPIO27 (BCM notation)
        print("Humidity = {} %; Temperature = {} C".format(humidity, temperature))


def read_temperature():
    # for now read temperature
    humidity, temperature = Adafruit_DHT.read_retry(11, DHT11Pin)
    return str(temperature)

def read_humidity():
    # for now read humidity
    humidity, temperature = Adafruit_DHT.read_retry(11, DHT11Pin)
    return str(humidity)

def execute_buzz(params_list):
    if params_list is not None:
        try:
            how_long = int(params_list[0])
            beep(how_long)
        except:
            pass
    else:
        beep(0.5)


def handle_disable(params_list=None):
    print('elooooooooooooo')

_timezone = 'Europe/Warsaw'

def handle_timezone(arg=None):
    if arg is None:
        # handle read
        return _timezone
    else:
        # handle write
        global _timezone
        _timezone = arg
        return True

