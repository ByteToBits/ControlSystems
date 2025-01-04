
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

    bool alarmDelayCounter(bool enable, bool trigger, unsigned int alarmTriggerDelay);
    float linearInterpolation(float x, float x1, float x2, float y1, float y2); 
}

#endif
