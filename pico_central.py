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
    device = await ble_scan()
    if not device:
        print("No Peripheral found.")
        return

    try:
        print(f"Connecting to {device.name()}")
        connection = await device.device.connect()
    except asyncio.TimeoutError:
        print("Connection timed out.")
        return

    async with connection:
        try:
            service = await connection.service(_SERVICE_UUID)
            characteristic = await service.characteristic(_CHARACTERISTIC_UUID)
            await receive_data(characteristic)
        except Exception as e:
            print(f"Error discovering service/characteristic: {e}")
            await connection.disconnect()


asyncio.run(run_central_mode())
