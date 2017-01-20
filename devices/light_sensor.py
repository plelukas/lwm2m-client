# Created by Bartosz Szmit on 1/19/17. 
# Domain: bszmit.pl
# GitHub: github.com/bszmit

from gpiozero import MCP3008 as MCP


class LightSensor(object):
    def __init__(self):
        self.sensor = MCP(0)

    def read(self):
        return self.sensor.value * 100
