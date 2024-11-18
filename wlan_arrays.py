import network
import socket
import time
from machine import Pin

# Setup network and temp_array
ssid = "test_wifi"
password = "SDP_Group2"

# Temperature in degrees Fahrenheit (approximate range for outdoor conditions)
temp_array = [68.5, 70.2, 72.0, 69.8, 71.6, 73.4, 74.1, 75.6, 68.9, 70.7]

# Humidity in relative humidity (RH), typical outdoor range
humid_array = [45.2, 47.8, 50.5, 49.3, 48.7, 46.1, 52.0, 49.8, 51.4, 47.3]

# UV sunlight in milliwatts per square meter (example range for UV index)
uv_array = [120, 145, 180, 160, 135, 150, 170, 140, 155, 165]

# Soil moisture on a scale of 318-791 (arbitrary calibration units)
moisture_array = [350, 410, 445, 380, 390, 430, 460, 370, 400, 420]

# pH values for soil, generally ranging between 4.5 (acidic) to 8.5 (alkaline)
ph_array = [6.8, 7.0, 6.5, 6.9, 7.1, 6.7, 6.6, 7.2, 6.4, 7.0]


# Setup Wi-Fi as access point
def setup_ap():
    ap = network.WLAN(network.AP_IF)
    ap.config(ssid=ssid, password=password)
    ap.active(True)
    while not ap.isconnected():
        time.sleep(1)
    print("Connected! IP = ", ap.ifconfig()[0])

# Generate HTML response with current temperature value
def web_page(temp_F, humid, uv, moisture, pH):
    html = f"""
        <!DOCTYPE html>
        <html>
        <body>
        <p>Temperature: {temp_F} </p>
        <p>Humidity: {humid} </p>
        <p>UV Light: {uv} </p>
        <p>Soil Moisture: {moisture} </p>
        <p>pH: {pH} </p>
        </body>
        </html>
        """
    return str(html)

# Setup socket
def open_socket():
    address = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(address)
    s.listen(3)
    return s

# Main loop to send each temperature in temp_array
setup_ap()
s = open_socket()
index = 0  # To track the current position in arrays

try:
    while (index < 10):
        client, _ = s.accept()
        request = client.recv(1024)
        request = str(request)

        # Get the current measurement in arrays
        temp_F = temp_array[index]
        humid = humid_array[index]
        uv = uv_array[index]
        moisture = moisture_array[index]
        pH = ph_array[index]
        html = web_page(temp_F, humid, uv, moisture, pH)

        # Send HTTP response
        client.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send(html)
        client.close()

        # Move to the next temperature value, loop back to the start if at the end
        index = index + 1

        # Interval between updates
        time.sleep(5)
        
finally:
    # Close the socket if the loop is interrupted
    s.close()
