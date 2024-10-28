import time
import json

# from get_uv import get_uv_data


# Simulating sensor data (replace these functions with actual sensor reading logic)
def get_temperature():
    # This is a placeholder for actual temperature reading logic
    return 24.5


def get_humidity():
    # This is a placeholder for actual humidity reading logic
    return 65.3


def main():
    # Get the current time in "YYYY-MM-DD HH:MM:SS" format
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Gather sensor data
    temperature = get_temperature()
    humidity = get_humidity()
    # uv = get_uv_data()

    # Create the data dictionary to be written to the JSON file
    sensor_data = {
        "time": current_time,
        "temperature": temperature,
        "humidity": humidity,
    }

    # Write the JSON data to a file
    with open("sensor_data.json", "w") as file:
        json.dump(sensor_data, file, indent=2)

    print("Data successfully written to sensor_data.json")


if __name__ == "__main__":
    main()
