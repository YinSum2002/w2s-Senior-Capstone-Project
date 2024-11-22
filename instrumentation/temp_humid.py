from machine import Pin, I2C
import board
import busio
import time
import am2320

# Set up I2C (you can choose either I2C0 or I2C1)
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)  # Configure for I2C0 with SCL=GP5, SDA=GP4

# AM2320 I2C address
AM2320_ADDR = 0x5C

def read_am2320():
    try:
        # Wake up the sensor
        i2c.writeto(AM2320_ADDR, b'')

        # Send command to read temperature and humidity
        i2c.writeto(AM2320_ADDR, b'\x03\x00\x04')

        # Read 8 bytes of data
        data = i2c.readfrom(AM2320_ADDR, 8)

        # Calculate humidity and temperature
        humidity = (data[2] << 8 | data[3]) / 10.0
        temperature = (data[4] << 8 | data[5]) / 10.0

        # Check if temperature is negative
        if data[4] & 0x80:
            temperature = -temperature

        if (humidity, temperature) != (None, None):
            #print("equal statement true")
            return humidity, temperature
        
        
        
        if (humidity, temperature) == (None, None):
            print("calling function again")
            read_am2320()

        
        return humidity, temperature

    except OSError as e:
        #print("Failed to read from AM2320:", e)
        #return None, None
        pass

for _ in range(10):
    read_am2320()