import aioble
import bluetooth
import asyncio
import struct
from sys import exit

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# IAM = "Central" # Change to 'Peripheral' or 'Central'
IAM = "Peripheral"

if IAM not in ['Peripheral','Central']:
    print("IAM must be either Peripheral or Central")
    exit()

if IAM == "Central":
    IAM_SENDING_TO = "Peripheral"
else:
    IAM_SENDING_TO = "Central"

MESSAGE = f"Hello from {IAM}!"

# Bluetooth parameters
BLE_NAME = f"{IAM}"  # You can dynamically change this if you want unique names
BLE_SVC_UUID = bluetooth.UUID(0x181A)
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_APPEARANCE = 0x0300
BLE_ADVERTISING_INTERVAL = 2000
BLE_SCAN_LENGTH = 5000
BLE_INTERVAL = 30000
BLE_WINDOW = 30000

# state variables
#message_count = 0

def encode_message(message):
    """ Encode a message to bytes """
    return message.encode('utf-8')

def decode_message(message):
    """ Decode a message from bytes """
    return message.decode('utf-8')

async def send_data_task(connection, characteristic):
    #global message_count
    while True:
        if not connection:
            print("Error: No connection in send_data")
            await asyncio.sleep(1)
            continue

        if not characteristic:
            print("Error: No characteristic provided in send_data")
            await asyncio.sleep(1)
            continue

        message = f"{MESSAGE}"
        #message_count += 1
        print(f"Sending: {message}")

        try:
            msg = encode_message(message)

            # Check if characteristic supports write before proceeding
            if hasattr(characteristic, 'write') and callable(getattr(characteristic, 'write')):
                await characteristic.write(msg)  # Added await

                # Added sleep to prevent flooding the connection
                await asyncio.sleep(1)

                # Attempt to read response
                if hasattr(characteristic, 'read') and callable(getattr(characteristic, 'read')):
                    response = await characteristic.read()  # Added await
                    if response:
                        print(f"{IAM} sent: {message}, received response: {decode_message(response)}")
                    else:
                        print(f"Warning: No response received after sending {message}")
                else:
                    print("Characteristic doesn't support reading")
            else:
                print("Characteristic doesn't support writing")

        except Exception as e:
            print(f"Error writing data: {e}")
            continue

        await asyncio.sleep(1)


async def receive_data_task(characteristic):
    #global message_count
    while True:
        try:
            if hasattr(characteristic, 'read') and callable(getattr(characteristic, 'read')):
                data = await characteristic.read()  # Added await to properly wait for the data
                if data:
                    print(f"{IAM} received: {decode_message(data)}")
                    if hasattr(characteristic, 'write') and callable(getattr(characteristic, 'write')):
                        await characteristic.write(encode_message("Got it"))  # Added await
                    else:
                        print("Characteristic doesn't support writing")
                else:
                    print("No data received")
            else:
                print("Characteristic doesn't support reading")

            await asyncio.sleep(1)
            #message_count += 1

        except asyncio.TimeoutError:
            print(f"Timeout waiting for data in {IAM}.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


async def run_peripheral_mode():
    """ Run the peripheral mode """

    # Set up the Bluetooth service and characteristic
    ble_service = aioble.Service(BLE_SVC_UUID)
    characteristic = aioble.Characteristic(
        ble_service,
        BLE_CHARACTERISTIC_UUID,
        read=True,
        notify=True,
        write=True,
        capture=True,
    )
    aioble.register_services(ble_service)

    print(f"{BLE_NAME} starting to advertise")

    while True:
        async with await aioble.advertise(
            BLE_ADVERTISING_INTERVAL,
            name=BLE_NAME,
            services=[BLE_SVC_UUID],
            appearance=BLE_APPEARANCE) as connection:
            print(f"{BLE_NAME} connected to another device: {connection.device}")

            tasks = [
                asyncio.create_task(send_data_task(connection, characteristic)),
            ]
            await asyncio.gather(*tasks)
            print(f"{IAM} disconnected")
            break

async def ble_scan():
    """ Scan for a BLE device with the matching service UUID """

    print(f"Scanning for BLE Beacon named {BLE_NAME}...")

    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == IAM_SENDING_TO and BLE_SVC_UUID in result.services():
                print(f"found {result.name()} with service uuid {BLE_SVC_UUID}")
                return result
    return None

async def run_central_mode():
    """ Run the central mode """

    # Start scanning for a device with the matching service UUID
    while True:
        device = await ble_scan()

        if device is None:
            continue
        print(f"device is: {device}, name is {device.name()}")

        try:
            print(f"Connecting to {device.name()}")
            connection = await device.device.connect()

        except asyncio.TimeoutError:
            print("Timeout during connection")
            continue

        print(f"{IAM} connected to {connection}")

        # Discover services
        async with connection:
            try:
                service = await connection.service(BLE_SVC_UUID)
                characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
            except (asyncio.TimeoutError, AttributeError):
                print("Timed out discovering services/characteristics")
                continue
            except Exception as e:
                print(f"Error discovering services {e}")
                await connection.disconnect()
                continue

            tasks = [
                asyncio.create_task(receive_data_task(characteristic)),
            ]
            await asyncio.gather(*tasks)

            await connection.disconnected()
            print(f"{BLE_NAME} disconnected from {device.name()}")
            break

async def main():
    """ Main function """
    while True:
        if IAM == "Central":
            tasks = [
                asyncio.create_task(run_central_mode()),
            ]
        else:
            tasks = [
                asyncio.create_task(run_peripheral_mode()),
            ]

        await asyncio.gather(*tasks)

asyncio.run(main())