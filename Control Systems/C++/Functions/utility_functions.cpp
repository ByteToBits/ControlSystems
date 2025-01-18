
#include "utility_functions.h"
#include <tuple>
#include <map>

// A namespace in C++ is essentially a way to group related functions, classes, variables, or objects together under a single name
// This organizes codes and prevents conflicts 

namespace UitlityFunctions 
{   
    //  Rising Edge: For Tracking the States of the Pulse Detection
    static std::map<int, bool> risingEdgePreviousStates; // Tracks Previous Signal State
    static std::map<int, bool> risingEdgePulseStates;   // Tracks Pulse States

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

    bool risingEdge(int signalID, bool &trigger)
    {
        // Check it's a Rising Flag Condition (Previous State: Low | Current State: High)
        if (!risingEdgePreviousStates[signalID] && trigger == true)
        {
            risingEdgePulseStates[signalID] = true;
        }

        
    }
}