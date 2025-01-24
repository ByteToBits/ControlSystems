
#include "utilityFunctions.h"
#include <tuple>
#include <map>

// A namespace in C++ is essentially a way to group related functions, classes, variables, or objects together under a single name
// This organizes codes and prevents conflicts 

// This Program will be compiled into a Static Library since it's call by many other Functions 
// Step 1: Compile as an Object File
// Step 2: Compile Object File as a Static Link
// Step 3: Compile and Link "Main Program"

namespace UtilityFunctions 
{   
    namespace { // Anonymous Namespace
        //  Rising and Falling Edge: For Tracking the States of the Pulse Detection
        std::map<int, bool> previousSignalState;   // Tracks Pulse States
    }

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
     * @brief Detects a Rising Edge Signal and Returns a Bool during the Rising Edge State
     * @param signalID A Unique Tracking ID for the Particular Signal
     * @param signalTrigger The Discrete Signal Trigger for the Rising Edge Pulse Detection
     * @return The Rising Edge Flag as a Boolean
     */
   bool risingEdge(int signalID, bool signalTrigger)
    {   
        bool risingEdgeFlag = false; 

        // Check it's a Rising Flag Condition (Previous State: Low | Current State: High)
        if (!previousSignalState[signalID] && signalTrigger == true) // (Low -> High)
        {   
            risingEdgeFlag = true; 
        }
        // Update Previous State for the Next Method Call
        previousSignalState[signalID] = signalTrigger; 

        return risingEdgeFlag; 
    }

    /**
     * @brief Detects teh Falling Edge of a Signal and Returns a Bool during the Rising Edge State
     * @param signalID A Unique Tracking ID for the Particular Signal
     * @param signalTrigger The Discrete Signal Trigger for the Rising Edge Pulse Detection
     * @return The Falling Edge Flag as a Boolean
     */
    bool fallingEdge(int signalID, bool signalTrigger)
    {
        bool fallingEdgeFlag = false; 
        if (previousSignalState[signalID] && signalTrigger == false)
        {
            fallingEdgeFlag = true; 
        }
        // Update Previous State for the Next Method Call
        previousSignalState[signalID] = signalTrigger; 

        return fallingEdgeFlag; 
    }

    /**
     * @brief Starts a Time Counter when the Input is True
     * @param signalTrigger The Boolean Flag that will activate the Timer
     * @param timerLimit The maximum time limit the Counter Function can count up to
     * @param resetTimer resets the Time Counter to 0 
     * @return Counter Time Limit Reach (Boolean) | Time Elapsed in Seconds | Time Elapsed in Milliseconds
     */
    std::tuple<bool, unsigned int, unsigned int> counterOn(bool signalTigger, unsigned int timeLimit, bool resetTimer)
    {
        
    }

}
