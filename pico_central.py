import aioble
import bluetooth
import ujson
import asyncio

# Bluetooth parameters
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)


async def ble_scan():
    print("Scanning for Peripheral...")
    async with aioble.scan(
        5000, interval_us=30000, window_us=30000, active=True
    ) as scanner:
        async for result in scanner:
            if result.name() == "Peripheral" and _SERVICE_UUID in result.services():
                print(f"Found Peripheral with UUID {_SERVICE_UUID}")
                return result
    return None


async def receive_data(characteristic):
    try:
        print("Receiving data...")
        json_bytes = await characteristic.read()
        json_data = ujson.loads(json_bytes.decode("utf-8"))

        print("Data received and parsed:")
        print(f"Humidity: {json_data['humidity']}")
        print(f"Temperature (C): {json_data['temp_c']}")
        print(f"Temperature (F): {json_data['temp_f']}")
    except Exception as e:
        print(f"Error receiving or parsing data: {e}")


async def run_central_mode():
    """Run the central mode to connect to the peripheral and receive data."""

    # Start scanning for a device with the matching service UUID
    while True:
        device = await ble_scan()

        if device is None:
            print("No device found, retrying scan...")
            continue
        print(f"Device found: {device}, name: {device.name()}")

        try:
            print(f"Attempting to connect to {device.name()}...")
            connection = await device.device.connect()

        except asyncio.TimeoutError:
            print("Connection timeout.")
            continue

        print(f"Connected to {device.name()} as {IAM}")

        # Discover services
        async with connection:
            try:
                service = await connection.service(BLE_SVC_UUID)
                if service is None:
                    print("Service not found. Disconnecting and retrying.")
                    await connection.disconnect()
                    continue  # Restart the connection attempt

                characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
                if characteristic is None:
                    print("Characteristic not found. Disconnecting and retrying.")
                    await connection.disconnect()
                    continue  # Restart the connection attempt

                print("Service and characteristic found. Ready to receive data.")

            except (asyncio.TimeoutError, AttributeError) as e:
                print(f"Error discovering services/characteristics: {e}")
                await connection.disconnect()
                continue
            except Exception as e:
                print(f"Unexpected error discovering services: {e}")
                await connection.disconnect()
                continue

            # Run the task to receive data from the peripheral
            tasks = [
                asyncio.create_task(receive_data_task(characteristic)),
            ]
            await asyncio.gather(*tasks)

            await connection.disconnected()
            print(f"Disconnected from {device.name()}")
            break  # End loop if successfully disconnected


asyncio.run(run_central_mode())
