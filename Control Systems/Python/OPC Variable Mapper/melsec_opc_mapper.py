import xml.etree.ElementTree as elementTree
import data_parser as dataParser
import traceback
import os

rawDataDirectory= r"Control Systems\Python\OPC Variable Mapper\Data\Raw Data"
dataStructureDirectory = r"Control Systems\Python\OPC Variable Mapper\Data\Data Structures" 
outputDataDirectory = r"Control Systems\Python\OPC Variable Mapper\Data\Output"

scanRateSetting = 1000; 
headerString = ( "Tag Name,Address,Data Type,Respect Data Type,Client Access,Scan Rate,Scaling,Raw Low,Raw High,"
                 "Scaled Low,Scaled High,Scaled Data Type,Clamp Low,Clamp High,Eng Units,Description,Negate Value" )

#SCADA_FCU_6_10_VSD_Ctrl_Bypass_Shorterlock	D0001012.02	Boolean	1	R/W	750

print("\nOPC Variable Mapper (Flavour: MELSEC) Running...")

# Process 1: Get the Derived Data Types (Structures) from XML File into a Dictionary
dataStructure = {'Derived Data Types' : []}
try: 
  for files in os.listdir(dataStructureDirectory): 
    xmlFilePath = os.path.join(dataStructureDirectory, files) 
    structType, dataPacket = dataParser.fetchDataStructure(xmlFilePath); 
    dataStructure["Derived Data Types"].append({'Struct': structType, 'Variables': dataPacket})
  dataParser.printDictionary(dataStructure, False)
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
  dataParser.printDictionary(dataFile, False)
  print("Success: Reading & Parsing Raw Data")
except Exception as e: 
  print("Error: Reading & Parsing Raw Data - ", e)
  traceback.print_exc()          

# Process 3: Data Wrangling - Map the raw data variables to their corresponding structure 
# primitive data types and append types to the dataFile.
try: 
  dataFile = dataParser.mapVariableTypes(dataFile, dataStructure)
  dataParser.printDictionary(dataFile, False)
  print("Success: Data Wrangling Sucess")
except Exception as e: 
  print("Error: Mapping Data Types - ", e)
  traceback.print_exc()     

# Process 4: Data Cleaning - Remove any Variables with "Unknown" or Missing Primitive Data Type
dataCleaning = True; 
print("\nExecute: Data Cleaning (Flag = " + str(dataCleaning) + ")")
if dataCleaning: 
  print("Pre-Filter Data for 'Unknown' or Missing Primitive Data Type:")
  dataFile = dataParser.reportUnknownData(dataFile, dataCleaning, False)
  print("Post-Filter Data for 'Unknown' or Missing Primitive Data Type:")
  dataFile = dataParser.reportUnknownData(dataFile, dataCleaning, False)

# Proces 5: Data Filter - Omit the Unecessary Vairables From the Data File based on the Filter.csv
dataFilter = True; 
print("\nExecute: Data Filter (Flag = " + str(dataFilter) + ")")

# Process 6: Structure the Data and Write it to a CSV File
globalVariables = dataFile.keys() # Returns a Dictionary View of the Keys
if globalVariables: 
  for globalVariable in globalVariables:  # parentKey Need to be Iterated
    structVariables = list(dataFile[globalVariable].keys())
    for i in range(len(structVariables)): 
      print(structVariables[i])
      # for variable in structVariables: 
        # print(variable)