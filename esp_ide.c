#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2591.h>
#include <Adafruit_VEML6075.h>

#define PH_SENSOR_PIN 2  // GPIO 0 connected to the sensor's analog output
#define SOIL_MOISTURE_PIN 3  // GPIO 1 connected to the sensor's analog output

#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  15        /* Time ESP32 will go to sleep (in seconds) */

RTC_DATA_ATTR int bootCount = 0;

// Create sensor instances
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);
Adafruit_VEML6075 uv = Adafruit_VEML6075();
Adafruit_AHTX0 aht;

void configureSensor() {
  // Set gain and integration time for the TSL2591
  tsl.setGain(TSL2591_GAIN_MED);        // Options: LOW, MED, HIGH, MAX
  tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS); // Options: 100MS, 200MS, 300MS, 400MS, 500MS, 600MS
}

unsigned long previousTSLTime = 0;   // Last time TSL2591 was read
unsigned long previousVEMLTime = 0;  // Last time VEML6075 was read
unsigned long previousAHTTime = 0;   // Last time AHT20 was read
unsigned long previousPHTime = 0;    // Last time pH sensor was read
unsigned long previousCSMSTime = 0;  // Last time Moisture was read

const unsigned long TSL_INTERVAL = 15 * 1000; // 15 seconds in milliseconds
const unsigned long VEML_INTERVAL = 15 * 1000; // 15 seconds in milliseconds
const unsigned long AHT_INTERVAL = 30 * 1000; // 30 seconds in milliseconds
const unsigned long PH_INTERVAL = 60 * 1000;  // 60 seconds in milliseconds
const unsigned long CSMS_INTERVAL = 60 * 1000; // 60 seconds in milliseconds

void print_wakeup_reason(){
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason)
  {
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n",wakeup_reason); break;
  }
}

void setup() {
    Serial.begin(115200);
    delay(1000); //Take some time to open up the Serial Monitor

    //Increment boot number and print it every reboot
    ++bootCount;
    Serial.println("Boot number: " + String(bootCount));

    //Print the wakeup reason for ESP32
    print_wakeup_reason();

    /*
    First we configure the wake up source
    We set our ESP32 to wake up every 5 seconds
    */
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
    Serial.println("Setup ESP32 to sleep for every " + String(TIME_TO_SLEEP) +
    " Seconds");

    while (!Serial);
    
    // Initialize I2C GPIO 8 (SCL) and GPIO 9 (SDA)
    Wire.begin(9, 8);

    // Initialize the AHT20 Sensor
    if (!aht.begin()) {
        Serial.println("Failed to initialize AHT20 sensor!");
        while (1);
    }

    // Initialize the TSL2591 sensor
    if (!tsl.begin()) {
        Serial.println(F("Could not find a valid TSL2591 sensor, check wiring!"));
        while (1); // Halt execution
    }
    Serial.println(F("TSL2591 sensor initialized"));
    
    // Initialize the VEML6075 sensor
    if (!uv.begin()) {
      Serial.println("Failed to find VEML6075 sensor. Check wiring!");
      while (1); // Halt execution
    }

    // Configure the TSL2591 sensor
    configureSensor();
}

void loop() {
    unsigned long currentTime = millis(); // Get the current time

          // Run the TSL2591 sensor every 15 minutes
    if (currentTime - previousTSLTime >= TSL_INTERVAL) {
        previousTSLTime = currentTime;

        // Get full-spectrum (visible + IR) and IR-only light levels
        uint32_t full = tsl.getFullLuminosity();
        uint16_t visible = full & 0xFFFF;
        uint16_t infrared = full >> 16;

        // Calculate Lux from the sensor readings
        float lux = tsl.calculateLux(visible, infrared);

        // Print TSL2591 readings
        Serial.print(F("Visible Light: ")); Serial.print(visible);
        Serial.print(F(" | Infrared: ")); Serial.print(infrared);
        Serial.print(F(" | Lux: ")); Serial.println(lux);
    }

    // Run the VEML6075 sensor every 15 minutes
    if (currentTime - previousVEMLTime >= VEML_INTERVAL) {
        previousVEMLTime = currentTime;

        // Read UVA, UVB, and calculate UV Index
        float uva = uv.readUVA();
        float uvb = uv.readUVB();
        float uvIndex = uv.readUVI();

        // Print the readings to the Serial Monitor
        Serial.print("UVA: ");
        Serial.print(uva);
        Serial.print(" | UVB: ");
        Serial.print(uvb);
        Serial.print(" | UV Index: ");
        Serial.println(uvIndex);
    }

    // Run the AHT20 sensor every 30 minutes
    if (currentTime - previousAHTTime >= AHT_INTERVAL) {
        previousAHTTime = currentTime;

        sensors_event_t humidity, temp;
        aht.getEvent(&humidity, &temp);

        // Print AHT20 readings
        Serial.print("Temp: "); Serial.print(temp.temperature); Serial.println(" °C");
        Serial.print("Humidity: "); Serial.print(humidity.relative_humidity); Serial.println(" %");
    }

    // Run the pH sensor every 1 hour
    if (currentTime - previousPHTime >= PH_INTERVAL) {
        previousPHTime = currentTime;

        // Read the raw ADC value from the pH sensor
        int raw_value = analogRead(PH_SENSOR_PIN);

        // Convert raw value to voltage (ESP32 ADC resolution is 12-bit by default)
        float voltage = (raw_value / 4095.0) * 3.3;

        // Convert the voltage to pH value using calibration
        float pH = 3.5 * voltage;  // Adjust the multiplier and offset as needed

        // Print pH readings
        Serial.print("Raw ADC Value: ");
        Serial.print(raw_value);
        Serial.print(" | Voltage: ");
        Serial.print(voltage, 2);
        Serial.print(" V | pH: ");
        Serial.println(pH, 2);
    }

    // Run the Moisture sensor every 1 hour
    if (currentTime - previousCSMSTime >= CSMS_INTERVAL) {
        previousCSMSTime = currentTime;

        // Read the raw analog value from the sensor
        int raw_value = analogRead(SOIL_MOISTURE_PIN);

        // Convert the raw value to a percentage (assuming 0-100%)
        // Calibration: You may need to determine the min (dry) and max (wet) raw values for your sensor
        float min_raw = 0;   // Replace with your dry calibration value
        float max_raw = 4095; // Replace with your wet calibration value (for ESP32 ADC resolution)

        // Map the raw value to a percentage
        float moisture_percent = map(raw_value, min_raw, max_raw, 0, 100);
        moisture_percent = constrain(moisture_percent, 0, 100); // Ensure the value stays within 0-100%

        // Print the readings to the Serial Monitor
        Serial.print("Raw ADC Value: ");
        Serial.print(raw_value);
        Serial.print(" | Soil Moisture: ");
        Serial.print(moisture_percent, 1);  // Print moisture percentage with 1 decimal place
        Serial.println("%");
    }

    // Add a small delay to reduce CPU usage
    delay(100);
   
}
