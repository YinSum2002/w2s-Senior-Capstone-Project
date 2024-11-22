import time
import board
import busio
import adafruit_veml6075
import veml6075
from machine import I2C, Pin

def read_uv():
    i2c = I2C(0x01, sda=Pin(6), scl=Pin(7))
    
    #print("Scanning I2C devices...")
    devices = i2c.scan()
    #print("Found I2C devices:", [hex(dev) for dev in devices])    
    
    sensor = veml6075.VEML6075(i2c=i2c)

    #print(he, sensor.uv_index)
    return (sensor.uv_index, sensor.uva, sensor.uvb)
