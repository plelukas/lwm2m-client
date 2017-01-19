
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

def beep(x):
    try:
        buzzer_on()
        time.sleep(x)
    finally:
        buzzer_off()
        time.sleep(0.01)


def gas_setup():
    GPIO.setup(GasPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def action(pin):
    beep(0.5)

def gas_on():
    GPIO.add_event_detect(GasPin, GPIO.RISING)
    GPIO.add_event_callback(GasPin, action)



def DHT11_adafruit():
    for i in range(0, 5):
        humidity, temperature = Adafruit_DHT.read_retry(11, DHT11Pin)  # GPIO27 (BCM notation)
        print("Humidity = {} %; Temperature = {} C".format(humidity, temperature))



if __name__ == '__main__':
    try:
        buzzer_setup()
        gas_setup()

        try:
            gas_on()
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass

    finally:
        GPIO.cleanup()

