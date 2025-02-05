
#ifndef UTILITY_FUNCTIONS_H
#define UTILITY_FUNCTIONS_H

#include <chrono>
#include <algorithm>

namespace UtilityFunctions 
{   
    /**
     * @brief Clamps the Value with a Specifiec Maximum and Minimum Range.
     * Template allows the implementation that works with multiple data Types ensures type safety during compilation.
     * Templates are resolved during compile time, leading to less runtime overhead
     * @param value The Value to be Clamped
     * @param minimum The Minimum Value
     * @param maximum The Maximum Value
     * @return The Clamped Value  
     */
    template <typename T>
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
    template <typename T>
    T linearInterpolation(T x, T x1, T x2, T y1, T y2)
    {
        return y1 + (x - x1)*((y2 - y1)/(x2 - x1)); 
    }

    std::tuple<bool, unsigned int> alarmDelayCounter(bool enable, bool trigger, unsigned int alarmTriggerDelay);

    bool risingEdge(int signalID, bool signalTrigger); 
    bool fallingEdge(int signalID, bool signalTrigger);

    std::tuple<bool, unsigned int, unsigned int> counterOnTimer(bool signalTrigger, unsigned timerLimit, bool resetTimer);
}

#endif
