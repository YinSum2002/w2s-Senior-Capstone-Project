#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

#define SERVICE_UUID "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "abcd1234-5678-1234-5678-abcdef123456"

// Define deep sleep options
//uint64_t uS_TO_S_FACTOR = 1000000;  // Conversion factor for micro seconds to seconds
// Sleep for 1 minute = 60 seconds
//uint64_t TIME_TO_SLEEP = 10;

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool dataSent = false;

// Dictionary of sensor data
std::map<std::string, std::vector<float>> sensorData = {
    {"TEMP", {}},
    {"SOIL", {}},
    {"LUX", {}},
    {"UV", {}},
    {"PH", {}},
    {"HUMIDITY", {}}
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
    sensorData["TEMP"].clear();
    sensorData["SOIL"].clear();
    sensorData["UV"].clear();
    sensorData["LUX"].clear();
    sensorData["PH"].clear();
    sensorData["HUMIDITY"].clear();

    for (int i = 0; i < 10; i++) {
        sensorData["TEMP"].push_back(random(9500, 10500) / 100.0); // 95.00 - 105.00
    }
    for (int i = 0; i < 2; i++) {
        sensorData["PH"].push_back(random(600, 800) / 100.0); // 6.00 - 8.00
        sensorData["UV"].push_back(random(6000, 8000));
    }
    for (int i = 0; i < 5; i++) {
        sensorData["HUMIDITY"].push_back(random(3000, 7000) / 100.0); // 30.00 - 70.00
        sensorData["SOIL"].push_back(random(318, 791));
        sensorData["HUMIDITY"].push_back(random(10, 100) / 100.0);
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
        // Iterate through dictionary keys
        for (auto& pair : sensorData) {
            std::string label = pair.first;  // "TEMP", "PH", "HUMIDITY", etc.
            for (float value : pair.second) {
                String message = String(label.c_str()) + ":" + String(value, 2);
                pCharacteristic->setValue(message.c_str());
                pCharacteristic->notify();
                Serial.println("Sent: " + message);
                delay(2000); // Ensures reliable transmission
            }
        }

        dataSent = true;
        Serial.println("All data sent. Disconnecting...");
        pServer->disconnect(0); // Force disconnect
    }

    if (!deviceConnected && dataSent) {
        Serial.println("Going to deep sleep to save battery...");
        //esp_deep_sleep_start(); // Put ESP32 in deep sleep
    }
}

