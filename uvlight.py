import time
import board
import busio
import adafruit_veml6075
import veml6075
from machine import I2C, Pin
#import adafruit_tca9548a

i2c = I2C(0x01, sda=Pin(6), scl=Pin(7))
sensor = veml6075.VEML6075(i2c=i2c)
while True:
    print("uv_index: ", sensor.uv_index)
    time.sleep(10)    

# # Set up I2C bus
# i2c = busio.I2C(board.GP7, board.GP6)  # Update with your correct pins
# 
# # # initialize the multiplexer
# #tca = adafruit_tca9548a.TCA9548A(i2c)
# # 
# # Scan for devices
# devices = i2c.scan()
# 
# if devices:
#     print("I2C device(s) found:", [hex(device) for device in devices])
# else:
#     print("No I2C devices found")
# 
# # Initialize the sensor
# #uv_sensor = adafruit_veml6075.VEML6075(i2c)
# uv_sensor = veml6075.VEML6075(i2c)
# 
# 
# # Main loop
# while True:
#     print("UV Index: ", uv_sensor.uv_index)
#     print("UVA: ", uv_sensor.uva)
#     print("UVB: ", uv_sensor.uvb)
#     
#     time.sleep(10)


# import time
# import board
# import busio
# import adafruit_veml6075
# import json  # Import the JSON module
# 
# # Set up I2C bus
# i2c = busio.I2C(board.GP5, board.GP4)  # Update with your correct pins. SDA to GP4, SCL to GP5
# 
# # Initialize the sensor
# uv_sensor = adafruit_veml6075.VEML6075(i2c)
# 
# # Function to get UV data and return it as a dictionary
# def get_uv_data():
#     uv_data = {
#         'uv_index': uv_sensor.uv_index,
#         'uva': uv_sensor.uva,
#         'uvb': uv_sensor.uvb
#     }
#     return uv_data
# 
# # Main loop
# while True:
#     # Get UV data
#     uv_data = get_uv_data()
# 
#     # Convert the UV data dictionary to a JSON string
#     uv_json = json.dumps(uv_data)
# 
#     # Print the JSON string
#     print("UV Data as JSON: ", uv_json)
# 
#     # Save the JSON string to a file (optional)
#     with open("uv_data.json", "w") as json_file:
#         json.dump(uv_data, json_file)
# 
#     time.sleep(1)
