#include <iostream>
#include "utilityFunctions.h"

int main() 
{
    bool trigger = false; 

    // Test Rising Edge
    trigger = true; 
    std::cout << "Signal 1 Rising Edge: " << std::boolalpha << UtilityFunctions::risingEdge(1, trigger) << std::endl; // Output: True

    trigger = true; 
    std::cout << "Signal 1 Rising Edge: " << std::boolalpha << UtilityFunctions::risingEdge(1, trigger) << std::endl; // Output: False

    trigger = false; 
    std::cout << "Signal 1 Falling Edge: " << std::boolalpha << UtilityFunctions::fallingEdge(1, trigger) << std::endl; // Output: True

    trigger = false; 
    std::cout << "Signal 1 Falling Edge: " << std::boolalpha << UtilityFunctions::fallingEdge(1, trigger) << std::endl; // Output: False

    trigger = true; 
    std::cout << "Signal 1 Rising Edge: " << std::boolalpha << UtilityFunctions::risingEdge(1, trigger) << std::endl; // Output: True

    trigger = false; 
    std::cout << "Signal 1 Falling Edge: " << std::boolalpha << UtilityFunctions::fallingEdge(1,trigger) << std::endl; // Output: True

    return 0;
}
