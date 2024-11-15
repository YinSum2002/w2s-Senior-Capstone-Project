import time
from machine import Pin

# Initialize LEDs on pins 14, 15, and 16
led1 = Pin(10, Pin.OUT)
led2 = Pin(11, Pin.OUT)
led3 = Pin(12, Pin.OUT)

# Time delay between flashes (in seconds)
flash_delay = 0.5

def flash_led(led):
    print(led)
    led.on()  # Turn the LED on
    print(led.on())
    time.sleep(flash_delay)
    led.off()  # Turn the LED off
    print(led.off())
    time.sleep(flash_delay)

while True:
    flash_led(led1)  # Flash LED connected to pin 14
    flash_led(led2)  # Flash LED connected to pin 15
    flash_led(led3)  # Flash LED connected to pin 16
