import aioble
import bluetooth
import asyncio
from sys import exit
from machine import I2C, Pin
import time

# AHT20 I2C address and commands
AHT20_I2C_ADDR = 0x38
AHT20_CMD_INIT = b'\xBE\x08\x00'
AHT20_CMD_TRIGGER = b'\xAC\x33\x00'

# AHT20 sensor class
class AHT20:
    def __init__(self, i2c):
        self.i2c = i2c
        self.init_sensor()

    def init_sensor(self):
        self.i2c.writeto(AHT20_I2C_ADDR, AHT20_CMD_INIT)
        time.sleep(0.05)

    def trigger_measurement(self):
        self.i2c.writeto(AHT20_I2C_ADDR, AHT20_CMD_TRIGGER)
        time.sleep(0.1)

    def read_data(self):
        data = self.i2c.readfrom(AHT20_I2C_ADDR, 6)
        if data[0] & 0x80:
            return None, None

        humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) & 0xFFFFF
        temperature = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) & 0xFFFFF

        humidity_percent = (humidity / 1048576) * 100
        temperature_celsius = ((temperature / 1048576) * 200) - 50

        return humidity_percent, temperature_celsius

# Set up I2C and sensor
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
sensor = AHT20(i2c)
print("Initalizing sensor(s)...")
time.sleep(5)

# Bluetooth parameters
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_NAME = "Peripheral"
BLE_SVC_UUID = bluetooth.UUID(0x181A)
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_APPEARANCE = 0x0300
BLE_ADVERTISING_INTERVAL = 2000

# Separate data arrays for each sensor value
humidity_data = []
temp_c_data = []
temp_f_data = []

async def gather_sensor_data(sensor):
    """Gather data and append each value to its respective array."""
    sensor.trigger_measurement()
    humidity, temp_c = sensor.read_data()
    temp_f = (temp_c * 9 / 5) + 32

    # Format values to strings and append to respective arrays
    humidity_data.append(f"{humidity:.2f}")
    temp_c_data.append(f"{temp_c:.2f}")
    temp_f_data.append(f"{temp_f:.2f}")

    print(f"Collected -> Humidity: {humidity}, Temp (C): {temp_c}, Temp (F): {temp_f}")
    await asyncio.sleep(1)

def encode_message(message):
    """Encode message as bytes for transmission."""
    return message.encode('utf-8')

def decode_message(message):
    """ Decode a message from bytes """
    return message.decode('utf-8')

async def send_data_task(connection, characteristic):
    """Alternate sending values from each array over BLE with acknowledgment."""
    max_len = max(len(humidity_data), len(temp_c_data), len(temp_f_data))

    for i in range(max_len):
        # Send humidity value if available
        if i < len(humidity_data):
            message = f"HUMIDITY:{humidity_data[i]}"
            print(f"Sending {message}")
            await send_message(connection, characteristic, message)

        # Send temperature in Celsius if available
        if i < len(temp_c_data):
            message = f"TEMP_C:{temp_c_data[i]}"
            print(f"Sending {message}")
            await send_message(connection, characteristic, message)

        # Send temperature in Fahrenheit if available
        if i < len(temp_f_data):
            message = f"TEMP_F:{temp_f_data[i]}"
            print(f"Sending {message}")
            await send_message(connection, characteristic, message)

async def send_message(connection, characteristic, message):
    """Send a message and wait for acknowledgment from the central."""
    try:
        # Send the message
        msg = encode_message(message)
        characteristic.write(msg)
        await asyncio.sleep(0.5)  # Small delay to ensure message sends

        # Wait for acknowledgment
        ack_received = False
        while not ack_received:
            response = characteristic.read()
            if response:
                response = decode_message(response)
                if response == "Got it":
                    ack_received = True
                    print(f"Acknowledgment received for message: {message}")
            await asyncio.sleep(0.5)  # Small delay before re-checking

    except Exception as e:
        print(f"Error sending message: {e}")

"""
async def send_data_task(connection, characteristic):
    # Alternate sending values from each array over BLE.
    max_len = max(len(humidity_data), len(temp_c_data), len(temp_f_data))
    
    for i in range(max_len):

        # Send humidity value if available
        if i < len(humidity_data):
            message = humidity_data[i]
            print(f"Humidity: {message}")
            await send_message(connection, characteristic, message)

        # Send temperature in Celsius if available
        if i < len(temp_c_data):
            message = temp_c_data[i]
            print(f"Temp (C): {message}")
            await send_message(connection, characteristic, message)

        # Send temperature in Fahrenheit if available
        if i < len(temp_f_data):
            message = temp_f_data[i]
            print(f"Temp (F): {message}")
            await send_message(connection, characteristic, message)

async def send_message(connection, characteristic, message):
    # Helper function to send an encoded message and wait for acknowledgment.
    if not connection:
        print("error - no connection in send data")

    if not characteristic:
        print("error no characteristic provided in send data")

    try:
        msg = encode_message(message)
        characteristic.write(msg)
        await asyncio.sleep(0.5)  # Slight delay before the next message

        # Await acknowledgment from the central
        response = decode_message(characteristic.read())
        print(f"Central acknowledged: {message}, response {response}")
    except Exception as e:
        print(f"Error sending message: {e}") """


async def run_peripheral_mode(sensor):
    """Run the peripheral mode, gathering data 10 times before connecting."""
    # Counter to track the number of times we gather data
    gather_count = 0
    
    # Gather data 10 times
    while gather_count < 5:
        await gather_sensor_data(sensor)
        gather_count += 1
        await asyncio.sleep(1)
        
    ble_service = aioble.Service(_SERVICE_UUID)
    characteristic = aioble.Characteristic(
        ble_service,
        _CHARACTERISTIC_UUID,
        read=True,
        notify=True,
        write=True,
        capture=True,
    )
    aioble.register_services(ble_service)
    print("Peripheral starting to advertise")

    while True:
        await asyncio.sleep(1)
        async with await aioble.advertise(
            BLE_ADVERTISING_INTERVAL,
            name=BLE_NAME,
            services=[BLE_SVC_UUID],
            appearance=BLE_APPEARANCE
        ) as connection:
            print(f"{BLE_NAME} connected to: {connection.device}")
            tasks = [
                asyncio.create_task(send_data_task(connection, characteristic)),
            ]
            await asyncio.gather(*tasks)
            print("All messages sent. Disconnecting...")

            # Clear data arrays for the next round
            humidity_data.clear()
            temp_c_data.clear()
            temp_f_data.clear()

            break

async def main():
    while True:
        tasks = [asyncio.create_task(run_peripheral_mode(sensor))]
        await asyncio.gather(*tasks)

asyncio.run(main())
