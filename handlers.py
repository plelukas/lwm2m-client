#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# when resource is both readable and writable
# then specify optional argument for a method to distinguish between reads and writes
# writable handler MUST return True or False in order to tell if it completed successfully or not
from devices.buzzer import Buzzer
from devices.gas_sensor import GasSensor
from devices.pressure_sensor import PressureSensor
from devices.thermometer import Thermometer
from devices.light_sensor import LightSensor

thermometer = Thermometer()
lightSensor = LightSensor()
buzzer = Buzzer(5)
pressureSensor = PressureSensor()
gasSensor = GasSensor()


def read_manufacturer():
    return "Lenovo"


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


def read_temperature():
    return thermometer.read_temp()


def read_light():
    return lightSensor.read()


def beep_buzzer(args):
    buzzer.beep()


def read_pressure():
    return pressureSensor.read()


def read_gas():
    return gasSensor.read()
