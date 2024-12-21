import xml.etree.ElementTree as elementTree
import pprint

# Function: Print the Dictionary in a Formatted Manner for Debugging Purposes
def printDictionary(content, debugFlag): 
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
# Format Numeric Values to two digits and Prefix non-numeric bit with '0'
def formatAddress(address):
    if '.' in address:
        base, bit = address.split('.')
        if bit.isdigit():
            return f"{base}.{int(bit):02d}"  
        else:
            return f"{base}.0{bit}"  
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
            variableName = variable.get('name')  # Get the variable name

            # Check if it is a structured or primitive type
            typeElement = variable.find('.//type', namespace)
            structTypeElement = typeElement.find('.//derived', namespace) if typeElement is not None else None

            if structTypeElement is not None:
                # Structured variable
                structType = structTypeElement.get('name')
                variableData = {
                    "Struct": structType,
                    "Members": []
                }
                # Find all member elements under variableStructDeviceAssignment
                members = variable.findall(".//addData/data/variableStructDeviceAssignment/member", namespace)
                for member in members:
                    memberName = member.get('name')
                    memberAddress = formatAddress(member.get('address'))

                    # Add member details as a list
                    variableData["Members"].append([memberName, memberAddress])

            else:
                # Primitive variable
                variableType = getPrimitiveType(typeElement, namespace)
                variableAddress = formatAddress(variable.get('address'))
                variableData = {
                    "Struct": "Primitive",  # Explicitly mark as Primitive
                    "Type": variableType,
                    "Address": variableAddress
                }

            # Add the variable to the scadaVariable dictionary
            scadaVariable[variableName] = variableData

        # Add the globalVar to the dataFile dictionary
        dataFile[globalVarName] = scadaVariable

    return dataFile

# Function: Reports and optionally prunes data with "Unknown" primitive types or are Null
# Param: dataFile (dict) Original dataFile containing structured variables and members
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

            # Check if it is a structured variable
            if structType != "Primitive":
                updated_members = []  # List to hold valid members
                for member in variableData.get("Members", []):
                    if len(member) == 3:  # Ensure member has all required fields
                        memberName, memberType, memberAddress = member
                        if memberType == "Unknown":  # Handle unknown types
                            unknown_count += 1
                            if debugFlag:
                                print(f"Struct: {structType}, Member: {memberName}, Address: {memberAddress}")
                            if pruneData:
                                keep_variable = False  # Mark variable for removal if pruning
                        else:
                            updated_members.append(member)  # Keep valid members
                    else:  # Handle warnings for malformed members
                        unknown_count += 1  # Count warnings in the unknown total
                        if debugFlag:
                            print(f"Warning: Member in {structType} has an unexpected format: {member}")
                        if pruneData:
                            keep_variable = False  # Mark variable for removal if pruning
                if pruneData and keep_variable:
                    variableData["Members"] = updated_members  # Keep only valid members
            else:  # Handle primitive variables
                if variableData.get("Type") == "Unknown":  # Check if primitive type is unknown
                    unknown_count += 1
                    if debugFlag:
                        print(f"Struct: Primitive, Member: {variableName}, Address: {variableData.get('Address')}")
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
# Param: dataFile (dict) Original dataFile containing structured variables and members
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
                    # Update Members with matched primitive types
                    updated_members = []
                    for member in variableData.get("Members", []):
                        memberName, memberAddress = member
                        # Get the primitive type from the derived data type
                        memberType = matching_struct["Variables"].get(memberName, "Unknown")
                        updated_members.append([memberName, memberType, memberAddress])
                    # Replace Members in dataFile with enriched data
                    variableData["Members"] = updated_members

    return dataFile