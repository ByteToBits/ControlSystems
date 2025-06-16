/*
Function Block: Motor - Electrically Commutated (EC) Fan (Modified VSD Function Block) 
Program Version: v1.01  (20-April-2024 ) 
Controller: Mitsubishi iQ-R (Process | Redundant) 
	
Company: Engie South East Asia
Programmer: Tristan Sim 
	
Description: Function Block to Control & Monitoring Variable Speed Drive Motor 
Remarks: For some Reason, DeviceXPlorer OPC Can't Write to Boolean
*/

#include "Motor.h"
#include <iostream>
#include <chrono>

// Static member definitions (moved from header to avoid linker errors)
int Motor::_risingEdgeID_Command = 1000;
int Motor::_fallingEdgeID_Command = 1001;  
int Motor::_fallingEdgeID_RunStatus = 1002;

Motor::Motor(int assignedPriority): 
  Command(false),
  Permissive(false),
  Fault_Alarm(false),
  Available(false),
  Running(false),
  Priority(99),
  SCADA(),
  _Mode(0),                         // Operating mode (0=Off, 1=Manual, 2=Auto, 3=Maintenance)
  _State(0),                        // Current motor state (0=Stop, 1=Run, 3=Maintenance, 4=Trip, 5=FailStart, 6=FailStop)
  _Command(0),                      // Motor command output (0=Stop, 1=Start)
  _Permissive(false),               // Permissive to run flag
  _Available(false),                // Available for auto operation flag
  _Priority(99),                    // Current priority (99=fault priority)
  _Fault_Code(99),                  // Default fault code
  _MA_Status(false),                // Manual/Auto selector status
  _Run_Status(false),               // Motor run status feedback
  _Trip_Status(false),              // Motor trip status feedback
  _Interlock(false),                // Interlock status
  _Fault_Alarm(false),              // Latching fault alarm flag
  _Fail_to_Start(false),            // Fail to start alarm flag
  _Fail_to_Stop(false),             // Fail to stop alarm flag
  _Motor_Start_Counter(0),          // Fail to start counter (seconds)
  _Motor_Stop_Counter(0),           // Fail to stop counter (seconds)
  _Sec_Counter(0),                  // Second counter for run hour totalizer
  _Run_Minutes(0),                  // Run minutes accumulator
  _First_Scan(true),                // First scan flag for initialization
  Assigned_Priority(assignedPriority) // Motor priority for sequencing
{
    // Increment static IDs for each instance to avoid conflicts
    _risingEdgeID_Command += 10;
    _fallingEdgeID_Command += 10;
    _fallingEdgeID_RunStatus += 10;
}

void Motor::execute(bool MA_Status, bool Run_Status, bool Trip_Status, bool Interlock, bool Auto_Command, bool Sec_Pulse)
{
    // Initialize setpoints on first scan or when requested
    if (_First_Scan || (SCADA.Ctrl_Initialize >= 1)) {
        initializeSetpoints();
        _First_Scan = false;
    }
    
    // Handle input mapping and simulation
    handleInputMapping(MA_Status, Run_Status, Trip_Status, Interlock);
    
    // Operator Control Mode validation - Catch any out of bounds errors
    if ((SCADA.Ctrl_Mode < 1) || (SCADA.Ctrl_Mode > 3)) {
        _Mode = 0; 
    } else {
        _Mode = SCADA.Ctrl_Mode;
    }
    
    // Execute main logic sequence (matching PLC order)
    handleAlarmLogic();
    handlePermissiveLogic();
    handleStartStopLogic(Auto_Command);
    handleFailCounters(Sec_Pulse);
    handleRunHourTotalizer(Sec_Pulse);
    updateScadaMapping();
    updateOutputMapping();
}

void Motor::initializeSetpoints()
{
    // Initialize SCADA Setpoint Variables
    // Fail to Start/Stop Timer Setpoint - In Seconds
    SCADA.Ctrl_Fail_to_Start_SP = 120;
    SCADA.Ctrl_Fail_to_Stop_SP = 120;
    
    // Speed Input (SI) Analog Input - Adjust based on AI Module
    SCADA.Ctrl_SI_RAW_Max = 32000.0;    // 20 mA
    SCADA.Ctrl_SI_RAW_Min = -19200.0;   // 4 mA
    SCADA.Ctrl_SI_EU_Max = 100.0;       // 100 %
    SCADA.Ctrl_SI_EU_Min = 0.0;         // 0 %
    
    // Speed Control (SC) Analog Output - Adjust based on AO Module
    SCADA.Ctrl_SC_RAW_Max = 32000.0;    // 20 mA
    SCADA.Ctrl_SC_RAW_Min = -19200.0;   // 4 mA
    SCADA.Ctrl_SC_EU_Max = 100.0;       // 100% Speed
    SCADA.Ctrl_SC_EU_Min = 0.0;         // 0% Speed
    
    SCADA.Ctrl_Initialize = 0;
    
    SCADA.Ctrl_MinSpeed = 40.0;         // Minimum Allowable Speed of EC Fan in %
    SCADA.Ctrl_MaxSpeed = 100.0;        // Maximum Allowable Speed of EC Fan in %
    
    // Due to DeviceXPlorer Not able to Read/Write to a Data Register Boolean
    SCADA.Ctrl_Reset = 0;
    SCADA.Ctrl_Manual_Override = 0;
}

