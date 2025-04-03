import numpy as np
import math

print("\nResistance Validation Steinhard-Hart Equation\n")

# Constants for Steinhart-Hart equation (these are example values, you need the correct values for your thermistor)
A = 1.143771e-3  # Steinhart-Hart coefficient A
B = 2.317285e-4  # Steinhart-Hart coefficient B
C = 9.624355e-8  # Steinhart-Hart coefficient C

resistanceValues = np.array([22422.93], dtype=np.float64)

# Function to calculate temperature in Celsius from resistance using Steinhart-Hart equation
def calculate_temperature(R, A, B, C):
    # Calculate the temperature in Kelvin using the Steinhart-Hart equation
    
    kelvin = - 273.15
    ln_R = np.log(R) # / np.log(2.71828)# Natural log of the resistance
    # ln_R1 = np.log(R) # Natural log of the resistance
    temperature_celsius = 1 / (A + B * ln_R + C * ln_R**3) + kelvin
    
    return temperature_celsius

# Loop through each resistance value, calculate the temperature, and print the result
for i in range(len(resistanceValues)):
    Rt_measured = resistanceValues[i]
    
    # Calculate the temperature for the given resistance
    temperature = calculate_temperature(Rt_measured, A, B, C)
    
    print(f"CH {i+103}: Resistance = {Rt_measured:.3f} Ohms | Temperature = {temperature:.4f}°C")

