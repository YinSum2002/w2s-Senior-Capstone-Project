import time
import board
import busio
import adafruit_tsl2591
import adafruit_tca9548a

# initialize the multiplexer
#tca = adafruit_tca9548a.TCA9548A(i2c)

# Scan for devices
# devices = i2c.scan()
# 
# if devices:
#     print("I2C device(s) found:", [hex(device) for device in devices])
# else:
#     print("No I2C devices found")

def light():
    # Set up I2C bus
    i2c = busio.I2C(board.GP7, board.GP6)  # Use your I2C pins
    time.sleep(1)
    # Scan for devices
    print("Scanning I2C devices...")
    devices = i2c.scan()
    print("Found I2C devices:", [hex(dev) for dev in devices])
    
    tca = adafruit_tca9548a.TCA9548A(i2c)

    # Initialize the sensor to the 0th channel on the multiplexer
    sensor = adafruit_tsl2591.TSL2591(i2c) # how do I address a specific device for these i2c busses
    #sensor = adafruit_tsl2591.TSL2591(tca[0])
    
    # Main loop to read light levels
    while True:
        lux = sensor.lux
        print("Lux:", lux)
        time.sleep(1)
    # Main loop
    #while True:
    return sensor.lux
    #print("Lux:", lux)
    
    
light()    
time.sleep(1)
