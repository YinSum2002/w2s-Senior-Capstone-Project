import aioble
import bluetooth
import asyncio
from sys import exit

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Bluetooth parameters
BLE_NAME = "CentralDevice"
BLE_SVC_UUID = bluetooth.UUID(0x181A)
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_SCAN_INTERVAL = 10000
BLE_SCAN_WINDOW = 10000

# Arrays to store received sensor values
humidity_values = []
temperature_c_values = []
temperature_f_values = []

# Decode received messages
def decode_message(message):
    """Decode a message from bytes"""
    return message.decode('utf-8')

async def receive_data_task(characteristic):
    """Receive data from the connected peripheral device."""
    sensor_labels = ["Humidity", "Temperature (C)", "Temperature (F)"]
    sensor_index = 0  # Track which sensor value we expect to receive

    while True:
        try:
            # Read data from the peripheral
            data = await characteristic.read()

            if data:
                # Decode the received message
                sensor_value = decode_message(data)
                print(f"Received {sensor_labels[sensor_index]}: {sensor_value}")

                # Convert sensor value to float and store in the appropriate array
                try:
                    value = float(sensor_value)
                    if sensor_index == 0:
                        humidity_values.append(value)
                    elif sensor_index == 1:
                        temperature_c_values.append(value)
                    elif sensor_index == 2:
                        temperature_f_values.append(value)
                    print(f"Appended to {sensor_labels[sensor_index]} array: {value}")
                except ValueError:
                    print(f"Failed to convert {sensor_value} to float")

                # Send acknowledgment
                await characteristic.write(b"Got it")
                print(f"Acknowledged {sensor_labels[sensor_index]}")

                # Move to the next sensor in the sequence
                sensor_index = (sensor_index + 1) % len(sensor_labels)

            await asyncio.sleep(0.5)  # Small delay to prevent rapid polling

        except asyncio.TimeoutError:
            print("Timeout waiting for data.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

async def ble_scan():
    """Scan for a BLE device with the matching service UUID."""
    print("Scanning for BLE devices...")

    async with aioble.scan(10000, interval_us=BLE_SCAN_INTERVAL, window_us=BLE_SCAN_WINDOW, active=True) as scanner:
        async for result in scanner:
            if result.name() == "PeripheralDevice" and BLE_SVC_UUID in result.services():
                print(f"Found {result.name()} with service UUID {BLE_SVC_UUID}")
                return result
    return None

async def run_central_mode():
    while True:
        device = await ble_scan()

        if device is None:
            continue

        try:
            connection = await device.device.connect()
        except asyncio.TimeoutError:
            print("Timeout during connection")
            continue

        print(f"{IAM} connected to {connection}")

        async with connection:
            try:
                service = await connection.service(BLE_SVC_UUID)
                characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
                await receive_data_task(characteristic)
            except Exception as e:
                print(f"Service discovery failed: {e}")

        # Wait for the next scan
        print("Central disconnected, resuming scan...")

async def main():
    """Main function for the central device."""
    while True:
        await run_central_mode()

# Run the central BLE main loop
asyncio.run(main())
