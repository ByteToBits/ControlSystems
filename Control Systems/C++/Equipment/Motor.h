// Description: Motor Class Header - Updated to Match PLC Logic
// Project: Industrial Process Control System
// Author: Tristan Sim
// Date: 30th December 2024
// Version: 1.02

#ifndef MOTOR_H
#define MOTOR_H

#include <iostream> 
#include <chrono>
#include "../Functions/utility_functions.h"

// SCADA Data Structure - Matches PLC FB_Motor_SCADA
struct ScadaMotor {
    // Feedback variables - Write from Function Block to SCADA
    bool FB_MA_Status;          // Feedback: Manual/Auto selector switch status (0=Manual | 1=Auto)
    bool FB_Run_Status;         // Feedback: Run status (0=Stopped | 1=Running)
    bool FB_Trip_Status;        // Feedback: Trip status (0=Healthy | 1=Tripped)
    bool FB_EStop_Status;       // Feedback: Emergency stop status (0=Triggered | 1=Not triggered)
    int FB_Command;             // Feedback: Motor command output (0=Stop | 1=Start)
    bool FB_Fail_to_Start;      // Feedback: Fail to start alarm status
    bool FB_Fail_to_Stop;       // Feedback: Fail to stop alarm status
    bool FB_Interlock;          // Feedback: Interlock status (0=Prevent run | 1=Allow run)
    bool FB_Ready;              // Feedback: Equipment ready status (1=Ready in Auto mode)
    int FB_State;               // Feedback: Operating state (0=Stop | 1=Run | 3=Maintenance | 4=Trip | 5=FailStart | 6=FailStop)
    int FB_Priority;            // Feedback: Equipment priority for sequencing
    double FB_Speed_Feedback;   // Feedback: Speed feedback (frequency in Hz)
    double FB_Speed_Output;     // Feedback: Speed control output (percent)
    unsigned int FB_Run_Hours;  // Feedback: Accumulated run hours
    unsigned int FB_Start_Time; // Feedback: Last start timestamp
    unsigned int FB_Stop_Time;  // Feedback: Last stop timestamp
    
    // Control variables - Read from SCADA to Function Block
    int Ctrl_Mode;                      // Control: Operating mode (0=Override stop | 1=Override start | 2=Auto | 3=Maintenance)
    int Ctrl_Initialize;                // Control: Initialize function block (resets to defaults) - INT due to OPC issue
    int Ctrl_Bypass_Interlock;         // Control: Bypass interlock (1=Bypass active) - INT due to OPC issue
    int Ctrl_Simulate_Mode;             // Control: Simulation mode enable (1=Simulation active) - INT due to OPC issue
    int Ctrl_Simulate_MA_Mode;          // Control: Simulate MA switch (0=Manual | 1=Auto)
    int Ctrl_Simulate_Run_Status;       // Control: Simulate run status (0=Stopped | 1=Running)
    int Ctrl_Simulate_Trip;             // Control: Simulate trip (0=Normal | 1=Tripped)
    int Ctrl_Fail_to_Stop_SP;           // Control: Fail to stop timeout in seconds
    int Ctrl_Fail_to_Start_SP;          // Control: Fail to start timeout in seconds
    int Ctrl_Manual_Override;           // Control: Manual Override - INT due to OPC issue
    double Ctrl_Manual_Override_Speed;  // Control: Manual Override VSD speed control value
    double Ctrl_SI_EU_Max;              // Control: Speed input upper engineering units limit (Hz)
    double Ctrl_SI_EU_Min;              // Control: Speed input lower engineering units limit (Hz)
    double Ctrl_SI_RAW_Max;             // Control: Speed input upper raw signal limit (mA)
    double Ctrl_SI_RAW_Min;             // Control: Speed input lower raw signal limit (mA)
    double Ctrl_SC_EU_Max;              // Control: Speed output upper engineering units limit (%)
    double Ctrl_SC_EU_Min;              // Control: Speed output lower engineering units limit (%)
    double Ctrl_SC_RAW_Max;             // Control: Speed output upper raw signal limit (mA)
    double Ctrl_SC_RAW_Min;             // Control: Speed output lower raw signal limit (mA)
    double Ctrl_MaxSpeed;               // Control: Maximum speed limit (%)
    double Ctrl_MinSpeed;               // Control: Minimum speed limit (%)
    int Ctrl_Reset;                     // Control: Reset equipment and fault alarms - INT due to OPC issue
    
    // Constructor: Initialize Variables
    ScadaMotor()
        : FB_MA_Status(false), FB_Run_Status(false), FB_Trip_Status(false), FB_EStop_Status(true),
          FB_Command(0), FB_Fail_to_Start(false), FB_Fail_to_Stop(false), FB_Interlock(false),
          FB_Ready(false), FB_State(0), FB_Priority(99), FB_Speed_Feedback(0.0), FB_Speed_Output(0.0),
          FB_Run_Hours(0), FB_Start_Time(0), FB_Stop_Time(0),
          Ctrl_Mode(0), Ctrl_Initialize(0), Ctrl_Bypass_Interlock(0), Ctrl_Simulate_Mode(0),
          Ctrl_Simulate_MA_Mode(0), Ctrl_Simulate_Run_Status(0), Ctrl_Simulate_Trip(0),
          Ctrl_Fail_to_Stop_SP(120), Ctrl_Fail_to_Start_SP(120), Ctrl_Manual_Override(0),
          Ctrl_Manual_Override_Speed(0.0), Ctrl_SI_EU_Max(100.0), Ctrl_SI_EU_Min(0.0),
          Ctrl_SI_RAW_Max(32000.0), Ctrl_SI_RAW_Min(-19200.0), Ctrl_SC_EU_Max(100.0), Ctrl_SC_EU_Min(0.0),
          Ctrl_SC_RAW_Max(32000.0), Ctrl_SC_RAW_Min(-19200.0), Ctrl_MaxSpeed(100.0), Ctrl_MinSpeed(40.0),
          Ctrl_Reset(0) {}
};

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
      
      // Rising/Falling edge detection IDs (static members declared here, defined in .cpp)
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

#endif