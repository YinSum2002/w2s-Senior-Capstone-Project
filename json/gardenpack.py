import json
import os


def read_sensor_data(file_path):
    """Read sensor data from a text file and return as a dictionary."""
    sensor_data = {}
    try:
        with open(file_path, "r") as file:

            for line in file:
                for line in file:
                    print("Line: ", line, "\n")
                key, value = line.strip().split(": ")

                sensor_data[key] = float(value)  # Convert the values to float
    except Exception as e:
        print(f"Error reading {file_path}: {e}\n")
    return sensor_data


def consolidate_sensor_data(sensor_files):
    """Consolidate data from multiple sensor files into a single dictionary."""
    consolidated_data = {}
    for file_path in sensor_files:
        sensor_data = read_sensor_data(file_path)
        consolidated_data.update(sensor_data)
    return consolidated_data


def create_json_packet(sensor_data):
    """Create a JSON packet from the consolidated sensor data."""
    return json.dumps(sensor_data, indent=4)


# Specify the sensor files to read from
sensor_files = ["sensor_1.txt", "sensor_2.txt", "sensor_3.txt"]

# Check if files exist
sensor_files = [f for f in sensor_files if os.path.exists(f)]

# Consolidate sensor data
consolidated_data = consolidate_sensor_data(sensor_files)

# Create JSON packet
json_packet = create_json_packet(consolidated_data)

# Output the JSON packet
print(json_packet)
