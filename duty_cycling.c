/*
Simple Deep Sleep with Timer Wake Up
=====================================
ESP32 offers a deep sleep mode for effective power
saving as power is an important factor for IoT
applications. In this mode CPUs, most of the RAM,
and all the digital peripherals which are clocked
from APB_CLK are powered off. The only parts of
the chip which can still be powered on are:
RTC controller, RTC peripherals ,and RTC memories

This code displays the most basic deep sleep with
a timer to wake it up and how to store data in
RTC memory to use it over reboots

This code is under Public Domain License.

Author:
Pranav Cherukupalli <cherukupallip@gmail.com>
*/

#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_TSL2591.h>
#include <Adafruit_VEML6075.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// Create sensor instances
Adafruit_AHTX0 aht;
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);
Adafruit_VEML6075 uv = Adafruit_VEML6075();

RTC_DATA_ATTR int loopCounter = 0;

RTC_DATA_ATTR unsigned long wakeupTime = 0;
RTC_DATA_ATTR unsigned long sleepTime = 0;
RTC_DATA_ATTR unsigned long awakeDuration = 0;

#define SERVICE_UUID "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "abcd1234-5678-1234-5678-abcdef123456"

#define PH_SENSOR_PIN 0  // GPIO 0 connected to the sensor's analog output
#define SOIL_MOISTURE_PIN 1  // GPIO 1 connected to the sensor's analog output

#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  5        /* Time ESP32 will go to sleep (in seconds) */
#define MAX_ARRAY 300

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool dataSent = false;

RTC_DATA_ATTR int bootCount = 0;

RTC_DATA_ATTR struct sensorData {
    char label[6];
    float values[MAX_ARRAY];
} sensors[6] = {
    {"TEMP", {0}},  // Temperature values
    {"HUMID", {0}}, // Humidity values
    {"LUX", {0}},   // Light values
    {"SOIL", {0}},  // Soil moisture values
    {"UV", {0}},    // UV index values
    {"PH", {0}}     // pH values
};

class MyServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
        Serial.println("deviceConnected was just set to true");
        dataSent = false;
    }
    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
        Serial.println("Client Disconnected. Stopping BLE Advertising...");
        BLEDevice::getAdvertising()->stop();
    }
};

void configureSensor() {
  // Set gain and integration time for the TSL2591
  tsl.setGain(TSL2591_GAIN_MED);        // Options: LOW, MED, HIGH, MAX
  tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS); // Options: 100MS, 200MS, 300MS, 400MS, 500MS, 600MS
}

/*
Method to print the reason by which ESP32
has been awaken from sleep
*/
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

void printSensorData() {
    Serial.println("Stored Sensor Data:");

    for (int i = 0; i < 6; i++) {  // Loop through the 6 sensors
        Serial.print(sensors[i].label);
        Serial.print(": [");

        for (int j = 0; j < loopCounter; j++) {  // Loop through float values
            if (sensors[i].values[j] != 0.0){
              Serial.print(sensors[i].values[j], 2); // Print 2 decimal places

              if (j < loopCounter - 1) {
                  Serial.print(", ");  // Add a comma between values
              }
            }
            
        }
        Serial.println("]");  // Close the array
    }
}

void prepareForDeepSleep() {
  sleepTime = millis();  // Record sleep time
  awakeDuration = sleepTime - wakeupTime;  // Calculate time spent awake

  Serial.println("ESP Going to Sleep at: " + String(sleepTime) + " ms");
  Serial.println("Time Awake: " + String(awakeDuration) + " ms");

  delay(1000);
  Serial.flush(); 
  esp_deep_sleep_start();
}

