import xml.etree.ElementTree as elementTree
import data_parser as dataParser
import data_processor as dataProcessor
import data_writer as dataWriter
import traceback
import os

controllerType = "FX5" # iQR

rawDataDirectory= r"Control Systems\Python\OPC Variable Mapper\Data\Raw Data"
dataStructureDirectory = r"Control Systems\Python\OPC Variable Mapper\Data\Data Structures\\" + controllerType
outputDataDirectory = r"Control Systems\Python\OPC Variable Mapper\Data\Output"
filterDirectory = r"Control Systems\Python\OPC Variable Mapper\Data\Filter\\" + controllerType

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
dataFiles = []
try: 

  for files in os.listdir(rawDataDirectory):
      xmlFilePath = os.path.join(rawDataDirectory, files)
      dataFiles.append(dataParser.fetchRawData(xmlFilePath))
  
  print("\nSuccess: Reading & Parsing Raw Data")
  print("Total Number of Raw Data File: " + str(len(dataFiles)))

  for dataFile in dataFiles: 
    dataParser.printFormater(dataFile, False)
    for globalVar, rawDataContents in dataFile.items(): 
      print("File: " + globalVar + ".xml")
      print("Structure Variables:")

      # for structName, structMetaData in rawDataContents.items(): 
      #   print("Struct: " + structName + " | Structure Type: " + structMetaData.get('Struct'))

except Exception as e: 
  print("Error: Reading & Parsing Raw Data - ", e)
  traceback.print_exc()          


# Process 3: Data Wrangling - Map the raw data variables to their corresponding structure 
# primitive data types and append types to the dataFile.
try: 
  for i in range(len(dataFiles)):
    dataFiles[i] = dataParser.mapVariableTypes(dataFiles[i], dataStructure)
    dataParser.printFormater(dataFiles[i], True)
  print("\nSuccess: Data Wrangling Sucess")

except Exception as e: 
  print("Error: Mapping Data Types - ", e)
  traceback.print_exc()     


# Process 4: Data Cleaning - Remove any Variables with "Unknown" or Missing Primitive Data Type
dataCleaning = True; 
print("\nExecute: Data Cleaning (Flag = " + str(dataCleaning) + ")")
if dataCleaning: 
  for dataFile in dataFiles: 
    print("Pre-Filter Data for 'Unknown' or Missing Primitive Data Type:")
    dataFile = dataParser.reportUnknownData(dataFile, dataCleaning, False)
    print("Post-Filter Data for 'Unknown' or Missing Primitive Data Type:")
    dataFile = dataParser.reportUnknownData(dataFile, dataCleaning, False)

# Proces 5: Data Filter - Omit the Unecessary Vairables From the Data File based on the Filter.csv
dataFilter = True; 
print("\nExecute: Data Filter (Flag = " + str(dataFilter) + ")")
filterFiles = dataProcessor.getStructType(dataFiles) # Get the Structure Type which Corresponds to the Filter File Name
dataFiles = dataProcessor.filterVariables(True, dataFiles, filterFiles, filterDirectory) 
dataParser.printFormater(dataFiles, False)


# Process 6: Construct String Data for CSV File
print("\nExecute: Data Formatting\n")
contentList, fileName = dataProcessor.formatStringData(dataFiles[0], scanRateSetting, headerString, trailerPacket)
dataParser.printFormater(contentList, False)


# Process 7: Write Data to CSV
try: 
  dataWriter.writeDataToCSV(outputDataDirectory, dataFiles[0], contentList)
except Exception as e: 
  print("Error: Writing Data to Destination - ", e)
  traceback.print_exc() 

print(f"End of Program\n")
