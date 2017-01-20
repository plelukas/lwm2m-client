# Created by Bartosz Szmit on 1/20/17. 
# Domain: bszmit.pl
# GitHub: github.com/bszmit


from gpiozero import Buzzer as Buzz
import threading


class Buzzer(object):
    def __init__(self, pin: int):
        self.sensor = Buzz(pin)

    def beep(self):
        if not self.sensor.is_active:
            threading.Timer(0.25, self.sensor.off).start()
            self.sensor.on()
