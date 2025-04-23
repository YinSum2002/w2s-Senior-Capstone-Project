#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_TSL2591.h>
#include <Adafruit_VEML6075.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <SPI.h>
#include <SD.h>

// Create sensor instances
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);
Adafruit_VEML6075 uv = Adafruit_VEML6075();

RTC_DATA_ATTR int loopCounter = 0;

RTC_DATA_ATTR unsigned long wakeupTime = 0;
RTC_DATA_ATTR unsigned long sleepTime = 0;
RTC_DATA_ATTR unsigned long awakeDuration = 0;

#define SD_CS 5  // Chip Select pin
#define SERVICE_UUID "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "abcd1234-5678-1234-5678-abcdef123456"

#define PH_SENSOR_PIN 32  // GPIO 32 connected to the sensor's analog output
#define SOIL_MOISTURE_PIN 33  // GPIO 33 connected to the sensor's analog output

#define LED_DUTY_CYCLE 4   // LED indicating ESP is awake (duty cycling)
#define LED_SLEEP 16        // LED indicating ESP is in deep sleep
#define LED_BLE 17          // LED indicating ESP is transmitting data

#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  2        /* Time ESP32 will go to sleep (in seconds) */
#define MAX_ARRAY 300

// #define rfid 
#define rfid 136395207

#define MAX_JSON_ENTRIES 100  // Tune this as needed for memory constraints
RTC_DATA_ATTR char rtc_json_data[2048];  // Persisted JSON string buffer
RTC_DATA_ATTR int rtc_json_size = 0;     // Track current size of data
RTC_DATA_ATTR int fileIndex = 0;


BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool dataSent = false;
bool BLE_setup = false;

RTC_DATA_ATTR int bootCount = 0;

RTC_DATA_ATTR bool isSleeping = false;  // RTC variable to track sleep state

RTC_DATA_ATTR struct sensorData {
    char label[6];
    float values[MAX_ARRAY];
} sensors[4] = {
    {"LUX", {0}},   // Light values
    {"SOIL", {0}},  // Soil moisture values
    {"UV", {0}},    // UV index values
    {"PH", {0}}     // pH values
};
// Define sizes array separately
RTC_DATA_ATTR int sizes[4] = {6, 12, 6, 1};  // LUX, SOIL, UV, PH

class MyServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
        Serial.println("deviceConnected was just set to true");
        dataSent = false;
    }
    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
        Serial.println("Client Disconnected. Stopping BLE Advertising...");
        BLEDevice::startAdvertising();
    }
};

void configureSensor() {
  // Set gain and integration time for the TSL2591
  tsl.setGain(TSL2591_GAIN_LOW);        // Options: LOW, MED, HIGH, MAX
  tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS); // Options: 100MS, 200MS, 300MS, 400MS, 500MS, 600MS
}

void clearRTCData() {
  for (int i = 0; i < 4; i++) {
    // Optional: clear the label too, if needed
    // memset(sensors[i].label, 0, sizeof(sensors[i].label));
    
    // Zero out all sensor values
    for (int j = 0; j < MAX_ARRAY; j++) {
      sensors[i].values[j] = 0;
    }
  }
  Serial.println("RTC sensor data cleared.");
}

String serializeSensorData() {
  String json = "{";
  json += "\"RFID\":" + String(rfid) + ",";
  json += "\"DATA\":{";

  for (int i = 0; i < 4; i++) {
    json += "\"" + String(sensors[i].label) + "\":[";
    for (int j = 0; j < sizes[i]; j++) {
      json += String(sensors[i].values[j], 6);
      if (j < 12 - 1) json += ",";
    }
    json += "]";
    if (i < 3) json += ",";
  }

  json += "}}";  // Close "data" and root objects
  return json;
}

