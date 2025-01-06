
#include "motor.h"

#include <iostream>
#include <chrono>

Motor::Motor(): 
  runStatus(false),
  tripStatus(false),
  selectorMode(false),
  scadaMotor()
{}

float Motor::scaleSpeedInput(float rawAnalogInput, float rawAnalogInputMin, float rawAnalogInputMax, float engineeringUnitMin, float engineeringUnitMax)
{
    return UtilityFunctions::linearInterpolation(rawAnalogInput, rawAnalogInputMin, rawAnalogInputMax, engineeringUnitMin, engineeringUnitMax); 
}

bool Motor::failToStartCounter(bool enable, bool trigger, unsigned int alarmTriggerDelay)
{
    return UtilityFunctions::alarmDelayCounter(enable, trigger, alarmTriggerDelay);
}

bool Motor::failToStopCounter(bool enable, bool trigger, unsigned int alarmTriggerDelay)
{
    return UtilityFunctions::alarmDelayCounter(enable, trigger, alarmTriggerDelay);
}