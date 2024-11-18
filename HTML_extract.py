import socket
import time
import re

# Server IP address and port
server_ip = "192.168.4.1"
port = 80

# Array to store received values
temperature_data = []
humidity_data = []
uv_data = []
moisture_data = []
ph_data = []

def get_temperature(html_content):
    match = re.search(r"Temperature:\s*([\d.]+)", html_content)
    if match:
        return float(match.group(1))
    return None

def get_humidity(html_content):
    match = re.search(r"Humidity:\s*([\d.]+)", html_content)
    if match:
        return float(match.group(1))
    return None

def get_uv(html_content):
    match = re.search(r"UV Light:\s*([\d.]+)", html_content)
    if match:
        return float(match.group(1))
    return None

def get_moisture(html_content):
    match = re.search(r"Soil Moisture:\s*([\d.]+)", html_content)
    if match:
        return float(match.group(1))
    return None

def get_ph(html_content):
    match = re.search(r"pH:\s*([\d.]+)", html_content)
    if match:
        return float(match.group(1))
    return None

def fetch_html():
    addr = (server_ip, port)
    response = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(addr)
        s.send(b"GET / HTTP/1.1\r\nHost: " + server_ip.encode() + b"\r\nConnection: close\r\n\r\n")
        
        while True:
            data = s.recv(2048).decode()
            if not data:
                break
            response += data
    
    return response

# Main loop to fetch and store temperature data every interval
interval = 5  # Interval in seconds
max_readings = 10  # Match number of server values

while len(temperature_data) < max_readings:
    html_content = fetch_html()

    temperature = get_temperature(html_content)
    humidity = get_humidity(html_content)
    uv = get_uv(html_content)
    moisture = get_moisture(html_content)
    ph = get_ph(html_content)
    
    if temperature is not None:
        temperature_data.append(temperature)
        print(f"Temperature data added: {temperature}")
    else:
        print("Failed to retrieve temperature from HTML.")
    
    if humidity is not None:
        humidity_data.append(humidity)
        print(f"Humidity data added: {humidity}")
    else:
        print("Failed to retrieve humidity from HTML.")

    if uv is not None:
        uv_data.append(uv)
        print(f"UV data added: {uv}")
    else:
        print("Failed to retrieve UV from HTML.")

    if moisture is not None:
        moisture_data.append(moisture)
        print(f"Soil Moisture data added: {moisture}")
    else:
        print("Failed to retrieve soil moisture from HTML.")

    if ph is not None:
        ph_data.append(ph)
        print(f"pH data added: {ph} \n")
    else:
        print("Failed to retrieve pH value from HTML. \n")

    # Wait for the specified interval before fetching the next value
    time.sleep(interval)

# Print the final arrays of data
print("Final temperature readings:", temperature_data)
print("Final humidity readings:", humidity_data)
print("Final UV readings:", uv_data)
print("Final soil moisture readings:", moisture_data)
print("Final pH readings:", ph_data)