void setup(){
  Serial.begin(115200);
  
  delay(1000); //Take some time to open up the Serial Monitor

  wakeupTime = millis();  // Record when ESP wakes up
  Serial.println("ESP Woke Up at: " + String(wakeupTime) + " ms");

  //Increment boot number and print it every reboot
  ++bootCount;
  Serial.println("Boot number: " + String(bootCount));

  //Print the wakeup reason for ESP32
  print_wakeup_reason();

  BLEDevice::init("RFID #12345");
  pServer = BLEDevice::createServer();
  Serial.println("About to call MyServerCallbacks");
  pServer->setCallbacks(new MyServerCallbacks());
  Serial.println("Just called MyServerCallbacks");

  BLEService* pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_NOTIFY
                  );

  pService->start();
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pServer->getAdvertising()->start();

  /*
  First we configure the wake up source
  We set our ESP32 to wake up every 5 seconds
  */
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  Serial.println("Setup ESP32 to sleep for every " + String(TIME_TO_SLEEP) +
  " Seconds");

  while (!Serial);
  Wire.end();
  // Initialize I2C GPIO 8 (SCL) and GPIO 9 (SDA)
  Wire.begin(9, 8);

  delay(100);  // Give sensors time to wake up

  // Reinitialize all sensors
  if (!aht.begin()) {
      Serial.println("Failed to initialize AHT20 sensor!");
      while (1);
  }

  if (!tsl.begin()) {
      Serial.println(F("Could not find a valid TSL2591 sensor, check wiring!"));
      while (1);
  }

  if (!uv.begin()) {
      Serial.println("Failed to find VEML6075 sensor. Check wiring!");
      while (1);
  }

  Serial.println("All sensors initialized.");

  loopCounter++;

  if (loopCounter % 1 == 0){
    // Run the AHT20
    sensors_event_t humidity, temp;
    aht.getEvent(&humidity, &temp);

    sensors[0].values[loopCounter/1] = temp.temperature;
    sensors[1].values[loopCounter/1] = humidity.relative_humidity;

    // Print AHT20 readings
    Serial.print("Temp: "); Serial.print(temp.temperature); Serial.println(" °C");
    Serial.print("Humidity: "); Serial.print(humidity.relative_humidity); Serial.println(" %");
  }

  if (loopCounter % 2 == 0){
    // Read the raw analog value from the sensor
    int raw_value = analogRead(SOIL_MOISTURE_PIN);

    // Convert the raw value to a percentage (assuming 0-100%)
    // Calibration: You may need to determine the min (dry) and max (wet) raw values for your sensor
    float min_raw = 0;   // Replace with your dry calibration value
    float max_raw = 4095; // Replace with your wet calibration value (for ESP32 ADC resolution)

    // Map the raw value to a percentage
    float moisture_percent = map(raw_value, min_raw, max_raw, 0, 100);
    moisture_percent = constrain(moisture_percent, 0, 100); // Ensure the value stays within 0-100%

    sensors[3].values[loopCounter/2] = moisture_percent;

    // Print the readings to the Serial Monitor
    Serial.print("Raw ADC Value: ");
    Serial.print(raw_value);
    Serial.print(" | Soil Moisture: ");
    Serial.print(moisture_percent, 1);  // Print moisture percentage with 1 decimal place
    Serial.println("%");
  }

  if (loopCounter % 3 == 0){
    // Get full-spectrum (visible + IR) and IR-only light levels
    uint32_t full = tsl.getFullLuminosity();
    uint16_t visible = full & 0xFFFF;
    uint16_t infrared = full >> 16;

    // Calculate Lux from the sensor readings
    float lux = tsl.calculateLux(visible, infrared);

    sensors[2].values[loopCounter/3] = lux;

    // Print TSL2591 readings
    Serial.print(F("Visible Light: ")); Serial.print(visible);
    Serial.print(F(" | Infrared: ")); Serial.print(infrared);
    Serial.print(F(" | Lux: ")); Serial.println(lux);

    // // Read UVA, UVB, and calculate UV Index
    float uva = uv.readUVA();
    float uvb = uv.readUVB();
    float uvIndex = uv.readUVI();

    sensors[4].values[loopCounter/3] = uva;

    // Print the readings to the Serial Monitor
    Serial.print("UVA: ");
    Serial.print(uva);
    Serial.print(" | UVB: ");
    Serial.print(uvb);
    Serial.print(" | UV Index: ");
    Serial.println(uvIndex);

    // Read the raw ADC value from the pH sensor
    int raw_ADC_value = analogRead(PH_SENSOR_PIN);

    // Convert raw value to voltage (ESP32 ADC resolution is 12-bit by default)
    float voltage = (raw_ADC_value / 4095.0) * 3.3;

    // Convert the voltage to pH value using calibration
    float pH = 3.5 * voltage;  // Adjust the multiplier and offset as needed

    sensors[5].values[loopCounter/3] = pH;

    // Print pH readings
    Serial.print("Raw ADC Value: ");
    Serial.print(raw_ADC_value);
    Serial.print(" | Voltage: ");
    Serial.print(voltage, 2);
    Serial.print(" V | pH: ");
    Serial.println(pH, 2);
  }

  /*
  Next we decide what all peripherals to shut down/keep on
  By default, ESP32 will automatically power down the peripherals
  not needed by the wakeup source, but if you want to be a poweruser
  this is for you. Read in detail at the API docs
  http://esp-idf.readthedocs.io/en/latest/api-reference/system/deep_sleep.html
  Left the line commented as an example of how to configure peripherals.
  The line below turns off all RTC peripherals in deep sleep.
  */
  //esp_deep_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
  //Serial.println("Configured all RTC Peripherals to be powered down in sleep");

  /*
  Now that we have setup a wake cause and if needed setup the
  peripherals state in deep sleep, we can now start going to
  deep sleep.
  In the case that no wake up sources were provided but deep
  sleep was started, it will sleep forever unless hardware
  reset occurs.
  */
  // Serial.println("Still accepting changes");

  if (loopCounter % 6 == 0){
    
    loop();
  }
  prepareForDeepSleep();

  Serial.println("This will never be printed");
}

void loop(){
  //This is not going to be called
  Serial.println("We are in the loop");

  printSensorData();

  if (deviceConnected){
    Serial.println("deviceConnected");
  }
  if (!dataSent){
    Serial.println("!dataSent");
  }
  if (deviceConnected && !dataSent) {
    Serial.println("Waiting for BLE to be ready...");
    delay(2000);  // Give BLE some time before sending
    for (int i = 0; i < 6; i++) {  // Loop through each sensor type
        Serial.println("Entered loop of 6");
        for (int j = 0; j <= loopCounter; j++) {  // Loop through stored values
            Serial.println("Entered loop of loopCounter");
            if (sensors[i].values[j] != 0.0) {  // Skip zero values
                Serial.println("sensors[i].values[j] != 0.0");
                String message = String(sensors[i].label) + ":" + String(sensors[i].values[j], 2);
                pCharacteristic->setValue(message.c_str());
                pCharacteristic->notify();
                Serial.println("Sent: " + message);
                delay(2000);  // Ensures reliable transmission
            }
        }
    }

    dataSent = true;
    Serial.println("All data sent. Disconnecting...");
    pServer->disconnect(0);  // Force disconnect
    return;
  }
}
