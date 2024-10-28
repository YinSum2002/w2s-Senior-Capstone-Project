from machine import ADC, Pin
import time

# Set up the soil moisture sensor
soil_moisture_pin = ADC(Pin(26))  # Use GP26 (ADC0)

# Function to read the moisture level
def read_moisture():
    # Read the ADC value (0-65535) and scale it to a 0-100% range
    moisture_level = soil_moisture_pin.read_u16() / 65535 * 100
    return moisture_level

# Main loop to continuously read the sensor
while True:
    moisture = read_moisture()
    print(f"Soil Moisture Level: {moisture:.2f}%")
    time.sleep(1)
