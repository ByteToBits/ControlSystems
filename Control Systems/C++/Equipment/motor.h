// Description: Motor Class Header - Updated to Match PLC Logic
// Project: Industrial Process Control System
// Author: Tristan Sim
// Date: 30th December 2024
// Version: 1.02

#ifndef MOTOR_H
#define MOTOR_H

#include <iostream> 
#include <chrono>
#include <../Functions/utility_functions.h>

_Status;
   int Ctrl_Simulate_Trip;
   
   // Constructor: Initialize Variables
   ScadaMotor()
     : FB_MA_Status(false), FB_Run_Status(false), FB_Trip_Status(false), FB_EStop_Status(true),
       FB_Command(0), FB_Fail_to_Start(false), FB_Fail_to_Stop(false), FB_Interlock(false),
       FB_Ready(false), FB_State(0), FB_Priority(99), FB_Speed_Feedback(0.0), FB_Speed_Output(0.0),
       FB_Run_Hours(0), FB_Start_Time(0), FB_Stop_Time(0),
       Ctrl_Mode(0), Ctrl_Initialize(false), Ctrl_Bypass_Interlock(false), Ctrl_Simulate_Mode(false),
       Ctrl_Simulate_MA_Mode(0), Ctrl_Simulate_Run_Status(0), Ctrl_Simulate_Trip(0),
       Ctrl_Fail_to_Stop_SP(120), Ctrl_Fail_to_Start_SP(120), Ctrl_Manual_Override_Speed(0.0),
       Ctrl_SI_EU_Max(100.0), Ctrl_SI_EU_Min(0.0), Ctrl_SI_RAW_Max(32000.0), Ctrl_SI_RAW_Min(-19200.0),
       Ctrl_SC_EU_Max(100.0), Ctrl_SC_EU_Min(0.0), Ctrl_SC_RAW_Max(32000.0), Ctrl_SC_RAW_Min(-19200.0),
       Ctrl_MaxSpeed(100.0), Ctrl_MinSpeed(40.0), Ctrl_Reset(0) {}

class Motor 
{
   public:
      // Constructor
      Motor(int assignedPriority = 1);
      
      // Main execution method (called cyclically like PLC scan)
      void execute(bool MA_Status, bool Run_Status, bool Trip_Status, bool Interlock, bool Auto_Command, bool Sec_Pulse);
      
      // Output variables (Function Block Outputs)
      bool Command;
      bool Permissive; 
      bool Fault_Alarm;
      bool Available;
      bool Running;
      int Priority;
      
      // SCADA Interface
      ScadaMotor SCADA;

   private: 
      // Internal state variables (matching PLC _variables)
      int _Mode;
      int _State;
      int _Command;
      bool _Permissive;
      bool _Available;
      int _Priority;
      int _Fault_Code;
      
      bool _MA_Status;
      bool _Run_Status;
      bool _Trip_Status;
      bool _Interlock;
      
      bool _Fault_Alarm;
      bool _Fail_to_Start;
      bool _Fail_to_Stop;
      
      unsigned int _Motor_Start_Counter;
      unsigned int _Motor_Stop_Counter;
      unsigned int _Sec_Counter;
      unsigned int _Run_Minutes;
      
      bool _First_Scan;
      int Assigned_Priority;
      
      // Rising/Falling edge detection IDs
      static int _risingEdgeID_Command;
      static int _fallingEdgeID_Command;
      static int _fallingEdgeID_RunStatus;
      
      // Private methods
      void initializeSetpoints();
      void handleInputMapping(bool MA_Status, bool Run_Status, bool Trip_Status, bool Interlock);
      void handleAlarmLogic();
      void handlePermissiveLogic();
      void handleStartStopLogic(bool Auto_Command);
      void handleFailCounters(bool Sec_Pulse);
      void handleRunHourTotalizer(bool Sec_Pulse);
      void updateScadaMapping();
      void updateOutputMapping();
      
      // Utility method wrappers
      bool risingEdge(int signalID, bool signal);
      bool fallingEdge(int signalID, bool signal);
      int limitInt(int value, int min, int max);
};

// Static member initialization
int Motor::_risingEdgeID_Command = 1000;
int Motor::_fallingEdgeID_Command = 1001;  
int Motor::_fallingEdgeID_RunStatus = 1002;

#endif