void Motor::handleInputMapping(bool MA_Status, bool Run_Status, bool Trip_Status, bool Interlock)
{
    // Function Block Input Mapping: Digital Input
    if (SCADA.Ctrl_Simulate_Mode >= 1) {  // Simulate the Digital Input Values
        _MA_Status = (SCADA.Ctrl_Simulate_MA_Mode != 0);
        _Run_Status = (SCADA.Ctrl_Simulate_Run_Status != 0);
        _Trip_Status = (SCADA.Ctrl_Simulate_Trip != 0);
        
        if (_Mode == 3) { // If Maintenance Mode: Don't Register any Trip Alarm
            _Trip_Status = false;
            _Priority = _Fault_Code;
            _Available = false;
        }
    } else { // Write Digital Input Values to Local Variables
        _MA_Status = MA_Status;
        _Run_Status = Run_Status;
        
        if (_Mode == 3) { // If Maintenance Mode: Don't Register any Trip Alarm
            _Trip_Status = false;
            _Priority = _Fault_Code;
            _Available = false;
        } else {
            _Trip_Status = Trip_Status;
        }
    }
    
    // Function Block Input Mapping: Interlocks & Permissive
    if (SCADA.Ctrl_Bypass_Interlock >= 1) { // Interlock
        _Interlock = true;
    } else {
        _Interlock = Interlock;
    }
    
    // SCADA Mapping: Write Local Variables to SCADA Data Structure
    SCADA.FB_MA_Status = _MA_Status;
    SCADA.FB_Run_Status = _Run_Status;
    SCADA.FB_Interlock = _Interlock;
    
    // SCADA Mapping: Clamp into Binary Range the Control Reset and Override Speed Control INT
    // Due to DeviceXPlorer Not able to Read/Write to a Data Register Boolean
    SCADA.Ctrl_Reset = limitInt(SCADA.Ctrl_Reset, 0, 1);
    SCADA.Ctrl_Manual_Override = limitInt(SCADA.Ctrl_Manual_Override, 0, 1);
}

void Motor::handleAlarmLogic()
{
    // Alarm Handler: Latching Fault Alarm
    if (_Trip_Status && (_Mode != 3)) {
        _Fault_Alarm = true;
        _State = 4;
        SCADA.FB_Trip_Status = true;
        _Mode = 0;
        _Priority = _Fault_Code;
        _Available = false;
    }
    else if (_Fail_to_Start) {
        _Fault_Alarm = true;
        _State = 5;
        _Mode = 0;
        _Priority = _Fault_Code;
        _Available = false;
    }
    else if (_Fail_to_Stop) {
        _Fault_Alarm = true;
        _State = 6;
        _Mode = 0;
        _Priority = _Fault_Code;
        _Available = false;
    }
    
    // Normalize & Release Latching Fault Alarm
    if ((SCADA.Ctrl_Reset == 1) && !_Trip_Status) {
        _Fault_Alarm = false;
        _State = 0;
        
        // Reset Failed to Start/Stop Alarms
        _Motor_Start_Counter = 0;
        _Motor_Stop_Counter = 0;
        SCADA.FB_Trip_Status = false;
        _Fail_to_Start = false;
        _Fail_to_Stop = false;
        
        SCADA.Ctrl_Reset = 0;
        // Due to DeviceXPlorer Not able to Read/Write to a Data Register Boolean
        SCADA.Ctrl_Reset = 0;
        
        if (SCADA.Ctrl_Mode == 1) {
            SCADA.Ctrl_Mode = 0;
        }
    } else {
        SCADA.Ctrl_Reset = 0;
        // Due to DeviceXPlorer Not able to Read/Write to a Data Register Boolean
        SCADA.Ctrl_Reset = 0;
    }
}

void Motor::handlePermissiveLogic()
{
    // Permissive & Interlocks: Using Operator Precedence
    if (_Fault_Alarm) { // State: Fault
        _Permissive = false;
        _Available = false;
        _Priority = _Fault_Code;
        _Available = false;
    }
    else if (_Mode == 3) { // State: Maintenance
        _State = 3;
        _Permissive = false;
        _Available = false;
        _Command = 0;
        _Priority = _Fault_Code;
        _Available = false;
    }
    else {
        if (!_Fault_Alarm && _MA_Status) { // If Motor is Healthy and Selector Switch in Auto Mode
            if (_Mode == 2) {
                _Available = true;  // Motor is only Available to Start in Auto Mode
                _Priority = Assigned_Priority; // Assign it Valid Priority
            } else {
                _Available = false;
                _Priority = _Fault_Code;
            }
            
            _Permissive = _Interlock; // Interlocks need to be Satisfied or Bypass
            
            // Update State to Run/Stop Status
            if (_Run_Status) {
                _State = 1;
            } else {
                _State = 0;
            }
        } else { // If Motor Runs in Local Mode
            _Permissive = false;
            _Available = false;
            _Priority = _Fault_Code;
            
            if (_Run_Status) {
                _State = 1;
            } else {
                _State = 0;
            }
        }
    }
}

