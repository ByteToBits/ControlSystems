
// Description: Base Class Header for Motor Class
// Project: Industrial Process Control System
// Author: Tristan Sim
// Date: 30th December 2024
// Version: 1.01

#ifndef MOTOR_H // Include Guard: Checks if Class is not already defined during Compilation
#define MOTOR_H // Define: If Class is not Defined, Defines Class and prevents Re-Inclusion

class Motor 
{
   public:
      bool runStatus; 
      bool selectorMode;      
      bool tripStatus; 
};

#endif