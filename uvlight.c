#include <Wire.h>  // For I2C communication

#define VEML6075_ADDRESS 0x10  // The I2C address for VEML6075

// Function to read 16-bit data from a register
uint16_t read16(uint8_t reg) {
  Wire.beginTransmission(VEML6075_ADDRESS);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(VEML6075_ADDRESS, 2);
  uint16_t value = Wire.read();
  value |= (Wire.read() << 8);
  return value;
}

// Function to initialize the VEML6075 sensor
void setupVEML6075() {
  Wire.begin();
  // Example: Configure the VEML6075 sensor
  Wire.beginTransmission(VEML6075_ADDRESS);
  Wire.write(0x00);  // Configuration register
  Wire.write(0x0F);  // Example configuration value
  Wire.endTransmission();
}

// Function to get UV data
void getUVData(float *uvIndex, float *uva, float *uvb) {
  // Read UVA and UVB data from the sensor
  uint16_t uva_raw = read16(0x07);
  uint16_t uvb_raw = read16(0x09);

  // Convert raw data to actual UVA, UVB values (example calculation)
  *uva = uva_raw * 0.1;  // Adjust with your calibration factors
  *uvb = uvb_raw * 0.1;  // Adjust with your calibration factors
  *uvIndex =
      (*uva + *uvb) / 2.0;  // Example: Simple average calculation for UV index
}

void setup() {
  Serial.begin(9600);
  setupVEML6075();
  delay(100);
}

void loop() {
  float uvIndex, uva, uvb;

  // Get UV data
  getUVData(&uvIndex, &uva, &uvb);

  // Print data in JSON-like format
  Serial.print("{\"uv_index\": ");
  Serial.print(uvIndex);
  Serial.print(", \"uva\": ");
  Serial.print(uva);
  Serial.print(", \"uvb\": ");
  Serial.print(uvb);
  Serial.println("}");

  delay(1000);  // Wait for 1 second
}
