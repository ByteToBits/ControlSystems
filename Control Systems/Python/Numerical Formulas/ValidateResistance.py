
import numpy
import SteinhartHartEquation
import PolynomialMethod
import NewtonRaphsonMethod

print("\nResistance Validation")

# Constants for Steinhart-Hart equation
A = 1.129240e-3  # Steinhart-Hart coefficient A
B = 2.341077e-4  # Steinhart-Hart coefficient B
C = 8.775468e-8  # Steinhart-Hart coefficient C

# Resistance at 0°C for PT1000
resistance_initial = 10000
# Initial guess for temperature
initialTempGuess = 10
# Tolerance for convergence
tolerance = 0.01  # Increased tolerance for faster convergence
max_iterations = 25000  # Maximum iterations to prevent infinite loop

coefficient_a = numpy.array([3.9083e-3, 3.9083e-3, 3.9083e-3], dtype=numpy.float64)
coefficient_b = numpy.array([-5.775e-7, -5.775e-7, -5.775e-7], dtype=numpy.float64)
coefficient_c = numpy.array([-4.183e-12, -4.183e-12, -4.183e-12], dtype=numpy.float64)

resistanceValues = numpy.array([11020.059, 11000.063, 11011.234], dtype=numpy.float64)

# Use Steinhart-Hart Equation
print("\nResistance Validation using Steinhart-Hart Equation (For NTC Thermistor)")
for i in range(len(resistanceValues)):
    Rt_measured = resistanceValues[i]
    # Calculate the temperature for the given resistance
    temperature = SteinhartHartEquation.calculate_temperature(Rt_measured, A, B, C)
    print(f"CH {i+1}: Resistance = {Rt_measured:.3f} Ohms | Temperature = {temperature:.3f}°C")

# Use Polynomial Equation using Callendar-Van Dusen Equation
print("\nResistance Validation using Polynomial Approach (Based on Callendar-Van Dusen Equation)")
for i in range(len(resistanceValues)):
    a = coefficient_a[i]
    b = coefficient_b[i]
    Rt_measured = resistanceValues[i]
    # Find the temperature
    temperature = PolynomialMethod.calculate_temperature(Rt_measured, resistance_initial, a, b)
    print(f"CH {i+1}: Resistance = {Rt_measured:.3f} Ohms | Temperature = {temperature:.3f}°C")

# Use Newton Raphson using Callendar-Van Dusen Equation
print("\nResistance Validation using Newton-Raphson Method (Based on Callendar-Van Dusen Equation)")
for i in range(len(resistanceValues)):
    a = coefficient_a[i]
    b = coefficient_b[i]
    c = coefficient_c[i]
    Rt_measured = resistanceValues[i]
    temperature = NewtonRaphsonMethod.calculate_temperature(Rt_measured, resistance_initial, a, b, c, initialTempGuess, tolerance, max_iterations)
    print(f"CH {i+1}: Resistance = {Rt_measured:.3f} | Temperature = {temperature:.3f}°C")

print("\nEnd Calcuations\n")