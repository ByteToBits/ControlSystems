/*
Extension VSD: This Script Extends the Normal Motor Script & 
Adds a Speed Input & Control for VSD

Function Block: VSD Motor - Variable Speed Drive Motor Control
Program Version: v1.01  (20-April-2024 ) 
Controller: Mitsubishi iQ-R (Process | Redundant) 
	
Author: Tristan Sim 
	
Description: Extends Motor Function Block with Variable Speed Drive Control
*/

#include "MotorVSD.h"
#include <cmath>

VSDMotor::VSDMotor(int assignedPriority) 
    : Motor(assignedPriority),  // Call base class constructor
      Speed_Control(0),
      Frequency(0),
      SCADA_VSD(),
      _Control_Output_Percent(0.0),
      _Speed_Input_FL(0.0),
      _Speed_Control_FL(0.0),
      _MinSpeedRaw(0.0),
      _MaxSpeedRaw(0.0),
      _Deadband(500.0)  // Overshoot or Undershoot Deadband
{
    // Copy base SCADA to VSD SCADA for inheritance
    static_cast<ScadaMotor&>(SCADA_VSD) = SCADA;
    // Update the base SCADA reference to point to our extended version
    SCADA = SCADA_VSD;
}

void VSDMotor::execute(bool MA_Status, bool Run_Status, bool Trip_Status, bool Interlock, 
                      bool Auto_Command, bool Sec_Pulse, int Speed_Input, double PID_Command)
{
    // Call base class execute method first
    Motor::execute(MA_Status, Run_Status, Trip_Status, Interlock, Auto_Command, Sec_Pulse);
    
    // Execute VSD-specific functionality
    handleSpeedControl(PID_Command);
    handleSpeedInput(Speed_Input);
    updateVSDScadaMapping();
}

void VSDMotor::handleSpeedControl(double PID_Command)
{
    // Speed Control: Control Output Value
    // Select Which Speed Control the VSD will use
    // Due to DeviceXPlorer Not able to Read/Write to a Data Register Boolean
    if (SCADA_VSD.Ctrl_Manual_Override >= 1) {
        _Control_Output_Percent = SCADA_VSD.Ctrl_Value_Override; // Manual Override
    } else {
        _Control_Output_Percent = PID_Command;
        SCADA_VSD.Ctrl_Value_Override = _Control_Output_Percent;
    }
    
    // Clamp Control Output
    _Control_Output_Percent = limitDouble(_Control_Output_Percent, 
                                         SCADA_VSD.Ctrl_SC_EU_Min, 
                                         SCADA_VSD.Ctrl_SC_EU_Max);
    SCADA_VSD.Ctrl_Value_Override = limitDouble(SCADA_VSD.Ctrl_Value_Override,
                                               SCADA_VSD.Ctrl_SC_EU_Min,
                                               SCADA_VSD.Ctrl_SC_EU_Max);
    
    SCADA_VSD.FB_Speed_Output = _Control_Output_Percent; // Map Value to SCADA
    
    // Linear Interpolation: Scaled Speed Control
    if (_Command == 1) { // Start Command Must be True to Write Control Output
        
        // Linear Interpolation
        if (((SCADA_VSD.Ctrl_SC_EU_Max - SCADA_VSD.Ctrl_SC_EU_Min) != 0.0) && 
            ((SCADA_VSD.Ctrl_SC_RAW_Max - SCADA_VSD.Ctrl_SC_RAW_Min) != 0.0)) {
            
            _Speed_Control_FL = linearInterpolation(_Control_Output_Percent,
                                                   SCADA_VSD.Ctrl_SC_EU_Min,
                                                   SCADA_VSD.Ctrl_SC_EU_Max,
                                                   SCADA_VSD.Ctrl_SC_RAW_Min,
                                                   SCADA_VSD.Ctrl_SC_RAW_Max);
        } else { // Catch Zero Division Error
            _Speed_Control_FL = SCADA_VSD.Ctrl_SC_RAW_Min;
        }
        
        // Clamp the Max and Minimum Speed - Need to Convert Engineering Values to RAW Form
        _MinSpeedRaw = linearInterpolation(SCADA_VSD.Ctrl_MinSpeed,
                                          SCADA_VSD.Ctrl_SC_EU_Min,
                                          SCADA_VSD.Ctrl_SC_EU_Max,
                                          SCADA_VSD.Ctrl_SC_RAW_Min,
                                          SCADA_VSD.Ctrl_SC_RAW_Max);
        
        _MaxSpeedRaw = linearInterpolation(SCADA_VSD.Ctrl_MaxSpeed,
                                          SCADA_VSD.Ctrl_SC_EU_Min,
                                          SCADA_VSD.Ctrl_SC_EU_Max,
                                          SCADA_VSD.Ctrl_SC_RAW_Min,
                                          SCADA_VSD.Ctrl_SC_RAW_Max);
        
        if (!(SCADA_VSD.Ctrl_Manual_Override >= 1)) {
            _Speed_Control_FL = limitDouble(_Speed_Control_FL, _MinSpeedRaw, _MaxSpeedRaw);
        }
        
    } else {
        _Speed_Control_FL = 0.0;
    }
    
    // Write to Analog Output
    Speed_Control = floatToInt(_Speed_Control_FL); // All Other Modes Set AO to 0
}

