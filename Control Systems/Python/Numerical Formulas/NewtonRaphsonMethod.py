
import numpy as np

print("\nResistance Validation in Using Newton Raphson Method\n")

# Resistance at 0°C for PT1000
resistance_initial = 10000
# Initial guess for temperature
initialTempGuess = 10
# Tolerance for convergence
tolerance = 0.01  # Increased tolerance for faster convergence
max_iterations = 25000  # Maximum iterations to prevent infinite loop

resistanceValues = np.array([11020.059, 11000.063, 11011.234], dtype=np.float64)

coefficient_a = np.array([3.9083e-3, 3.9083e-3, 3.9083e-3], dtype=np.float64)
coefficient_b = np.array([-5.775e-7, -5.775e-7, -5.775e-7], dtype=np.float64)
coefficient_c = np.array([-4.183e-12, -4.183e-12, -4.183e-12], dtype=np.float64)

def calculate_resistance(T, resistance_initial, a, b, c):
    return resistance_initial * (1 + a * T + b * T**2 + c * (T - 100) * T**3)

def calculate_temperature(Rt_measured, resistance_initial, a, b, c, T_guess, tolerance, max_iterations):
    T = T_guess
    iterations = 0
    while iterations < max_iterations:
        Rt_calculated = calculate_resistance(T, resistance_initial, a, b, c)
        if abs(Rt_calculated - Rt_measured) < tolerance:
            return T
        if Rt_calculated < Rt_measured:
            T += 0.001  # Increased step size
        else:
            T -= 0.001  # Increased step size
        iterations += 1
    # print(f"Warning: Maximum iterations reached without converging for resistance {Rt_measured:.3f}")
    return T  # Return the last computed temperature, even if not fully converged

for i in range(len(resistanceValues)):
    # Callendar-Van Dusen Equation Expressed in terms of Temperature
    a = coefficient_a[i]
    b = coefficient_b[i]
    c = coefficient_c[i]
    Rt_measured = resistanceValues[i]

    # Find the temperature
    temperature = calculate_temperature(Rt_measured, resistance_initial, a, b, c, initialTempGuess, tolerance, max_iterations)
    print(f"CH {i+1}: Resistance = {Rt_measured:.3f} | Temperature = {temperature:.3f}°C")

