import time
import board
import busio
import adafruit_veml6075
import veml6075
from machine import I2C, Pin

import machine
import time

# Test GP4 (SDA)
# pin = machine.Pin(5, machine.Pin.OUT)
# while True:
#     pin.value(1)
#     time.sleep(0.5)
#     pin.value(0)
#     time.sleep(0.5)

# Repeat for GP5 (SCL)

def read_uv():
    print("reading uv")
    i2c = I2C(0, scl=Pin(5), sda=Pin(4))  # I2C0 on Pico W
    
    print("Scanning I2C devices...")
    devices = i2c.scan()
    print("Found I2C devices:", [hex(dev) for dev in devices])    
    
    sensor = veml6075.VEML6075(i2c=i2c)

    #print(sensor.uv_index)
    return (sensor.uv_index, sensor.uva, sensor.uvb)

print(read_uv())
#read_uv()