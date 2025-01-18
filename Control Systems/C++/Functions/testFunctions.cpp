#include <iostream> 

#include "utility_functions.h"

int main() 
{
    bool trigger = false; 
    
    trigger = true; 
    std::cout<< "Signal 1 Rising Edge: " << std::boolalpha << UtilityFunctions::risingEdge(1, trigger) << std::endl; // Output True 

    trigger = true; 
    std::cout<< "Signal 1 Rising Edge: " << std::boolalpha << UtilityFunctions::risingEdge(1, trigger) << std::endl; // Output False 

    trigger = false; 
    std::cout<< "Signal 1 Rising Edge: " << std::boolalpha << UtilityFunctions::risingEdge(1, trigger) << std::endl; // Output False 
    
    trigger = true; 
    std::cout<< "Signal 1 Rising Edge: " << std::boolalpha << UtilityFunctions::risingEdge(1, trigger) << std::endl; // Output True 
}