
#include "utility_functions.h"
#include <tuple>

// A namespace in C++ is essentially a way to group related functions, classes, variables, or objects together under a single name
// This organizes codes and prevents conflicts 

namespace UitlityFunctions 
{
    /**
     * @brief Triggers an Activation of an Alarm after the Trigger Condition remain True for a user-defined period of time.
     * @param enable Enable this particular Alarm (True = Alarm Enabled | False = Alarm Disabled)
     * @param trigger Condition to be met to start the alarm trigger countdown.
     * @param alarmTriggerDelay The delay (in milliseconds) before the alarm active flag is triggered.
     * @return The alarm active flag (true if alarm is triggered, false otherwise).
     */
    std::tuple<bool, unsigned int> alarmDelayCounter(bool enable, bool trigger, unsigned int alarmTriggerDelay)
    {
        // Static Variables are Initialized only once during the first call of the function
        // Static Variables persists across subsequent calls to the function and  will remain unchanged unless explicitly updated
        static bool activeAlarm = false;
        static bool timerActive = false; 
        static auto alarmStartTime = std::chrono::steady_clock::time_point{}; // Initialize a Null Time
        static auto elapsedTime = 0; 

        if (trigger && enable)
        {
            if (!timerActive) // One the Rising Pulse of the 
            {
                alarmStartTime = std::chrono::steady_clock::now(); 
                timerActive = true; 
            }

            // Calculate the Elapsed Time
            auto currentTime = std::chrono::steady_clock::now(); 
            elapsedTime = std::chrono::duration_cast<std::chrono::milliseconds>(currentTime - alarmStartTime).count(); 

            if (elapsedTime >= alarmTriggerDelay)
            {
                activeAlarm = true;
            }
            else
            {  
                timerActive = false;
                activeAlarm = false; 
                elapsedTime = 0; 
            }
        }

        return std::make_tuple(activeAlarm, elapsedTime); 
    }
    
    /**
     * @brief Clamps the Value with a Specifiec Maximum and Minimum Range.
     * Template allows the implementation that works with multiple data Types ensures type safety during compilation.
     * Templates are resolved during compile time, leading to less runtime overhead
     * @param value The Value to be Clamped
     * @param minimum The Minimum Value
     * @param maximum The Maximum Value
     * @return The Clamped Value  
     */
    template<typename T>
    T clamp(T value, T minimum, T maximum)
    {
        return std::max(minimum, std::min(maximum, value)); 
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
    float linearInterpolation(float x, float x1, float x2, float y1, float y2)
    {
        return y1 + (x - x1)*((y2 - y1)/(x2 - x1)); 
    }
}