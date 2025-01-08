
// Description: Base Class Header for Motor Class
// Project: Industrial Process Control System
// Author: Tristan Sim
// Date: 30th December 2024
// Version: 1.01

#ifndef MOTOR_H // Include Guard: Checks if Class is not already defined during Compilation
#define MOTOR_H // Define: If Class is not Defined, Defines Class and prevents Re-Inclusion
// #pragma once - Short Way of doing it for ifndef

#include <iostream> 
#include <chrono>

#include <../Functions/utility_functions.h>

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

   // Constructor: Initialize Variables
   ScadaMotor()
     : fb_RunStatus(false),
       fb_SelectorMode(false),
       fb_TripStatus(false),
       fb_AlarmState(0),
       fb_RunHours(0), 
       fb_FailToStartCounter(0),
       fb_FailToStopCounter(0),
       ctrl_ControlMode(0),
       ctrl_FailToStartTimeLimit(60),
       ctrl_FailToStopTimeLimit(60) {}
};

class Motor 
{
   public:

      bool runStatus; 
      bool tripStatus; 
      bool selectorMode; 

      ScadaMotor scadaMotor; // Interface 

   private: 
      bool failToStartCounter(bool enable, bool trigger, unsigned int alarmTriggerDelay);
      bool failToStopCounter(bool enable, bool trigger, unsigned int alarmTriggerDelay);
      float scaleSpeedInput(float rawAnalogInput, float rawAnalogInputMin, float rawAnalogInputMax, float engineeringUnitMin, float engineeringUnitMax); 
};

#endif