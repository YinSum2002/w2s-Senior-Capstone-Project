from machine import ADC, Pin
import time

# Set up the ADC (assuming you're using pin 31, which is ADC0)
ph_adc = ADC(Pin(26))  # ADC0 corresponds to GP26

# Calibration values (you may need to adjust these based on your sensor)
offset = 0.0
scaling_factor = 3.3 / 65535  # Convert 16-bit ADC reading to voltage

def read_ph():
    # Read the raw analog value
    raw_value = ph_adc.read_u16()
    
    # Convert raw value to voltage
    voltage = raw_value * scaling_factor
    
    # Calculate pH based on the voltage (you may need to adjust the formula)
    # For example, if 0V corresponds to pH 0 and 3.3V corresponds to pH 14:
    ph_value = voltage * 14.0 / 3.3 + offset
    print("pH: ", ph_value)
    return ph_value

# Main loop
#while True:
    #ph = read_ph()
    #print(f"pH Value: {ph:.2f}")
    #time.sleep(1)

read_ph()