
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
       