void appendSensorSnapshot() {
  // Step 1: Check the number of files on the SD card
  int fileCount = 0;
  String filenamePrefix = "/cycle_";
  File root = SD.open("/");
  
  // Count the number of files that start with "cycle_"
  while (File file = root.openNextFile()) {
    if (file.isDirectory()) continue;
    if (String(file.name()).startsWith(filenamePrefix)) {
      fileCount++;
    }
    file.close();
  }

  // Step 2: If there are 8 files, delete the oldest one
  if (fileCount >= 8) {
    int oldestFileIndex = -1;
    int oldestFileValue = INT_MAX;

    // Loop through the files again to find the one with the smallest index
    root.rewindDirectory();
    while (File file = root.openNextFile()) {
      if (file.isDirectory()) continue;
      if (String(file.name()).startsWith(filenamePrefix)) {
        int fileIndex = extractFileIndex(file.name());
        if (fileIndex < oldestFileValue) {
          oldestFileValue = fileIndex;
          oldestFileIndex = fileIndex;
        }
      }
      file.close();
    }

    // Step 3: Delete the oldest file
    if (oldestFileIndex != -1) {
      String oldestFileName = filenamePrefix + String(oldestFileIndex) + ".json";
      SD.remove(oldestFileName.c_str());
      Serial.println("Deleted oldest file: " + oldestFileName);
    }
  }

  // Step 4: Create a new file and save the data
  StaticJsonDocument<1024> doc;
  JsonArray rootJson = doc.to<JsonArray>();
  JsonObject container = rootJson.createNestedObject();
  JsonObject tagData = container.createNestedObject("12345");
  
  // Loop through each sensor
  for (int i = 0; i < 4; i++) {
    JsonArray arr = tagData.createNestedArray(sensors[i].label);
    for (int j = 0; j < loopCounter; j++) {
      // Check if the value is zero, and replace it with null (None in JSON)
      if (sensors[i].values[j] == 0) {
        arr.add(nullptr);  // Add null instead of zero
      } else {
        arr.add(sensors[i].values[j]);
      }
    }
  }

  // Create a unique filename
  String filename = "/cycle_" + String(fileIndex) + ".json";
  fileIndex++;  // Increment for the next write

  File file = SD.open(filename.c_str(), FILE_WRITE);
  if (file) {
    serializeJsonPretty(doc, file);
    file.close();
    Serial.println("Full snapshot written to SD:");
    serializeJsonPretty(doc, Serial);
    Serial.println("\nSaved to: " + filename);
  } else {
    Serial.println("Failed to write JSON to SD card.");
  }
}

// Helper function to extract the numerical index from a filename
int extractFileIndex(String filename) {
  int startIdx = filename.indexOf('_') + 1;
  int endIdx = filename.indexOf('.');
  String fileIndexStr = filename.substring(startIdx, endIdx);
  return fileIndexStr.toInt();
}

void printSensorData() {
    Serial.println("Stored Sensor Data:");

    for (int i = 0; i < 4; i++) {  // Loop through the 6 sensors
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

  pinMode(LED_DUTY_CYCLE, OUTPUT);
  pinMode(LED_SLEEP, OUTPUT);
  pinMode(LED_BLE, OUTPUT);

  delay(1000); //Take some time to open up the Serial Monitor

  wakeupTime = millis();  // Record when ESP wakes up
  Serial.println("ESP Woke Up at: " + String(wakeupTime) + " ms");

  // If waking from deep sleep, blink the sleep LED
  if (isSleeping) {
      for (int i = 0; i < 5; i++) {  // Blink LED2 (Sleep Indicator)
          digitalWrite(LED_SLEEP, HIGH);
          delay(500);
          digitalWrite(LED_SLEEP, LOW);
          delay(500);
      }
  }

  //Increment boot number and print it every reboot
  ++bootCount;
  Serial.println("Boot number: " + String(bootCount));

  /*
  First we configure the wake up source
  We set our ESP32 to wake up every 5 seconds
  */
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);

  while (!Serial);
  Wire.end();
  // Initialize I2C GPIO 25 (SCL) and GPIO 26 (SDA)
  Wire.begin(26, 25);

  delay(100);  // Give sensors time to wake up

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

  float sensorVals[4];
  bool includeFlags[4] = {false, false, false, false};

  if (loopCounter % 1 == 0){
    // Read the raw analog value from the sensor
    float raw_value = analogRead(SOIL_MOISTURE_PIN);

    // Convert the raw value to a percentage (assuming 0-100%)
    // Calibration: You may need to determine the min (dry) and max (wet) raw values for your sensor
    float min_raw = 0;   // Replace with your dry calibration value
    float max_raw = 4095; // Replace with your wet calibration value (for ESP32 ADC resolution)

    // Map the raw value to a percentage
    float moisture_percent = map(raw_value, min_raw, max_raw, 0, 100);
    moisture_percent = constrain(moisture_percent, 0, 100); // Ensure the value stays within 0-100%

    sensorVals[1] = moisture_percent;
    includeFlags[1] = true;

    sensors[1].values[loopCounter - 1] = moisture_percent;

    // Print the readings to the Serial Monitor
    Serial.print("Raw ADC Value: ");
    Serial.print(raw_value);
    Serial.print(" | Soil Moisture: ");
    Serial.print(moisture_percent, 1);  // Print moisture percentage with 1 decimal place
    Serial.println("%");
  }

  if (loopCounter % 2 == 0){
        // Get full-spectrum (visible + IR) and IR-only light levels
    uint32_t full = tsl.getFullLuminosity();
    uint16_t visible = full & 0xFFFF;
    uint16_t infrared = full >> 16;

    // Calculate Lux from the sensor readings
    float lux = tsl.calculateLux(visible, infrared);

    sensorVals[0] = lux;
    includeFlags[0] = true;

    sensors[0].values[loopCounter/2] = lux;


    // Print TSL2591 readings
    Serial.print(F("Visible Light: ")); Serial.print(visible);
    Serial.print(F(" | Infrared: ")); Serial.print(infrared);
    Serial.print(F(" | Lux: ")); Serial.print(lux);

    // // Read UVA, UVB, and calculate UV Index
    float uva = uv.readUVA();
    float uvb = uv.readUVB();
    float uvIndex = uv.readUVI();

    sensorVals[2] = uva;
    includeFlags[2] = true;

    sensors[2].values[loopCounter/2] = uva;

    // Print the readings to the Serial Monitor
    Serial.print("UVA: ");
    Serial.print(uva);
    Serial.print(" | UVB: ");
    Serial.print(uvb);
    Serial.print(" | UV Index: ");
    Serial.println(uvIndex);
  }

  if (loopCounter % 12 == 0){
    // Read the raw ADC value from the pH sensor
    float raw_ADC_value = analogRead(PH_SENSOR_PIN);

    // Convert raw value to voltage (ESP32 ADC resolution is 12-bit by default)
    float voltage = (raw_ADC_value / 4095.0) * 3.3;

    // Convert the voltage to pH value using calibration
    float pH = 3.5 * voltage;  // Adjust the multiplier and offset as needed

    sensorVals[3] = pH;
    includeFlags[3] = true;

    sensors[3].values[loopCounter/12] = pH;

    // Print pH readings
    Serial.print("Raw ADC Value: ");
    Serial.print(raw_ADC_value);
    Serial.print(" | Voltage: ");
    Serial.print(voltage, 2);
    Serial.print(" V | pH: ");
    Serial.println(pH, 2);
  }

  // Initialize SD card
  if (!SD.begin(SD_CS)) {
      Serial.println("SD card initialization failed!");
      return;
  }
  

  if (loopCounter % 12 == 0){
    digitalWrite(LED_BLE, HIGH); // Turn ON BLE LED
    appendSensorSnapshot();
    loop();
    delay(1000);
    digitalWrite(LED_BLE, LOW);  // Turn OFF BLE LED

    // Clear RTC memory after data is successfully written to the SD card
    clearRTCData();  // Custom function to clear RTC memory
    loopCounter = 0;
  }
  
  digitalWrite(LED_DUTY_CYCLE, HIGH);  // Turn ON duty cycle LED
  isSleeping = false;  // Reset sleep flag

  delay(3000);  // Simulating sensor readings

  Serial.println("Going to sleep now");
  digitalWrite(LED_DUTY_CYCLE, LOW);   // Turn OFF duty cycle LED. 
  isSleeping = true;  // Set sleep flag for next boot

  delay(1000);
  
  prepareForDeepSleep();

  Serial.println("This will never be printed");
}

