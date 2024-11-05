from machine import Pin, I2C

# Set up I2C (same settings as your main code)
i2c = I2C(0, scl=Pin(17), sda=Pin(16))

# Scan for devices
devices = i2c.scan()

if devices:
    print("I2C device(s) found:", [hex(device) for device in devices])
else:
    print("No I2C devices found")
