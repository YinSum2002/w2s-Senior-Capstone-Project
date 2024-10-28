from machine import Pin, ADC
import time

# Constants
SensorPin = 26  # Assuming GPIO26 for ADC input (change to your correct ADC pin)
Offset = 0.00  # Deviation compensate
LED = Pin(13, Pin.OUT)  # LED connected to GPIO13
samplingInterval = 20  # Sampling interval in milliseconds
printInterval = 800  # Print interval in milliseconds
ArrayLenth = 40  # Number of samples for averaging

pHArray = [0] * ArrayLenth  # Store the average value of the sensor feedback
pHArrayIndex = 0

# Initialize ADC for analog pH sensor
adc = ADC(Pin(SensorPin))

def average_array(arr, number):
    if number <= 0:
        print("Error: Invalid array length for averaging")
        return 0
    
    if number < 5:
        return sum(arr) / number
    else:
        # Calculate average excluding the min and max values
        min_val = min(arr)
        max_val = max(arr)
        total = sum(arr) - min_val - max_val
        return total / (number - 2)

# Setup
print("pH meter experiment!")

# Main loop
samplingTime = time.ticks_ms()
printTime = time.ticks_ms()

while True:
    currentTime = time.ticks_ms()
    
    # Sampling at intervals
    if time.ticks_diff(currentTime, samplingTime) > samplingInterval:
        pHArray[pHArrayIndex] = adc.read()  # Read analog value (0-4095 for 12-bit ADC)
        pHArrayIndex += 1
        if pHArrayIndex == ArrayLenth:
            pHArrayIndex = 0
        
        voltage = average_array(pHArray, ArrayLenth) * 3.3 / 4095  # Convert ADC reading to voltage (3.3V system)
        pHValue = 3.5 * voltage + Offset  # Calculate pH value
        samplingTime = currentTime

    # Printing values at intervals
    if time.ticks_diff(currentTime, printTime) > printInterval:
        print("Voltage: {:.2f}V    pH value: {:.2f}".format(voltage, pHValue))
        LED.value(not LED.value())  # Toggle LED state
        printTime = currentTime

    time.sleep_ms(10)  # Short sleep to prevent high CPU usage
