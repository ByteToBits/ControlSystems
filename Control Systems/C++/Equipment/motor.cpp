
#include <iostream>

class Motor 
{
    public: 
       bool runStatus;
       bool selectorMode;
       bool tripMode; 

       void startMotor()
       {
           std::cout << "Motor has Started\n"; 
       }

       void stopMotor()
       {
           std::cout << "Motor has Stopped\n";
       }
}; 

int main() 
{
    Motor motor1; 

    motor1.runStatus = true; 

    if (motor1.runStatus) {
        motor1.startMotor(); 
    } 
    else 
    {
        motor1.stopMotor(); 
    }
}