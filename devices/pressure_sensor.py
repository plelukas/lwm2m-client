# Created by Bartosz Szmit on 1/20/17. 
# Domain: bszmit.pl
# GitHub: github.com/bszmit

import smbus


class PressureSensor(object):
    def __init__(self):
        self.sensor = smbus.SMBus(1)
        pass

    def read(self):
        self.sensor.write_byte_data(0x5d, 0x20, 0b10000000)  # turn on
        self.sensor.write_byte_data(0x5d, 0x21, 0b1)

        ph = self.sensor.read_byte_data(0x5d, 0x2a)  # read high, low bytes
        pl = self.sensor.read_byte_data(0x5d, 0x29)
        pxl = self.sensor.read_byte_data(0x5d, 0x28)
        pressure = float((((ph << 8) + pl) << 8) + pxl) / 4096  # compute pressure
        return pressure
