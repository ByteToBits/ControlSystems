
SPECIFIC_HEAT_OF_WATER = 4.19 # kJ/kg C
 
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

# Sample Value 
motor1_power = 30; # kW
motor1_rated_efficiency = 0.9; # 90%
pump1_rated_efficiency = 0.8; # 80%
# print(cal_hydraulic_losses(motor1_power, motor1_rated_efficiency, pump1_rated_efficiency))

# Chilller System Values
chwst = 6.7     # Celsius
chwrt = 12.6    # Celsius
chwFlowRate = 84.10   # L/s

cwst = 29.4     # Celsius
cwrt = 35.5    # Celsius
cwFlowRate = 97.65   # L/s

chiller_power = 308 # kW

# Heat Gain (Building Load) 
qHeatGainRT = cal_kW_to_RT(cal_energy_equation(chwFlowRate, SPECIFIC_HEAT_OF_WATER, chwst, chwrt))

# Heat Rejected (Cooling Tower) 
qHeatRejectedRT = cal_kW_to_RT(cal_energy_equation(cwFlowRate, SPECIFIC_HEAT_OF_WATER, cwst, cwrt))

# Total Work Input (RT)
totalWorkInput = cal_kW_to_RT(chiller_power)

# Percent Heat Balance 
percentHeatBalance = cal_percent_heat_balance(qHeatGainRT, qHeatRejectedRT, totalWorkInput)

# Answer: Heat Gain: 591.14 RT | Heat Rejected: 709
print ("Heat Gain: " + str(round(qHeatGainRT,2)) + " RT and Heat Rejected: " + str(round(qHeatRejectedRT,2)) + " RT")
print("Percent Heat Balance: "+ str(round(percentHeatBalance,2)) + " % ")