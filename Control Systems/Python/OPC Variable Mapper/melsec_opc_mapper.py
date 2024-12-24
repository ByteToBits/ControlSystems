import xml.etree.ElementTree as elementTree
import data_parser as dataParser
import data_processor as dataProcessor
import traceback
import os

rawDataDirectory= r"Control Systems\Python\OPC Variable Mapper\Data\Raw Data"
dataStructureDirectory = r"Control Systems\Python\OPC Variable Mapper\Data\Data Structures" 
outputDataDirectory = r"Control Systems\Python\OPC Variable Mapper\Data\Output"

scanRateSetting = 1000; 
headerString = ("Tag Name,Address,Data Type,Respect Data Type,Client Access,Scan Rate,Scaling,Raw Low,Raw High,"
                "Scaled Low,Scaled High,Scaled Data Type,Clamp Low,Clamp High,Eng Units,Description,Negate Value\n")
trailerPacket = f',,,,,,,,,"",'

print("\nOPC Variable Mapper (Flavour: MELSEC) Running...")

# Process 1: Get the Derived Data Types (Structures) from XML File into a Dictionary
dataStructure = {'Derived Data Types' : []}
try: 
  for files in os.listdir(dataStructureDirectory): 
    xmlFilePath = os.path.join(dataStructureDirectory, files) 
    structType, dataPacket = dataParser.fetchDataStructure(xmlFilePath); 
    dataStructure["Derived Data Types"].append({'Struct': structType, 'Variables': dataPacket})
  dataParser.printFormater(dataStructure, False)
  print("Success: Reading & Parsing Data Strucutre")
except Exception as e:
  print("Error: Reading & Parsing Data Strucutre - ", e)
  traceback.print_exc()

# Process 2: Get the Raw Data and Format the Data from XML File into a Dictionary
dataFile = {}
try: 
  for files in os.listdir(rawDataDirectory):
      xmlFilePath = os.path.join(rawDataDirectory, files)
      dataFile = dataParser.fetchRawData(xmlFilePath)
  dataParser.printFormater(dataFile, False)
  print("Success: Reading & Parsing Raw Data")
except Exception as e: 
  print("Error: Reading & Parsing Raw Data - ", e)
  traceback.print_exc()          

# Process 3: Data Wrangling - Map the raw data variables to their corresponding structure 
# primitive data types and append types to the dataFile.
try: 
  dataFile = dataParser.mapVariableTypes(dataFile, dataStructure)
  dataParser.printFormater(dataFile, False)
  print("Success: Data Wrangling Sucess")
except Exception as e: 
  print("Error: Mapping Data Types - ", e)
  traceback.print_exc()     

# Process 4: Data Cleaning - Remove any Variables with "Unknown" or Missing Primitive Data Type
dataCleaning = False; 
print("\nExecute: Data Cleaning (Flag = " + str(dataCleaning) + ")")
if dataCleaning: 
  print("Pre-Filter Data for 'Unknown' or Missing Primitive Data Type:")
  dataFile = dataParser.reportUnknownData(dataFile, dataCleaning, False)
  print("Post-Filter Data for 'Unknown' or Missing Primitive Data Type:")
  dataFile = dataParser.reportUnknownData(dataFile, dataCleaning, False)

# Proces 5: Data Filter - Omit the Unecessary Vairables From the Data File based on the Filter.csv
dataFilter = True; 
print("\nExecute: Data Filter (Flag = " + str(dataFilter) + ")")

# Process 6: Construct String Data for CSV File
print("\nExecute: Data Formatting\n")
contentList, fileName = dataProcessor.formatStringData(dataFile, scanRateSetting, headerString, trailerPacket)
dataParser.printFormater(contentList, False)

# Process 7: Write Data to CSV
try: 
  for fileName, globalVariables in dataFile.items():
    if fileName and globalVariables: 
      stringFileName = fileName.replace('SCADA_', "")
      outputDataDirectory = f'{outputDataDirectory}\\{stringFileName}.csv'
      with open(outputDataDirectory, "w", newline="") as file:
          file.writelines(contentList)     
  # print(f"CSV written to Destination: {outputDataDirectory}")
  print(f"Success: Data Written to CSV Files")
  print("Destination: " + fileName + ".csv")
except Exception as e: 
  print("Error: Writing Data to Destination - ", e)
  print("Destination: " + fileName)
  traceback.print_exc() 

print(f"End of Program\n")