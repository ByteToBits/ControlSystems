
import csv
import os

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



# def filterVariables(enable, dataFiles, filterFiles, filterDirectory):
#     if not enable:
#         return dataFiles  # If filtering is disabled, return the data as-is
    
#     filterDataFiles = []
    
#     for filterFile in filterFiles:
#         if filterFile == 'Primitive':
#             continue
        
#         try:
#             filterFilePath = os.path.join(filterDirectory, f"{filterFile}.csv")
#             # filterFilePath = f"{filterDirectory}/{filterFile}.csv"
#             tempArray = readCSV(filterFilePath)
            
#             keepValues = set()
#             popValues = set()
            
#             # Read the CSV and categorize variables into keep and pop sets
#             for row in tempArray[2:]:
#                 if len(row) < 2:
#                     continue  # Skip invalid rows
#                 label = row[1].strip()
#                 if row[0].strip().lower() == "yes":
#                     keepValues.add(label)
#                 elif row[0].strip() == "":
#                     popValues.add(label)
            
#             # Process each data file and apply filtering
#             for dataFile in dataFiles:
#                 if isinstance(dataFile, dict):
#                     for locationGroup, globalVariables in dataFile.items():
#                         for scadaVariable, metadata in globalVariables.items():
#                             variables = metadata.get('Variables', [])
#                             filteredVariables = []
                            
#                             for var in variables:
#                                 varName = var[0]
#                                 # If "Process Value" Tag does not map, Hardcode it to always keep FB_Process_Value
#                                 # if varName == "FB_Process_Value" or varName == "Ctrl_Mode" or varName in keepValues:
#                                 if varName == "FB_Process_Value" or varName == "Ctrl_Mode" or varName in keepValues:
#                                     filteredVariables.append(var)
#                                 # Remove only those explicitly marked for removal
#                                 elif varName not in popValues:
#                                     filteredVariables.append(var)
                            
#                             metadata['Variables'] = filteredVariables
            
#             filterDataFiles = dataFiles  # Update the filtered data
        
#         except Exception as e:
#             print(f"Failed to filter data for {filterFilePath}: {e}")
    
#     return filterDataFiles

def filterVariables(enable, dataFiles, filterFiles, filterDirectory, debug=False):
    """
    Filter variables based on filter CSV files.
    
    Parameters:
    enable (bool): Whether filtering is enabled
    dataFiles (list): The data files to filter
    filterFiles (list): The structure types to filter
    filterDirectory (str): Directory containing filter CSV files
    debug (bool): Whether to print debug information (defaults to False)
    
    Returns:
    list: The filtered data files
    """
    if not enable:
        return dataFiles  # If filtering is disabled, return the data as-is
    
    if debug:
        print(f"Filter directory: {filterDirectory}")
        print(f"Structure types to filter: {filterFiles}")
    
    # Process each filter file (structure type)
    for filterFile in filterFiles:
        if filterFile == 'Primitive':
            continue
        
        try:
            # Construct path to filter file using os.path.join for cross-platform compatibility
            filterFilePath = os.path.join(filterDirectory, f"{filterFile}.csv")
            if debug:
                print(f"Processing filter file: {filterFilePath}")
            
            # Check if filter file exists
            if not os.path.exists(filterFilePath):
                if debug:
                    print(f"WARNING: Filter file not found: {filterFilePath} - skipping")
                continue
                
            # Read filter CSV
            tempArray = readCSV(filterFilePath)
            if debug:
                print(f"Read filter file with {len(tempArray)} rows")
            
            keepValues = set()
            popValues = set()
            
            # Process the filter file to determine which variables to keep/remove
            for row in tempArray[2:]:  # Skip header rows
                if len(row) < 2:
                    continue
                
                label = row[1].strip()
                action = row[0].strip().lower() if len(row[0].strip()) > 0 else ""
                
                if action == "yes":
                    keepValues.add(label)
                    if debug:
                        print(f"Marked to keep: {label}")
                else:
                    # Only add to popValues if it's not explicitly marked to keep
                    popValues.add(label)
                    if debug:
                        print(f"Not marked to keep: {label}")
            
            # Process each data file
            for dataFile in dataFiles:
                if isinstance(dataFile, dict):
                    for locationGroup, globalVariables in dataFile.items():
                        for scadaVariable, metadata in globalVariables.items():
                            # Check if current structure matches the filter file
                            currentStructType = metadata.get('Struct')
                            if currentStructType == filterFile:
                                if debug:
                                    print(f"Applying filter to {scadaVariable} (Structure: {filterFile})")
                                
                                variables = metadata.get('Variables', [])
                                if not variables:
                                    if debug:
                                        print(f"  No variables found for {scadaVariable}")
                                    continue
                                    
                                if debug:
                                    print(f"  Before filtering: {len(variables)} variables")
                                
                                # Create a new list for filtered variables
                                filteredVariables = []
                                
                                # Process each variable
                                for var in variables:
                                    if len(var) < 1:
                                        continue
                                        
                                    varName = var[0]
                                    
                                    # KEEP LOGIC: Modified to be more inclusive
                                    # 1. Always keep critical control variables
                                    # 2. Keep anything explicitly marked to keep in the filter
                                    # 3. Keep anything not explicitly marked for removal
                                    if (varName == "FB_Process_Value" or 
                                        varName == "Ctrl_Mode" or 
                                        varName == "FB_SlaveHealth" or 
                                        varName == "FB_Temperature" or
                                        varName in keepValues or 
                                        varName not in popValues):
                                        filteredVariables.append(var)
                                        if debug:
                                            print(f"    Kept: {varName}")
                                    else:
                                        if debug:
                                            print(f"    Removed: {varName}")
                                
                                # Update the filtered variables
                                metadata['Variables'] = filteredVariables
                                if debug:
                                    print(f"  After filtering: {len(filteredVariables)} variables")
        
        except Exception as e:
            # Always print errors, even if debug is off
            print(f"Error processing filter file {filterFile}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return dataFiles