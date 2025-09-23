// Additional Board Manager
// https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
// XIAO_ESP32C3 - Simple BLE Slave (Just Connect)

#include "BLEDevice.h"
#include "BLEServer.h"
#include "BLEUtils.h"
#include "BLE2902.h"

// BLE Service and Characteristic UUIDs (must match master)
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "87654321-4321-4321-4321-cba987654321"

BLEServer* pServer = nullptr;
BLECharacteristic* pCharacteristic = nullptr;
bool deviceConnected = false;

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("MASTER CONNECTED!");
    }

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("MASTER DISCONNECTED - Restarting advertising...");
      BLEDevice::startAdvertising();
    }
};

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      // Just respond to any message with "PONG"
      pCharacteristic->setValue("PONG");
      pCharacteristic->notify();
      Serial.println("Received PING - Responded with PONG");
    }
};

void setup() {
  Serial.begin(115200);
  
  Serial.println("Simple BLE Slave - ESP32-C3");
  Serial.println("Device name: ESP32_Slave_BLE");
  Serial.println("Waiting for master connection...");
  
  // Initialize BLE
  BLEDevice::init("ESP32_Slave_BLE");
  
  // Create server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  // Create service
  BLEService *pService = pServer->createService(SERVICE_UUID);
  
  // Create characteristic
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_WRITE |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );
  
  pCharacteristic->setCallbacks(new MyCallbacks());
  pCharacteristic->addDescriptor(new BLE2902());
  
  // Start service and advertising
  pService->start();
  BLEDevice::getAdvertising()->addServiceUUID(SERVICE_UUID);
  BLEDevice::startAdvertising();
  
  Serial.println("BLE advertising started!");
}

void loop() {
  // Simple status update every 5 seconds
  if (deviceConnected) {
    Serial.println("Status: Connected to master");
  } else {
    Serial.println("Status: Waiting for master connection...");
  }
  
  delay(5000);
}