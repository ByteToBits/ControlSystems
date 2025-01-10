
import csv

def formatStringData(dataFile, scanRateSetting, headerString, trailerPacket): 
  """
  Function: Format Data File Dictionary to String Format

  Parameters:
  dataFile (dict): The Contents Extracted from the Raw Daw XML File
  scanRate (int): The Scan Rate of the OPC Server for each Tags in Milliseconds
  headerString (String): The Header String Line for the required format of the CSV File
  Param: trailerPacket (String): The Trailing String Packets to complete Each Line of Data

  Returns:
  contentList (List): A List of Strings of Each Line of Contents (Header, Data, ...)
  stringfileName (stringFileName): The File Name as a String
  """
  
  contentList = [headerString]
  stringfileName = ""
  # Iterate through the Parent Key
  for fileName, globalVariables in dataFile.items(): 
    stringfileName = fileName

    for globalVariable,  variableAttributes in globalVariables.items():
      structType = variableAttributes.get("Struct")
      # if globalVariable == "SCADA_FCU_6_10_CV":

      for attributes in variableAttributes.get("Variables", []): 
        if structType != "Primitive": 
          if len(attributes) == 3: 
            attributeName, attributeType, attributeAddress = attributes
            permissions = "RO" if attributeName[0:2] == "FB" else "R/W"
            concatString = f'"{globalVariable}_{attributeName}","{attributeAddress}",{attributeType},1,{permissions}'
            concatString = f'{concatString},{scanRateSetting},{trailerPacket}\n'
            
        contentList.append(concatString)

  return contentList, stringfileName


def readCSV(fileName): 
  """
  Function: Format Data File Dictionary to String Format

  Parameters:
  fileName (dict): The File Name and Path

  Returns:
  stringArray: A 2-D String Array Containing the CSV Contents
  """

  stringArray = []
  with open(fileName) as file: 
    csv_reader = csv.reader(file)
    for row in csv_reader: 
      stringArray.append(row)
  return stringArray
       

def getStructType(dataFiles): 
  """
  Function: Get the Structure Type from the List

  Parameters: 
  dataFiles(List): The List containibng the XML File Information

  Returns: 
  structTypeList(List): Returns a List of all the Structure Types that exist in the XML File
  """
  
  structTypeList = []
  for dataFile in dataFiles:
      # Check if the current element is a dictionary
      if isinstance(dataFile, dict):
          for locationGroup, globalVariables in dataFile.items():
              for scadaVariable, metadata in globalVariables.items():
                  structType = metadata.get('Struct')
                  structTypeList.append(structType)
                  variables = metadata.get('Variables', [])
  return structTypeList


def filterVariables(enable, dataFiles, filterFiles, filterDirectory):

  filterDataFiles = []

  if (enable): 
    for filterFile in filterFiles: 
      if filterFile != 'Primitive': 

        try: 
          filterFilePath = filterDirectory + "\\" + str(filterFile) + ".csv"
          # print(filterFilePath)
          popValues = []
          tempArray = readCSV(filterFilePath)

          for i in range(2, len(tempArray)): 
            if tempArray[i][0].lower() != "yes": 
              popValues.append(tempArray[i][1])

          # Filter Child Variables based on the Filter CSV Files
          for dataFile in dataFiles:
              if isinstance(dataFile, dict):
                  for locationGroup, globalVariables in dataFile.items():
                      for scadaVariable, metadata in globalVariables.items():
                          # Filter the 'Variables' array
                          metadata['Variables'] = [
                              var for var in metadata.get('Variables', []) 
                              if var[0] not in popValues ]
          
          filterDataFiles = dataFiles

        except Exception as e: 
          print("Failed to Filter Data for " + str(filterFilePath) + " | Exception" + e)
  
  return filterDataFiles