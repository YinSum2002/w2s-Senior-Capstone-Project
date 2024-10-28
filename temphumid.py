# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_am2320
import busio

# create the I2C shared bus
i2c = busio.I2C(board.GP17, board.GP16)#, frequency=10000)  # uses board.SCL and board.SDA


# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
am = adafruit_am2320.AM2320(i2c)


while True:
    print("Temperature: ", am.temperature)
    #print("Humidity: ", am.relative_humidity)
    time.sleep(2)
