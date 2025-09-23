// XIAO_ESP32C3 - BLE Version (Compatible with ESP32-C3)
// Additional Board Manager
// https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
// Simplified version with two main while loops

#include "BLEDevice.h"
#include "BLEClient.h"

// BLE Service and Characteristic UUIDs
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "87654321-4321-4321-4321-cba987654321"

BLEClient* pClient = nullptr;
BLERemoteCharacteristic* pRemoteCharacteristic = nullptr;
String targetDeviceName = "ESP32_Slave_BLE";

float signal_dist_alarm_setpoint = 5.0;

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32-C3 Bluetooth Master");
  
  // Initialize BLE
  BLEDevice::init("ESP32_Master_BLE");
  pClient = BLEDevice::createClient();
}

void loop() {
  // WHILE LOOP 1: Keep searching until device is found and connected
  while (!pClient->isConnected()) {
    Serial.println("Searching for device...");
    
    // Start scan
    BLEScan* pBLEScan = BLEDevice::getScan();
    pBLEScan->setActiveScan(true);
    BLEScanResults* pResults = pBLEScan->start(5, false);
    
    // Check each found device
    for (int i = 0; i < pResults->getCount(); i++) {
      BLEAdvertisedDevice device = pResults->getDevice(i);
      
      if (device.haveName() && String(device.getName().c_str()) == targetDeviceName) {
        Serial.println("Target device found! Connecting...");
        
        // Try to connect
        if (pClient->connect(&device)) {
          Serial.println("Connected successfully!");
          
          // Set up service and characteristic
          BLERemoteService* pService = pClient->getService(SERVICE_UUID);
          if (pService != nullptr) {
            pRemoteCharacteristic = pService->getCharacteristic(CHARACTERISTIC_UUID);
            if (pRemoteCharacteristic != nullptr) {
              Serial.println("Service and characteristic ready!");
              break; // Exit the for loop
            }
          }
          
          // If setup failed, disconnect and keep searching
          Serial.println("Service setup failed, disconnecting...");
          pClient->disconnect();
        }
      }
    }
    
    pBLEScan->clearResults();
    
    if (!pClient->isConnected()) {
      Serial.println("Device not found or connection failed, retrying in 2 seconds...");
      delay(2000);
    }
  }
  
  // WHILE LOOP 2: Stay connected and measure RSSI until connection breaks
  while (pClient->isConnected()) {
    // Get RSSI
    int rssi = pClient->getRssi();
    
    // Send ping to slave
    if (pRemoteCharacteristic != nullptr && pRemoteCharacteristic->canWrite()) {
      pRemoteCharacteristic->writeValue("PING");
    }

    float approx_slave_distance = calculateDistance(rssi);

    Serial.println("RSSI Signal Strength ");
    Serial.println("RSSI: " + String(rssi) + " dBm");
    Serial.println("Approximate Distance: " + String(approx_slave_distance) + " meters");

    if (approx_slave_distance > signal_dist_alarm_setpoint) {
      Serial.println("Alert: Slave Device Exceeded 5 meters from Master");
    }

    Serial.println(" ");
    
    delay(1000); // Measure every second
  }
  
  // If we get here, connection was lost
  Serial.println("Connection lost! Going back to search mode...");
  delay(1000);
}

float calculateDistance(int rssi) {
  if (rssi == 0) {
    return -1.0;
  }
  
  // Single formula based on your calibration points:
  // 0.3 meters at -30 dBm, 7 meters at -85 dBm
  // Using: distance = a * exp(b * |rssi|)
  
  double distance = 0.000346 * exp(0.1106 * abs(rssi));
  
  return distance;
}