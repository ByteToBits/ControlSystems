
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
      
      /**
       * @brief Triggers an Activation of an Alarm after the Trigger Condition remain True for a user-defined period of time.
       * @param trigger Condition to be met to start the alarm trigger countdown.
       * @param alarmTriggerDelay The delay (in milliseconds) before the alarm active flag is triggered.
       * @return The alarm active flag (true if alarm is triggered, false otherwise).
       */
      bool AlarmDelayCounter(bool trigger, unsigned int alarmTriggerDelay)
      {  
         // Static Variables are Initialized only once during the first call of the function
         // Static Variables persists across subsequent calls to the function and  will remain unchanged unless explicitly updated
         static bool activeAlarm = false;
         static bool timerActive = false; 
         static auto alarmStartTime = std::chrono::steady_clock::time_point{}; // Initialize Null Time 

         if (trigger) 
         {
            if (!timerActive) 
            {
               timerActive = true; 
               alarmStartTime = std::chrono::steady_clock::now(); // Track Start Time
            }
            // Calculate the Elapsed Time based on the Current Time - Start Time
            auto currentTime = std::chrono::steady_clock::now();
            auto elapsedTime = std::chrono::duration_cast<std::chrono::milliseconds>(currentTime-alarmStartTime).count(); 

            if (elapsedTime >= alarmTriggerDelay) 
            {
               activeAlarm = true; 
            }
         }
         else
         {
            timerActive = false; 
            activeAlarm = false; 
         }
         return activeAlarm; 
      }
};

#endif