void VSDMotor::handleSpeedInput(int Speed_Input)
{
    // Speed Input: Calculate the Frequency Feedback
    if (_Run_Status) {
        _Speed_Input_FL = intToFloat(Speed_Input); // Convert to Float
        
        // Check for Analog Input Fault: Overshoot or Undershoot
        if (_Speed_Input_FL > SCADA_VSD.Ctrl_SI_RAW_Max + _Deadband) {
            _Speed_Input_FL = SCADA_VSD.Ctrl_SI_RAW_Max;
        } else if (_Speed_Input_FL < SCADA_VSD.Ctrl_SI_RAW_Min - _Deadband) {
            _Speed_Input_FL = SCADA_VSD.Ctrl_SI_RAW_Max;
        }
        
        // Linear Interpolation: Normalize Speed Input
        if (((SCADA_VSD.Ctrl_SI_RAW_Max - SCADA_VSD.Ctrl_SI_RAW_Min) != 0.0) && 
            ((SCADA_VSD.Ctrl_SI_EU_Max - SCADA_VSD.Ctrl_SI_EU_Min) != 0.0)) {
            
            SCADA_VSD.FB_Speed_Feedback = linearInterpolation(_Speed_Input_FL,
                                                             SCADA_VSD.Ctrl_SI_RAW_Min,
                                                             SCADA_VSD.Ctrl_SI_RAW_Max,
                                                             SCADA_VSD.Ctrl_SI_EU_Min,
                                                             SCADA_VSD.Ctrl_SI_EU_Max);
        } else { // Catch Zero Division Error
            SCADA_VSD.FB_Speed_Feedback = SCADA_VSD.Ctrl_SI_EU_Min;
        }
        
        Frequency = floatToInt(SCADA_VSD.FB_Speed_Feedback);
        
    } else {
        SCADA_VSD.FB_Speed_Feedback = 0.0;
        Frequency = 0;
    }
}

void VSDMotor::updateVSDScadaMapping()
{
    // Update base SCADA mapping first (calls parent method)
    // This is already done by the base class execute method
    
    // VSD-specific SCADA mappings are already updated in the individual methods
    // FB_Speed_Feedback and FB_Speed_Output are updated in their respective methods
}

// Utility method implementations
int VSDMotor::floatToInt(double value)
{
    return static_cast<int>(std::round(value));
}

double VSDMotor::intToFloat(int value)
{
    return static_cast<double>(value);
}

double VSDMotor::linearInterpolation(double input, double inputMin, double inputMax, 
                                    double outputMin, double outputMax)
{
    return outputMin + (input - inputMin) * ((outputMax - outputMin) / (inputMax - inputMin));
}

double VSDMotor::limitDouble(double value, double min, double max)
{
    if (value < min) return min;
    if (value > max) return max;
    return value;
}