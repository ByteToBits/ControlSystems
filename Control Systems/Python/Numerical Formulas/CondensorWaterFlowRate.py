

chillerOffset = 12.00 
# Constants for working in Celsius
deltaTemperature = 5.44  # temperature change in °C (equivalent to 5.45°F in Celsius)
specificHeatCapacityOfWater = 4190  # specific heat in J/g°C for water (Celsius)

# Chiller's cooling capacity in tons (RT)
chillerRefTonnage = 560  # cooling capacity in tons (RT)

# Conversion factor from RT to BTU/h (1 RT = 12,000 BTU/h) 
RT_to_BTU = 12000  

# Flow rate per refrigeration ton (GPM/RT) in Celsius
# massOfWater = (RT_to_BTU * 1055.06)  / (specificHeatCapacityOfWater * deltaTemperature)

# 12000 BTU/hr is required to cool 'massOfWater' per hour by 'deltaTemperature'. 
# 12000 BTU/hr =  'massOfWater'/hr =  'massOfWater'liter/h
flowRateGPMperRT = (RT_to_BTU * 1055.06)  / (specificHeatCapacityOfWater * deltaTemperature) * (0.264172/60)

# Output flow rate per refrigeration ton (GPM/RT)
print("Flow Rate (GPM/RT): " + str(round(flowRateGPMperRT, 3)))

# Flow rate in GPM for the total chiller tonnage
flowRateGPM = flowRateGPMperRT * chillerRefTonnage

# Output total flow rate in GPM
print("Flow Rate (GPM): " + str(round(flowRateGPM, 3)))

# Convert GPM to liters/second (L/s)
flowRateMetric = flowRateGPM * 0.0630901  # 1 GPM = 0.0630901 L/s

# Output flow rate in L/s
print("Flow Rate (L/s): " + str(round(flowRateMetric, 3)))


# Chiller Rated Flow Rate in L/s + With Chiller Compensation (Clamp between Chiller Minimum and Maximum)
chillerMinFlowRate = 85.0
chillerMaxFlowRate = 122.0
chillerDesignFlowRate = min(max((flowRateMetric + chillerOffset), chillerMinFlowRate),chillerMaxFlowRate)

# Output flow rate in L/s + With Chiller Compensation
print("Calculated Flow Rate (L/s): " + str(round(flowRateMetric, 3)))
print("Flow Rate (L/s) with Chiller Offset: " + str(round(chillerDesignFlowRate, 3)))

print(0.264172/60)