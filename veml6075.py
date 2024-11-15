from machine import I2C, Pin
import time

# VEML6075 I2C address
VEML6075_ADDR = 0x10

# Register addresses
VEML6075_REG_CONF = 0x00      # Configuration register
VEML6075_REG_UVA = 0x07       # UVA data register
VEML6075_REG_UVB = 0x09       # UVB data register

# UV coefficients for UV index calculation
UVA_RESPONSIVITY = 0.0011
UVB_RESPONSIVITY = 0.00125

# I2C setup (using GP16 for SDA and GP17 for SCL)
i2c = I2C(0, scl=Pin(17), sda=Pin(16))

def initialize_veml6075():
    # Power on and configure the VEML6075 for UV measurements
    try:
        # Write to configuration register to enable UVA and UVB channels
        i2c.writeto_mem(VEML6075_ADDR, VEML6075_REG_CONF, b'\x00\x00')  # 0x00 00 config: power on, UV enabled
        print("VEML6075 initialized successfully.")
    except OSError as e:
        print("Failed to initialize VEML6075:", e)

def read_uv_data():
    try:
        # Read UVA and UVB values from their registers
        uva_data = i2c.readfrom_mem(VEML6075_ADDR, VEML6075_REG_UVA, 2)
        uvb_data = i2c.readfrom_mem(VEML6075_ADDR, VEML6075_REG_UVB, 2)
        
        # Convert bytes to integers
        uva = int.from_bytes(uva_data, 'little')
        uvb = int.from_bytes(uvb_data, 'little')
        
        return uva, uvb
    except OSError as e:
        print("Failed to read UV data:", e)
        return None, None

def calculate_uv_index(uva, uvb):
    # Calculate UV Index based on responsivity factors
    uva_index = uva * UVA_RESPONSIVITY
    uvb_index = uvb * UVB_RESPONSIVITY
    uv_index = (uva_index + uvb_index) / 2  # Average UVA and UVB indices

    return uv_index

# Initialize the sensor
initialize_veml6075()

# Main loop
while True:
    # Read UVA and UVB data
    uva, u3vb = read_uv_data()
    
    if uva is not None and uvb is not None:
        # Calculate and display UV index
        uv_index = calculate_uv_index(uva, uvb)
        print(f"UVA: {uva}, UVB: {uvb}, UV Index: {uv_index:.2f}")
    else:
        print("Error: Failed to read UVA/UVB values.")
    
    time.sleep(1)
