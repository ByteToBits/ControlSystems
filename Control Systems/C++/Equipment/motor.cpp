
#include "motor.h"

#include <iostream>
#include <chrono>

Motor::Motor()
  : runStatus(false),
    tripStatus(false),
    selectorMode(false),
    scadaMotor()
{}

/**
 * @brief Triggers an Activation of an Alarm after the Trigger Condition remain True for a user-defined period of time.
 * @param enable Enable this particular Alarm (True = Alarm Enabled | False = Alarm Disabled)
 * @param trigger Condition to be met to start the alarm trigger countdown.
 * @param alarmTriggerDelay The delay (in milliseconds) before the alarm active flag is triggered.
 * @return The alarm active flag (true if alarm is triggered, false otherwise).
 */
bool Motor::alarmDelayCounter(bool enable, bool trigger, unsigned int alarmTriggerDelay)
{
    // Static Variables are Initialized only once during the first call of the function
    // Static Variables persists across subsequent calls to the function and  will remain unchanged unless explicitly updated
    static bool activeAlarm = false;
    static bool timerActive = false; 
    static auto alarmStartTime = std::chrono::steady_clock::time_point{}; // Initialize a Null Time

    if (trigger && enable)
    {
        if (!timerActive) // One the Rising Pulse of the 
        {
            alarmStartTime = std::chrono::steady_clock::now(); 
            timerActive = true; 
        }

        // Calculate the Elapsed Time
        auto currentTime = std::chrono::steady_clock::now(); 
        auto elapsedTime = std::chrono::duration_cast<std::chrono::milliseconds>(currentTime - alarmStartTime).count(); 

        if (elapsedTime >= alarmTriggerDelay)
        {
            activeAlarm = true;
        }
        else
        {  
            timerActive = false;
            activeAlarm = false; 
        }
    }
    return activeAlarm; 
}

/**
 * @brief Performs linear interpolation to estimate the value of a function at a given point.
 * @param x  The independent variable at which to interpolate.
 * @param x1 The first known independent variable.
 * @param x2 The second known independent variable.
 * @param y1 The dependent variable corresponding to x1.
 * @param y2 The dependent variable corresponding to x2.
 * @return The interpolated value of 'y' at the given 'x'
 */
float Motor::linearInterpolation(float x, float x1, float x2, float y1, float y2)
{
    return y1 + (x - x1)*((y2 - y1)/(x2 - x1)); 
}