void loop() {
  unsigned long connectionStartTime = millis();
  const unsigned long timeoutDuration = 30000; // 30 seconds until timeout
  const int chunkSize = 197;  // Safe BLE payload size for ESP32

  // --- Setup BLE server if not already set up ---
  if (!BLE_setup) {
    BLEDevice::init("RFID #136395207");
    BLEDevice::setMTU(200);  // Optional: increase MTU

    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

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

    BLE_setup = true;
  }

  printSensorData();  // Optional debug

  // --- Wait for BLE connection or timeout ---
  while (!deviceConnected && (millis() - connectionStartTime < timeoutDuration)) {
    delay(100);
  }

  // --- Only send if connected and not already sent ---
  if (deviceConnected && !dataSent) {
    dataSent = false;
    delay(2500);  // Wait a bit before starting transfer

    // Step 1: Serialize the RTC sensor data into a JSON string
    String jsonData = serializeSensorData();            // Convert struct to JSON
    const char* rtc_json_data = jsonData.c_str();       // Get raw C string
    int jsonLength = jsonData.length();                 // Get its length

    Serial.print("RTC Data Length: ");
    Serial.println(jsonLength);
    Serial.println(rtc_json_data);

    // Step 2: Send data in chunks
    for (int i = 0; i < jsonLength; i += chunkSize) {
      char chunk[chunkSize + 1];                        // +1 for null terminator
      int len = min(chunkSize, jsonLength - i);         // Adjust last chunk length
      strncpy(chunk, rtc_json_data + i, len);
      chunk[len] = '\0';

      Serial.print("Sending chunk: ");
      Serial.println(chunk);

      pCharacteristic->setValue((uint8_t*)chunk, len);
      pCharacteristic->notify();

      delay(1000);  // Optional tuning
    }

    // Step 3: Send optional end marker
    pCharacteristic->setValue("END");
    pCharacteristic->notify();

    dataSent = true;
    Serial.println("All data sent. Disconnecting...");

    BLE_setup = false;
    pServer->disconnect(0);  // Force disconnect
    return;
  }

  // --- If we reach timeout without connection ---
  else {
    Serial.println("Connection timeout. Resuming data collection loop.");

    BLE_setup = false;
    pServer->disconnect(0);  // Force disconnect
    return;
  }
}
