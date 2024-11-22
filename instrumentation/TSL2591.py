import time
import board
import busio
import adafruit_tsl2591
import adafruit_tca9548a

def light():
    # Set up I2C bus
    i2c = busio.I2C(board.GP7, board.GP6)  # Use your I2C pins
    time.sleep(1)
    
    tca = adafruit_tca9548a.TCA9548A(i2c)

    # Initialize the sensor to the 0th channel on the multiplexer
    sensor = adafruit_tsl2591.TSL2591(i2c) # how do I address a specific device for these i2c busses
    #sensor = adafruit_tsl2591.TSL2591(tca[0])
    
    # Set gain to low to handle bright light
    sensor.gain = adafruit_tsl2591.GAIN_LOW

    return sensor.lux
    
light()    
time.sleep(1)

