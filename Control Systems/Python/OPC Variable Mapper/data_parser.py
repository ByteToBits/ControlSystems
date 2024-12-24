import xml.etree.ElementTree as elementTree
import pprint

# Function: Print the Dictionary in a Formatted Manner for Debugging Purposes
def printFormater(content, debugFlag): 
   if debugFlag: pprint.pprint(content)


# Function: Fetch Data Structure
# Get Each Data Structure of the XML File Paths and Parse Data
# Generate a Key Value Pair {'Struct_Name': ["Variable: FB, Type: BOOL"]}
def fetchDataStructure(xmlFilePath):  
    # Initialize an empty dictionary for storing structure & name information
    variableTypes = {}
    rawDataTree = elementTree.parse(xmlFilePath)
    rawDataRoot = rawDataTree.getroot()
    # Define the namespace (required for parsing XML with namespaces)
    namespace = {'': 'http://www.plcopen.org/xml/tc6_0201'}
    # Find all dataType elements within the XML
    data_types = rawDataRoot.findall('.//types/dataTypes/dataType', namespace)

    # Iterate over each dataType
    for data_type in data_types:
        # Get the Data Structure Name : SCADA_Motor_VSD
        structType = data_type.attrib.get('name')
        # Iterate through all the Variables & Add to the list
        for variable in data_type.findall('.//variable', namespace):
            variableName = variable.attrib.get('name')       
            variableType = getPrimitiveType(variable.find('.//type', namespace), namespace)
            variableTypes[variableName] = variableType
    
    return structType, variableTypes


# Function: Formats the Addresses with Bit index
# Format Numeric Values to two digits and Format Hex Chars to Decimal
def formatAddress(address):
    if '.' in address:
        base, bit = address.split('.')
        if bit.isdigit():
            # If the bit is a digit, format it to two digits
            return f"{base}.{int(bit):02d}"
        else:
            # If the bit is a letter (hexadecimal), convert it to its numeric equivalent
            return f"{base}.{int(bit, 16):02d}"
    return address


# Function: Get the Primitive Data Type
# Changes the PLC Primitive Data Type to the OPC's Primitive Data Type
def getPrimitiveType(type_element, namespace):
    if type_element is not None:
        if type_element.find('.//BOOL', namespace) is not None:
            return "Boolean"
        elif type_element.find('.//DWORD', namespace) is not None:
            return "DWord"
        elif type_element.find('.//REAL', namespace) is not None:
            return "Float"
        elif type_element.find('.//INT', namespace) is not None:
            return "Short"
        elif type_element.find('.//WORD', namespace) is not None:
            return "Word"
        else:
            return "Unknown"
    return "Unknown"


# Function: Fetch Raw Data
# Get Raw Data from XML File Paths and Parse Data into a Key-Value Pair
def fetchRawData(xmlFilePath):
    # Dictionary to hold all global variables
    dataFile = {}
    scadaVariable = {}  
    rawDataTree = elementTree.parse(xmlFilePath)
    root = rawDataTree.getroot()
    namespace = {'': 'http://www.plcopen.org/xml/tc6_0201'}

    # Find all globalVars elements within the XML
    globalVars = root.findall('.//instances/configurations/configuration/globalVars', namespace)

    for globalVar in globalVars:
        globalVarName = globalVar.get('name')  # Get the name attribute of globalVars

        # Iterate through variable elements
        for variable in globalVar.findall('.//variable', namespace):
            structName = variable.get('name')  # Get the variable name

            # Check if it is a structured or primitive type
            typeElement = variable.find('.//type', namespace)
            structTypeElement = typeElement.find('.//derived', namespace) if typeElement is not None else None

            if structTypeElement is not None:
                # Structured variable
                structType = structTypeElement.get('name')
                variableData = {
                    "Struct": structType,
                    "Variables": []
                }
                # Find all member elements under variableStructDeviceAssignment
                variables = variable.findall(".//addData/data/variableStructDeviceAssignment/member", namespace)
                for variable in variables:
                    variableName = variable.get('name')
                    variableAddress = formatAddress(variable.get('address'))

                    # Add variable details as a list
                    variableData["Variables"].append([variableName, variableAddress])

            else:
                # Primitive variable
                variableType = getPrimitiveType(typeElement, namespace)
                variableAddress = formatAddress(variable.get('address'))
                variableData = {
                    "Struct": "Primitive", 
                    "Type": variableType,
                    "Address": variableAddress
                }

            # Add the variable to the scadaVariable dictionary
            scadaVariable[structName] = variableData

        # Add the globalVar to the dataFile dictionary
        dataFile[globalVarName] = scadaVariable

    return dataFile

