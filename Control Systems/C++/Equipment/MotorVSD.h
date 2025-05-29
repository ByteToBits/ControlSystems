// Description: VSD Motor Class Header - Extends Motor Class with Speed Control
// Project: Industrial Process Control System
// Author: Tristan Sim
// Date: 30th December 2024
// Version: 1.02

#ifndef VSD_MOTOR_H
#define VSD_MOTOR_H

#include "Motor.h"

// Extended SCADA structure for VSD functionality
struct ScadaVSDMotor : public ScadaMotor {
    // Additional VSD-specific control variables
    double Ctrl_Value_Override;         // Manual Override Speed Control Value
    
    // Constructor: Initialize VSD-specific variables
    ScadaVSDMotor() : ScadaMotor(),
                      Ctrl_Value_Override(0.0) {}
};

class VSDMotor : public Motor 
{
public:
    // Constructor
    VSDMotor(int assignedPriority = 1);
    
    // Override the main execution method to include VSD functionality
    void execute(bool MA_Status, bool Run_Status, bool Trip_Status, bool Interlock, 
                bool Auto_Command, bool Sec_Pulse, int Speed_Input, double PID_Command);
    
    // VSD-specific output variables
    int Speed_Control;              // Analog output for speed control (raw value)
    int Frequency;                  // Frequency feedback output
    
    // Override SCADA interface with VSD version
    ScadaVSDMotor SCADA_VSD;
    
    // Provide access to base SCADA for compatibility
    ScadaMotor& getSCADA() { return SCADA_VSD; }

private:
    // VSD-specific internal variables
    double _Control_Output_Percent;     // Speed control output in percent
    double _Speed_Input_FL;             // Speed input as float
    double _Speed_Control_FL;           // Speed control as float  
    double _MinSpeedRaw;                // Minimum speed in raw units
    double _MaxSpeedRaw;                // Maximum speed in raw units
    double _Deadband;                   // Analog input deadband
    
    // VSD-specific private methods
    void handleSpeedControl(double PID_Command);
    void handleSpeedInput(int Speed_Input);
    void updateVSDScadaMapping();
    
    // Utility methods
    int floatToInt(double value);
    double intToFloat(int value);
    double linearInterpolation(double input, double inputMin, double inputMax, 
                              double outputMin, double outputMax);
    double limitDouble(double value, double min, double max);
};

#endif