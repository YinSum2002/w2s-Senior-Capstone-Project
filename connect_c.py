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
BLE_SCAN_INTERVAL = 30000
BLE_SCAN_WINDOW = 30000

# Arrays to store received sensor values
humidity_values = []
temperature_c_values = []
temperature_f_values = []


def encode_message(message):
    """Encode a message to bytes"""
    return message.encode("utf-8")


# Decode received messages
def decode_message(message):
    """Decode a message from bytes"""
    return message.decode("utf-8")


def print_sensor_data():
    """Print all collected sensor values."""
    print("\nCollected Sensor Data:")
    print("Humidity Values:", humidity_values)
    print("Temperature (C) Values:", temperature_c_values)
    print("Temperature (F) Values:", temperature_f_values)
    print("\n")


async def receive_data_task(characteristic):
    """Receive data from the connected peripheral device."""
    sensor_labels = ["Humidity", "Temperature (C)", "Temperature (F)"]
    sensor_index = 0  # Track which sensor value we expect to receive

    while True:
        try:
            # Read data from the peripheral
            data = await characteristic.read()

            if data:
                decoded_message = decode_message(data)

                # Check the label and store the value in the correct array
                if decoded_message.startswith("HUMIDITY:"):
                    try:
                        humidity_value = float(decoded_message.split(":")[1])
                        humidity_values.append(humidity_value)
                        print(f"Appended to Humidity array: {humidity_value}")
                    except ValueError:
                        print(f"Failed to convert to float: {decoded_message}")

                elif decoded_message.startswith("TEMP_C:"):
                    try:
                        temp_c_value = float(decoded_message.split(":")[1])
                        temperature_c_values.append(temp_c_value)
                        print(f"Appended to Temperature (C) array: {temp_c_value}")
                    except ValueError:
                        print(f"Failed to convert to float: {decoded_message}")

                elif decoded_message.startswith("TEMP_F:"):
                    try:
                        temp_f_value = float(decoded_message.split(":")[1])
                        temperature_f_values.append(temp_f_value)
                        print(f"Appended to Temperature (F) array: {temp_f_value}")
                    except ValueError:
                        print(f"Failed to convert to float: {decoded_message}")

                # Send acknowledgment
                await characteristic.write(encode_message("Got it"))
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


"""
async def receive_data_task(characteristic):
    # Receive data from the connected peripheral device.
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
                await characteristic.write(encode_message("Got it"))
                print(f"Acknowledged {sensor_labels[sensor_index]}")

                # Move to the next sensor in the sequence
                sensor_index = (sensor_index + 1) % len(sensor_labels)

            await asyncio.sleep(0.5)  # Small delay to prevent rapid polling

        except asyncio.TimeoutError:
            print("Timeout waiting for data.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break """


async def ble_scan():
    """Scan for a BLE device with the matching service UUID."""
    print("Scanning for BLE devices...")

    async with aioble.scan(
        5000, interval_us=BLE_SCAN_INTERVAL, window_us=BLE_SCAN_WINDOW, active=True
    ) as scanner:
        async for result in scanner:
            if result.name() == "Peripheral" and BLE_SVC_UUID in result.services():
                print(f"Found {result.name()} with service UUID {BLE_SVC_UUID}")
                return result
    return None


"""
async def run_central_mode():
    #Run the central mode to connect to and receive data from the peripheral.

    # Start scanning for a device with the matching service UUID
    while True:
        device = await ble_scan()

        if device is None:
            continue
        print(f"Device: {device}, Name: {device.name()}")

        try:
            print(f"Connecting to {device.name()}")
            connection = await device.device.connect()
        except asyncio.TimeoutError:
            print("Timeout during connection")
            continue

        print("Connected to peripheral device")

        # Discover services
        async with connection:
            try:
                service = await connection.service(BLE_SVC_UUID)
                characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
            except (asyncio.TimeoutError, AttributeError):
                print("Timed out discovering services/characteristics")
                continue
            except Exception as e:
                print(f"Error discovering services: {e}")
                await connection.disconnect()
                continue

            # Start receiving sensor data
            tasks = [
                asyncio.create_task(receive_data_task(characteristic)),
            ]
            await asyncio.gather(*tasks)

            await connection.disconnected()
            print("Disconnected from peripheral device")
            break """


async def run_central_mode():
    """Run the central mode to connect to and receive data from the peripheral."""

    while True:
        # Scan for devices matching the service UUID
        device = await ble_scan()

        if device is None:
            continue
        print(f"Device: {device}, Name: {device.name()}")

        try:
            print(f"Connecting to {device.name()}")
            connection = await device.device.connect()
        except asyncio.TimeoutError:
            print("Timeout during connection")
            continue

        print("Connected to peripheral device")

        # Discover services with a custom timeout using asyncio.wait_for
        async with connection:
            try:
                # Discover the service with a timeout
                service = await asyncio.wait_for(
                    connection.service(_SERVICE_UUID), timeout=5.0
                )
                # Discover the characteristic with a timeout
                characteristic = await asyncio.wait_for(
                    service.characteristic(_CHARACTERISTIC_UUID), timeout=5.0
                )
                print("Successfully discovered service and characteristic.")
            except asyncio.TimeoutError:
                print("Timed out discovering services/characteristics")
                await connection.disconnect()
                continue
            except Exception as e:
                print(f"Error discovering services: {e}")
                await connection.disconnect()
                continue

            # Start receiving sensor data
            tasks = [
                asyncio.create_task(receive_data_task(characteristic)),
            ]
            await asyncio.gather(*tasks)

            await connection.disconnected()
            print("Disconnected from peripheral device")
            break

    print_sensor_data()


async def main():
    """Main function for the central device."""
    while True:
        tasks = [
            asyncio.create_task(run_central_mode()),
        ]

        await asyncio.gather(*tasks)


# Run the central BLE main loop
asyncio.run(main())
