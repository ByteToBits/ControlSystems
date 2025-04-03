
import numpy as np

print("\nResistance Validation using 2 Degree Polynomial\n")

# Resistance at 0°C for PT1000
resistance_initial = 10000
# Create Double Data type (64-Bit Floating Point Precision)
resistanceValues = np.array([11020.059, 11000.063, 11011.234], dtype=np.float64)

coefficient_a = np.array([3.9083e-3, 3.9083e-3, 3.9083e-3], dtype=np.float64)
coefficient_b = np.array([-5.775e-7, -5.775e-7, -5.775e-7], dtype=np.float64)
coefficient_c = np.array([-4.183e-12, -4.183e-12, -4.183e-12], dtype=np.float64)

def calculate_temperature(Rt_measured, resistance_initial, a, b):
    # Calculate the discriminant
    discriminant = a**2 - 4 * b * (1 - Rt_measured / resistance_initial)
    
    if discriminant < 0:
        print("Warning: No real solution for the temperature. Check resistance value.")
        return None  # Return None if there's no real solution
    
    # Calculate the temperature using the positive root of the quadratic formula
    T = (-a + np.sqrt(discriminant)) / (2 * b)
    return T

for i in range(len(resistanceValues)):
    # Get coefficients
    a = coefficient_a[i]
    b = coefficient_b[i]
    Rt_measured = resistanceValues[i]

    # Find the temperature
    temperature = calculate_temperature(Rt_measured, resistance_initial, a, b)
    
    if temperature is not None:
        print(f"CH {i+1}: Resistance = {Rt_measured:.3f} | Temperature = {temperature:.3f}°C")
    else:
        print(f"CH {i+1}: Could not calculate temperature for resistance {Rt_measured:.3f}")
