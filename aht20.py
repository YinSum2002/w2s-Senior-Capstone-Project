<<<<<<< HEAD
from machine import I2C, Pin
import time

# AHT20 I2C address
AHT20_I2C_ADDR = 0x38

# AHT20 commands
AHT20_CMD_INIT = b'\xBE\x08\x00'
AHT20_CMD_TRIGGER = b'\xAC\x33\x00'

# AHT20 sensor class
class AHT20:
    def __init__(self, i2c):
        self.i2c = i2c
        self.init_sensor()

    def init_sensor(self):
        # Initialize AHT20 sensor
        self.i2c.writeto(AHT20_I2C_ADDR, AHT20_CMD_INIT)
        time.sleep(0.05)  # Wait for the sensor to initialize

    def trigger_measurement(self):
        # Trigger measurement
        self.i2c.writeto(AHT20_I2C_ADDR, AHT20_CMD_TRIGGER)
        time.sleep(0.1)  # Wait for measurement to complete

    def read_data(self):
        # Read 6 bytes of data from the sensor
        data = self.i2c.readfrom(AHT20_I2C_ADDR, 6)
        
        if data[0] & 0x80:  # Check if sensor is busy
            return None, None
        
        # Extract humidity (20-bit) and temperature (20-bit)
        humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) & 0xFFFFF
        temperature = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) & 0xFFFFF

        # Convert raw values to relative humidity (%) and temperature (°C)
        humidity_percent = (humidity / 1048576) * 100
        temperature_celsius = ((temperature / 1048576) * 200) - 50

        return humidity_percent, temperature_celsius

# Set up I2C connection (using I2C0, SDA=GP0, SCL=GP1)
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)

# Create AHT20 sensor object
sensor = AHT20(i2c)

print("\nStabilizing Sensor...")
time.sleep(10)

# Continuously read and display temperature and humidity
while True:
    sensor.trigger_measurement()
    humid, temp_c = sensor.read_data()
    temp_f = (temp_c * 9/5) + 32
    
    if humid is not None and temp_c is not None:
        # Basil ideally grows from anywhere between 40-60% RH
        print("Humidity: {:.2f}%".format(humid))
        if (humid < 40):
            print ("Too Dry!\n")
        elif (humid > 60):
            print ("Too Humid!\n")
        else:
            print ("Ideal Growing Conditions!\n")
        
        # Basil ideally grows between 70-85 deg F but can successfully grow as long as temp doesn't go below 50 deg F
        print("Temperature: {:.2f}°C / {:.2f}°F".format(temp_c, temp_f))
        if (temp_f < 50):
            print("Too cold to grow. Please move to warmer area.\n")
        elif (temp_f > 85):
            print("Consider moving to a colder area to maximize growing.\n")
        elif (temp_f > 70 and temp_f < 85):
            print("Ideal Temperature Range!\n")
        else:
            print("Within temperature range for growing\n")
    else:
        print("Sensor is busy, waiting for data...")

    time.sleep(2)  # Wait 2s before next reading
=======
from machine import I2C, Pin
import time

# AHT20 I2C address
AHT20_I2C_ADDR = 0x38

# AHT20 commands
AHT20_CMD_INIT = b'\xBE\x08\x00'
AHT20_CMD_TRIGGER = b'\xAC\x33\x00'

# AHT20 sensor class
class AHT20:
    def __init__(self, i2c):
        self.i2c = i2c
        self.init_sensor()

    def init_sensor(self):
        # Initialize AHT20 sensor
        self.i2c.writeto(AHT20_I2C_ADDR, AHT20_CMD_INIT)
        time.sleep(0.05)  # Wait for the sensor to initialize

    def trigger_measurement(self):
        # Trigger measurement
        self.i2c.writeto(AHT20_I2C_ADDR, AHT20_CMD_TRIGGER)
        time.sleep(0.1)  # Wait for measurement to complete

    def read_data(self):
        # Read 6 bytes of data from the sensor
        data = self.i2c.readfrom(AHT20_I2C_ADDR, 6)
        
        if data[0] & 0x80:  # Check if sensor is busy
            return None, None
        
        # Extract humidity (20-bit) and temperature (20-bit)
        humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) & 0xFFFFF
        temperature = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) & 0xFFFFF

        # Convert raw values to relative humidity (%) and temperature (°C)
        humidity_percent = (humidity / 1048576) * 100
        temperature_celsius = ((temperature / 1048576) * 200) - 50

        return humidity_percent, temperature_celsius

# Set up I2C connection (using I2C0, SDA=GP0, SCL=GP1)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

# Create AHT20 sensor object
sensor = AHT20(i2c)

print("\nStabilizing Sensor...")
time.sleep(10)

# Continuously read and display temperature and humidity
while True:
    sensor.trigger_measurement()
    humid, temp_c = sensor.read_data()
    temp_f = (temp_c * 9/5) + 32
    
    if humid is not None and temp_c is not None:
        # Basil ideally grows from anywhere between 40-60% RH
        print("Humidity: {:.2f}%".format(humid))
        if (humid < 40):
            print ("Too Dry!\n")
        elif (humid > 60):
            print ("Too Humid!\n")
        else:
            print ("Ideal Growing Conditions!\n")
        
        # Basil ideally grows between 70-85 deg F but can successfully grow as long as temp doesn't go below 50 deg F
        print("Temperature: {:.2f}°C / {:.2f}°F".format(temp_c, temp_f))
        if (temp_f < 50):
            print("Too cold to grow. Please move to warmer area.\n")
        elif (temp_f > 85):
            print("Consider moving to a colder area to maximize growing.\n")
        elif (temp_f > 70 and temp_f < 85):
            print("Ideal Temperature Range!\n")
        else:
            print("Within temperature range for growing\n")
    else:
        print("Sensor is busy, waiting for data...")

    time.sleep(2)  # Wait 2s before next reading
>>>>>>> refs/remotes/origin/main