# Function: Reports and optionally prunes data with "Unknown" primitive types or are Null
# Param: dataFile (dict) Original dataFile containing structured variables and variables
# Param: pruneData (bool) True = Filters and Removes "Unknown" Types | False = Returns Original Data
# Param: debugFlag (bool): True = Prints Out Debug Information
# Returns: (dict) A filtered or unmodified dictionary based on pruneData flag
def reportUnknownData(dataFile, pruneData, debugFlag):
    unknown_count = 0  # Counter for unknown and warning entries
    filtered_data = {}  # Dictionary to hold filtered data if pruneData is enabled

    if debugFlag:
        print("Unknown Primitive Data Types:")

    for globalVar, variables in dataFile.items():
        filtered_variables = {}  # Dictionary to hold filtered variables within a globalVar

        for variableName, variableData in variables.items():
            structType = variableData.get("Struct")
            keep_variable = True  # Default to keeping the variable unless pruning removes it
# 
            # Check if it is a structured variable
            if structType != "Primitive":
                updated_variables = []  # List to hold valid variables
                for variable in variableData.get("Variables", []):
                    if len(variable) == 3:  # Ensure variable has all required fields
                        variableName, variableType, variableAddress = variable
                        if variableType == "Unknown":  # Handle unknown types
                            unknown_count += 1
                            if debugFlag:
                                print(f"Struct: {structType}, Name: {variableName}, Address: {variableAddress}")
                            if pruneData:
                                keep_variable = False  # Mark variable for removal if pruning
                        else:
                            updated_variables.append(variable)  # Keep valid variables
                    else:  # Handle warnings for malformed variables
                        unknown_count += 1  # Count warnings in the unknown total
                        if debugFlag:
                            print(f"Warning: Variable in {structType} has an unexpected format: {variable}")
                        if pruneData:
                            keep_variable = False  # Mark variable for removal if pruning
                if pruneData and keep_variable:
                    variableData["Variables"] = updated_variables  # Keep only valid variables
            else:  # Handle primitive variables
                if variableData.get("Type") == "Unknown":  # Check if primitive type is unknown
                    unknown_count += 1
                    if debugFlag:
                        print(f"Struct: Primitive, Name: {variableName}, Address: {variableData.get('Address')}")
                    if pruneData:
                        keep_variable = False  # Mark variable for removal if pruning

            if keep_variable:  # Add variable to filtered data if it should be kept
                filtered_variables[variableName] = variableData

        if pruneData and filtered_variables:  # Add globalVar to filtered data if it has valid variables
            filtered_data[globalVar] = filtered_variables

    print(f"Total unknown primitive data types and warnings: {unknown_count}")

    # Return filtered data if pruning is enabled, otherwise return the original dataFile
    return filtered_data if pruneData else dataFile


# Function: Maps Each Variable Name to its Corresponding Primitive Data Type and Appends to it to the Dictionary
# Param: dataFile (dict) Original dataFile containing structured variables and variables
# Param: dataStructure (dict) The dictionary containing the Data Structure Information
# Returns: (dict) A Dictionary of dataFile Contents with newly appended Primitive Type
def mapVariableTypes(dataFile, dataStructure): 

    for globalVar, variables in dataFile.items():
        for variableName, variableData in variables.items():
            structType = variableData.get("Struct")
            if structType and structType != "Primitive":
                # Find the corresponding derived data type in dataStructure
                matching_struct = next((d for d in dataStructure["Derived Data Types"] if d["Struct"] == structType), None)
                if matching_struct:
                    # Update Variables with matched primitive types
                    updated_variables = []
                    for variable in variableData.get("Variables", []):
                        variableName, variableAddress = variable
                        # Get the primitive type from the derived data type
                        variableType = matching_struct["Variables"].get(variableName, "Unknown")
                        updated_variables.append([variableName, variableType, variableAddress])
                    # Replace Variables in dataFile with enriched data
                    variableData["Variables"] = updated_variables

    return dataFile