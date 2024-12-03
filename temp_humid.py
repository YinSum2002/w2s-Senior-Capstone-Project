import time
import machine
from machine import Pin, I2C

# Define AM2320 I2C address
AM2320_ADDR = 0x5C

# Initialize the I2C bus
print(machine.Pin(17))
print(machine.Pin(16))
i2c = I2C(0, scl=Pin(17), sda=Pin(16))
#i2c = machine.I2C(1, scl=machine.Pin(17), sda=machine.Pin(16))

devices = i2c.scan()

if devices:
    print("I2C device(s) found:", [hex(device) for device in devices])
else:
    print("No I2C devices found")

def read_am2320():
    try:
        # Step 1: Wake up the sensor (send a dummy write)
        i2c.writeto(AM2320_ADDR, b'')
        time.sleep(0.001)  # Wait for a short time

        # Step 2: Send the read command (0x03 to read temperature and humidity)
        i2c.writeto(AM2320_ADDR, b'\x03\x00\x04')

        # Step 3: Read 8 bytes of data
        result = i2c.readfrom(AM2320_ADDR, 8)

        # Step 4: Process the result
        # First two bytes are the function code and byte count, we ignore them
        humidity = (result[2] << 8 | result[3]) / 10.0
        temperature = (result[4] << 8 | result[5]) / 10.0

        return temperature, humidity

    except OSError as e:
        print("Failed to read from AM2320 sensor:", e)
        return None, None

while True:
    temperature, humidity = read_am2320()
    if temperature is not None and humidity is not None:
        print("Temperature:", temperature)
        print("Humidity:", humidity)
    else:
        print("Failed to read data.")
    time.sleep(2)