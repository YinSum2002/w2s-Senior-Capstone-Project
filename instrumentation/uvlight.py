import time
import board
import busio
import adafruit_veml6075
import veml6075
from machine import I2C, Pin
#import adafruit_tca9548a

i2c = I2C(0x01, sda=Pin(6), scl=Pin(7))
sensor = veml6075.VEML6075(i2c=i2c)
#while True:
def read_uv(sensor):
    for _ in range(1):
        print("uv_index: ", sensor.uv_index)    

def hello_there(str):
    print(str)

read_uv(sensor)