void Motor::handleStartStopLogic(bool Auto_Command)
{
    // Motor Start/Stop Control Logic
    if (_Permissive) {
        if ((_Mode == 2 && Auto_Command) || (_Mode == 1)) { // Motor Start Command
            _Command = 1;
        } else if ((_Mode == 2) && !Auto_Command) { // Auto Mode - Stop
            _Command = 0;
        } else { // All Mode Stops Motor
            _Command = 0;
        }
    } else {
        _Command = 0;
    }
}

void Motor::handleFailCounters(bool Sec_Pulse)
{
    // Fail to Start/Stop Alarm Section
    if (_MA_Status && (_Mode != 3)) {
        
        // Special Exception | Reset Counters if the status disappears for a while Start Command is True
        if ((_Command == 1) && fallingEdge(_fallingEdgeID_RunStatus, _Run_Status)) {
            _Motor_Start_Counter = 0;
        }
        
        if (_Command && !_Run_Status) { // Fail to Start Counter
            
            // On the Rising Edge of Start Command | Initialize Counter
            if (risingEdge(_risingEdgeID_Command, _Command)) {
                _Motor_Start_Counter = 0;
            }
            
            if (Sec_Pulse) { // Increment the Start Counter
                _Motor_Start_Counter = _Motor_Start_Counter + 1;
            }
            
            if (_Motor_Start_Counter > SCADA.Ctrl_Fail_to_Start_SP) {
                _Fail_to_Start = true;
            } else {
                _Fail_to_Start = false;
            }
        }
        else if (!_Command && _Run_Status) { // Fail to Stop Counter
            
            if (fallingEdge(_fallingEdgeID_Command, _Command)) {
                _Motor_Stop_Counter = 0;
            }
            
            if (Sec_Pulse) { // Increment the Stop Counter
                _Motor_Stop_Counter = _Motor_Stop_Counter + 1;
            }
            
            if (_Motor_Stop_Counter > SCADA.Ctrl_Fail_to_Stop_SP) {
                _Fail_to_Stop = true;
            } else {
                _Fail_to_Stop = false;
            }
        }
    }
    else if (!_Fault_Alarm) { // If Motor is Started Locally on the Local Control Panel (No Fault)
        if (_Run_Status) {
            _State = 1;
        } else {
            _State = 0;
        }
    }
}

void Motor::handleRunHourTotalizer(bool Sec_Pulse)
{
    // Motor Run Hour Totalizer
    if (Sec_Pulse && _Run_Status) { // Second Counter is Persistent
        _Sec_Counter = _Sec_Counter + 1;
        
        if (_Sec_Counter >= 60) { // Total Running Minutes
            _Run_Minutes = _Run_Minutes + 1;
            _Sec_Counter = 0;
        }
        
        // FIXED: This should check _Run_Minutes, not _Sec_Counter (which was just reset to 0)
        if (_Run_Minutes >= 60) { // Total Running Hour
            SCADA.FB_Run_Hours = SCADA.FB_Run_Hours + 1;
            _Run_Minutes = 0;
        }
    }
}

void Motor::updateScadaMapping()
{
    // SCADA Mapping: Write Local Variables to SCADA Data Structure
    SCADA.FB_State = _State;
    SCADA.FB_Command = _Command;
    SCADA.FB_Ready = _Available;
    SCADA.FB_Priority = _Priority;
    SCADA.FB_Fail_to_Start = _Fail_to_Start;
    SCADA.FB_Fail_to_Stop = _Fail_to_Stop;
    SCADA.FB_Start_Time = _Motor_Start_Counter;
    SCADA.FB_Stop_Time = _Motor_Stop_Counter;
}

void Motor::updateOutputMapping()
{
    // Function Block Output Mapping
    Command = (_Command != 0);
    Permissive = _Permissive;
    Fault_Alarm = _Fault_Alarm;
    Available = _Available;
    Running = _Run_Status;
    Priority = _Priority;
}

// Utility method wrappers
bool Motor::risingEdge(int signalID, bool signal)
{
    return UtilityFunctions::risingEdge(signalID, signal);
}

bool Motor::fallingEdge(int signalID, bool signal)
{
    return UtilityFunctions::fallingEdge(signalID, signal);
}

int Motor::limitInt(int value, int min, int max)
{
    if (value < min) return min;
    if (value > max) return max;
    return value;
}