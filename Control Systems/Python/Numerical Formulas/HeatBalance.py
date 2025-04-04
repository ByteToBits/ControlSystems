
# Heat Balance Equation for Building Construction Association (BCA) Greenmark
# Project: Sample Calculations
# Written by: Tristan Sim
# Date: 3/4/2025
# Reference: https://www1.bca.gov.sg/docs/default-source/docs-corp-buildsg/sustainability/periodic-energy-audits-code_edition-4-0s.pdf

SPECIFIC_HEAT_OF_WATER = 4.19 # kJ/kg C

# Sample Value 
motor1_power = 30; # kW
motor1_rated_efficiency = 0.9; # 90%
pump1_rated_efficiency = 0.8; # 80%

# Chilller System Values
chwst = 6.7     # Celsius
chwrt = 12.6    # Celsius
chwFlowRate = 84.10   # L/s
cwst = 29.4     # Celsius
cwrt = 35.5    # Celsius
cwFlowRate = 97.65   # L/s
chiller_power = 308 # kW

# Heat Energy Equation 
def cal_energy_equation(massFlowRate, specificHeatofWater, supplyTemp, returnTemp):   
    return massFlowRate*specificHeatofWater*(returnTemp - supplyTemp) 

# Hydraulic Losses
def cal_hydraulic_losses(motor_input_power, motor_rated_efficiency, pump_rated_efficiency):
    return (motor_input_power*motor_rated_efficiency*(1-pump_rated_efficiency))

# Adjusted Power Input to Compressor (W_in)
def cal_power_input_compressor(motor_input_power, motor_rated_efficiency):
    return motor_input_power*motor_rated_efficiency

# Percent Heat Balance
def cal_percent_heat_balance(q_evaporator, q_condenser, work_input): 
    return ((q_evaporator + work_input) - q_condenser)/q_condenser * 100

# Convert kW to RT
def cal_kW_to_RT(power_KW): 
    return power_KW/3.517

# Main Program --------------------------------------------------------------------------------------------

# Heat Gain (Building Load) 
qHeatGainRT = cal_kW_to_RT(cal_energy_equation(chwFlowRate, SPECIFIC_HEAT_OF_WATER, chwst, chwrt))

# Heat Rejected (Cooling Tower) 
qHeatRejectedRT = cal_kW_to_RT(cal_energy_equation(cwFlowRate, SPECIFIC_HEAT_OF_WATER, cwst, cwrt))

# Total Work Input (RT)
totalWorkInput = cal_kW_to_RT(chiller_power)

# Sample Motor Efficiency Calcuations
motorHydraulicLosses = cal_hydraulic_losses(motor1_power, motor1_rated_efficiency, pump1_rated_efficiency)

# Percent Heat Balance 
percentHeatBalance = cal_percent_heat_balance(qHeatGainRT, qHeatRejectedRT, totalWorkInput)

# Answer: Heat Gain: 591.14 RT | Heat Rejected: 709
print("\nFormula Below Does Not Hydraulic Lossess")
print("Motor 1 Hydraulic Losses: "+ str(round(motorHydraulicLosses,2)) + " kW\n")
print("Heat Gain: " + str(round(qHeatGainRT,2)) + " RT and Heat Rejected: " + str(round(qHeatRejectedRT,2)) + " RT")
print("Percent Heat Balance: "+ str(round(percentHeatBalance,2)) + " %\n")