
// Title: Modbus Master
// Project: Industrial Process Control System
// Author: Tristan Sim
// Date: 5th April 2025
// Version: 1.01

// Description: This Function Block is to Sequence the Polling of Each Modbus Device. To resolve the issue, where all Slaves in the Bus
//              Stops Responding when the are simultaneously polled. This script will poll each slave one by one. 

#include <iostream>
#include <chrono>
#include <thread>

int main() {
    
    const int TOTAL_SLAVES = 5;
    short numberOfEnabledSlaves[5] = {1, 1, 0, 1, 0}; 
    bool ModbusSlavesEnabled[5]; 

    short pollingDuration = 2; 
    short pollingDelay = 1; 

    std::cout << "\nModbus Master Started\n" << std::endl; 

    for (int i = 0; i < TOTAL_SLAVES; i++) {
    
       // Re-iniitalize Output
       bool enableFlag = true;

       for (int j = 0; j < TOTAL_SLAVES; j++) {
          ModbusSlavesEnabled[j] = false;
       };

       if (numberOfEnabledSlaves[i] == 1) {
           ModbusSlavesEnabled[i] = true;
           std::cout << "Modbus Slave " << i << " Enabled..." << std::endl; 
           std::this_thread::sleep_for(std::chrono::seconds(pollingDuration)); 
           enableFlag = true;
       } else {
           std::cout << "Modbus Slave " << i << " Disabled..." << std::endl;
       };

       std::cout << "Iteration " << i << " - Modbus Slave Status:" << std::endl;

       for (int j = 0; j < TOTAL_SLAVES; j++) {
           std::cout << ModbusSlavesEnabled[j] << " "; 
       };

       std::cout << std::endl;
       std::cout << "Poling Delay of " << pollingDelay << " seconds...\n" << std::endl; 

       if (enableFlag) {
          std::this_thread::sleep_for(std::chrono::seconds(pollingDelay));
       };
    
    };
    
    std::cout << "\nModbus Master Scan Cycle Completed" << std::endl;

    return 0;
}