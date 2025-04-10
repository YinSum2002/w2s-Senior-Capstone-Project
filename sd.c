#include <SPI.h>
#include <SD.h>
#include <ArduinoJson.h>

#define SD_CS 5  // Change this if your CS pin is different

void setup() {
    Serial.begin(115200);
    delay(3000);  // Increase delay to 3 seconds

    // Initialize SD card
    if (!SD.begin(SD_CS)) {
        Serial.println("SD card initialization failed!");
        return;
    }

    Serial.println("ESP32 is running!");

    Serial.println("Initializing SD Card...");
    if (!SD.begin(SD_CS)) {
        Serial.println("SD card initialization failed!");
        return;
    }
    Serial.println("SD card initialized successfully!");

    File file = SD.open("/test.txt", FILE_WRITE);
    if (file) {
        Serial.println("Writing to file...");
        file.println("Hello, ESP32 SD Card!");
        file.close();
        Serial.println("Write successful.");
    } else {
        Serial.println("Failed to open file for writing.");
    }

    file = SD.open("/test.txt");
    if (file) {
        Serial.println("Reading file:");
        while (file.available()) {
            Serial.write(file.read());
        }
        file.close();
    } else {
        Serial.println("Failed to open file for reading.");
    }

  writeSensorData();
}

void loop() {
  // Do nothing in loop for now
}

void writeSensorData() {
  // Mock sensor data
  float moisture = random(300, 800) / 10.0;       // e.g., 30% to 80%
  float ambientLight = random(100, 1000);         // in lux
  float uvIndex = random(0, 100) / 10.0;          // e.g., 0.0 to 10.0
  float pH = random(550, 750) / 100.0;            // e.g., 5.5 to 7.5

  // Create JSON object
  StaticJsonDocument<4096> doc;
  doc["timestamp"] = millis();  // Just using millis as a fake timestamp
  doc["moisture"] = moisture;
  doc["ambient_light"] = ambientLight;
  doc["uv_index"] = uvIndex;
  doc["pH"] = pH;

  // Serialize JSON to string
  String output;
  serializeJson(doc, output);

  // Write to file
  File file = SD.open("/data.json", FILE_APPEND);
  if (file) {
    file.println(output);
    file.close();
    Serial.println("Data written to SD:");
    Serial.println(output);
  } else {
    Serial.println("Failed to open file for writing.");
  }
}
