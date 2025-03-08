#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

#define SERVICE_UUID "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "abcd1234-5678-1234-5678-abcdef123456"

#define VALUE_COUNT 10

// Define deep sleep options
//uint64_t uS_TO_S_FACTOR = 1000000;  // Conversion factor for micro seconds to seconds
// Sleep for 1 minute = 60 seconds
//uint64_t TIME_TO_SLEEP = 10;

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool dataSent = false;

// Dictionary of sensor data
struct SensorData {
    char label[6];
    float values[VALUE_COUNT];
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
        dataSent = false;
    }
    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
        Serial.println("Client Disconnected. Stopping BLE Advertising...");
        BLEDevice::getAdvertising()->stop();
    }
};

// Function to generate sensor data
void generateSensorData() {
  for (int i = 0; i < 6; i++) {
    for (int j = 0; j < VALUE_COUNT; j++) {
        sensors[i].values[j] = 0.0;  // Reset all sensor values to 0.0
    }
  }

  for (int i = 0; i < 10; i++) {
      sensors[0].values[i] = random(9500, 10500) / 100.0; // 95.00 - 105.00
  }
  for (int i = 0; i < 2; i++) {
      sensors[5].values[i] = random(600, 800) / 100.0;
      sensors[4].values[i] = random(6000, 8000);
  }
  for (int i = 0; i < 5; i++) {
      sensors[2].values[i] = random(3000, 7000) / 10; // 95.00 - 105.00
      sensors[3].values[i] = random(318, 791); // 95.00 - 105.00
      sensors[1].values[i] = random(10, 100) / 100.0; // 95.00 - 105.00
  }
}

void setup() {
    Serial.begin(115200);
    BLEDevice::init("RFID #12345");

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

    // Enable Timer wake_up
    //esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);

    generateSensorData();
}

void loop() {
    if (deviceConnected && !dataSent) {
        // Iterate through the sensor struct array
        for (int i = 0; i < 6; i++) {  // Loop through each sensor type
            for (int j = 0; j <= VALUE_COUNT; j++) {  // Loop through stored values
                if (sensors[i].values[j] != 0.0) {  // Skip zero values
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

