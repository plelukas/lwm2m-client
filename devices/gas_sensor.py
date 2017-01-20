# Created by Bartosz Szmit on 1/20/17. 
# Domain: bszmit.pl
# GitHub: github.com/bszmit


from gpiozero import MCP3008 as MCP


class GasSensor(object):
    def __init__(self):
        self.sensor = MCP(1)

    def read(self):
        return self.sensor.value
