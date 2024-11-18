from machine import ADC, Pin
from time import sleep

# Define the air and water threshold values
AirValue = 791
WaterValue = 318 

# Calculate the intervals based on the values
intervals = (AirValue - WaterValue) // 3

# Initialize the ADC for the pin (GP26 = ADC0)
soil_moisture_sensor = ADC(Pin(27))

# Function to read the sensor value
def read_soil_moisture():
    # Read the raw ADC value (0-65535)
    raw_value = soil_moisture_sensor.read_u16()
    # Convert to a scale similar to Arduino (0-1023)
    scaled_value = raw_value // 64
    return scaled_value

def moist():
    # Main loop
    while True:
    #for _ in range(1):
        soilMoistureValue = read_soil_moisture()  # Read sensor value
        print("Soil Moisture Value:", soilMoistureValue)

        if WaterValue < soilMoistureValue < (WaterValue + intervals):
            print("Very Wet")
        elif (WaterValue + intervals) < soilMoistureValue < (AirValue - intervals):
            print("Wet")
        elif (AirValue - intervals) < soilMoistureValue < AirValue:
            print("Dry")

        sleep(0.1)  # Delay for 100ms (similar to Arduino delay)

moist()