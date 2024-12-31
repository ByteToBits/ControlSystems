
// Description: Base Class Header for Motor Class
// Project: Industrial Process Control System
// Author: Tristan Sim
// Date: 30th December 2024
// Version: 1.01

#ifndef MOTOR_H // Include Guard: Checks if Class is not already defined during Compilation
#define MOTOR_H // Define: If Class is not Defined, Defines Class and prevents Re-Inclusion

#include <iostream> 
#include <chrono>

// Structure: SCADA Motor 
// Operator Interface with the Motor Class
struct ScadaMotor
{  
   // Feedback Variables: Reaed-Only Access
   bool fb_RunStatus; 
   bool fb_SelectorMode;
   bool fb_TripStatus; 
   
   int fb_AlarmState;                     
   unsigned int fb_RunHours; 
   unsigned int fb_FailToStartCounter;
   unsigned int fb_FailToStopCounter; 

   // Control Variables: Read & Write Access
   int ctrl_ControlMode; 
   
   unsigned int ctrl_FailToStartTimeLimit; 
   unsigned int ctrl_FailToStopTimeLimit; 

   // Control Variables: Simulate Inputs (Should Physical Inputs be Unavailable)
   bool ctrl_SimulationMode; 
   bool ctrl_SimulateRunStatus; 
   bool ctrl_SimulateTripStatus; 
   bool ctrl_SimulateSelectorMode; 
};

class Motor 
{
   public:
      bool runStatus; 
      bool tripStatus; 
      bool selectorMode;      

   private: 
      bool _runStatus; 

      bool AlarmCounter(bool trigger, unsigned int alarmTimer)
      {  
         // Initialize Static Variables
         // Static Variables are Initialized only once during the first call of the function
         // It persists across subsequent calls to the function
         // Static Variables will remain unchangedd unless explicitly updated
         static bool alarmTriggered = false; 
         static auto alarmCounter = std::chrono::steady_clock::time_point{}; // Initialize Null Time 

         if (trigger) {
            if (!alarmTriggered) {
               alarmTriggered = true; 
               alarmCounter = std::chrono::steady_clock::now(); // Track Start Time
            }
         }

         return false; 
      }
};

#endif