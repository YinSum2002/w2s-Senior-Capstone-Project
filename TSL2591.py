import time
import board
import busio
import adafruit_tsl2591

# Set up I2C bus
i2c = busio.I2C(board.GP5, board.GP4)  # Use your I2C pins

# Initialize the sensor
sensor = adafruit_tsl2591.TSL2591(i2c)

# Main loop
while True:
    lux = sensor.lux
    print("Lux:", lux)
    
    time.sleep(1)
