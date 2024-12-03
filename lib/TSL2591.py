import time
import board
import busio
import adafruit_tsl2591
import adafruit_tca9548a
from machine import I2C, Pin

def light():
    # Set up I2C bus
    i2c = busio.I2C(board.GP5, board.GP4)  # Use your I2C pins
    time.sleep(1)
    print("Scanning I2C devices...")
    devices = i2c.scan()
    print("Found I2C devices:", [hex(dev) for dev in devices])
    
    tca = adafruit_tca9548a.TCA9548A(i2c)

    # Initialize the sensor to the 0th channel on the multiplexer
    sensor = adafruit_tsl2591.TSL2591(i2c) # how do I address a specific device for these i2c busses
    #sensor = adafruit_tsl2591.TSL2591(tca[0])
    
    # Set gain to low to handle bright light
    sensor.gain = adafruit_tsl2591.GAIN_LOW

    return sensor.lux
    
for _ in range(10):
    print(light())
#time.sleep(1)