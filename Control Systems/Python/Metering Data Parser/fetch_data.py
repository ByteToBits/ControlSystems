
# Project: Metering Data Parser
# File Type: Function File

# Description: Fetch Data
# Contains Functions for Retrieving Raw Data Files and Parsing them into Panda Frames

# Aurthor: Tristan Sim
# Date: 8/11/2025
# Version: 1.01
# Changelog: 

# Input Dependencies: Execution Month & Year (Variable) - Default (System Clock subtracted to Previous Months)
import pandas as pd
import numpy as np
import os
from typing import List, Tuple

# Function: List Folder Names
# Fetch All Folder Name of Each BTU Meter matching the given prefixes  and Store it in List 
def list_Folder_Names(folderPath: str, namePrefix: List[str], debugFlag: bool) -> List[str]:
    """
    Fetch All Folder Name of Each BTU Meter matching the given prefixes  and Store it in List.
    Args:
        folderPath: Path to the Parent data folder
        namePrefix: List of valid File Name Prefixes      
    Returns:
        List of out all the Folder Names
    """
    folderNames = []
    # Fetch All Folder Name of Each BTU Meter and Store it in List
    if os.path.exists(folderPath): 
        # Get all the subdirectories in the Metering Data Folder
        for folder in os.listdir(folderPath): 
            if os.path.isdir(os.path.join(folderPath, folder)): 
                if folder.startswith(tuple(namePrefix)): 
                   folderNames.append(folder)   
        if debugFlag == True: 
            print(f'Found {len(folderNames)} BTU Meters:')
            for name in folderNames: 
                print(f"- {name}")
    else: 
        print(f"Error:No Data folder found in {folderPath}")

    return sorted(folderNames)  


# Function: List File Names
# Fetch All File Names (With Parent Folder Name Information) and Store it in List:
def list_File_Names(parentFolderPath: str, childFolderNames: List[str], prefix: str, postfix: str, delimiter: str, debugFlag: bool) -> List[str]:
    """
    Fetch all file names matching the given prefix and postfix from child folders.
    Args:
        parentFolderPath: Path to the parent data folder
        childFolderNames: List of child folder names to search
        prefix: File name prefix to match
        postfix: File name postfix to match
        delimiter: Delimiter to separate folder name and file name
        debugFlag: Enable debug output     
    Returns:
        List of out all the File Names Sorted based on Child Folder Name
    """
    fileNames = []

    # Fetch All File Names (With Parent Folder Name Information) and Store it in List:
    for folderName in childFolderNames: 
        # Concatenate the Complete Folder Path for the BTU Meters
        concatBTUFolderPath = os.path.join(parentFolderPath, folderName)

        # Iterate through to retrieve the File Names and store them in a List for easy referencing
        if os.path.exists(concatBTUFolderPath): 

            for file in os.listdir(concatBTUFolderPath): 
                # Check if the Date of the File Meets the Target Data and Classify based on File Post Fix Text
                if file.startswith(prefix) and file.endswith(postfix):
                    fileNames.append(folderName + delimiter + file)

    return sorted(fileNames)
               

def read_Raw_Text_Data(filePath: str, encoding: str = 'utf-8', healthCheck: bool = True, debugFlag: bool = False) -> tuple:
    """
    Read raw BTU meter text data and parse into list of dictionaries.
    Args:
        filePath: Full path to the text file
        encoding: File encoding (Default: 'utf-8')
        healthCheck: Whether to check for #start/#stop health markers (default: True)
        debugFlag: Whether to print debug information (default: False)
        
    Returns:
        Tuple containing:
        - rawData: List of dictionaries with keys: Timestamp, Value, Health
        - diagnosticStatistics: Dictionary with parsing statistics
    """
    rawData = []
    lineCount = 0
    sensorHealth = True # Default as healthy (assume data starts healthy unless we see #stop first)
    timestampFailure = []
    timestampRecovery = []
    corruptedDataLines = []
    pendingStartMarker = False  # Flag to capture timestamp after #start

    # Get the Meter Name and File Name for Diagnostics
    meterName = os.path.basename(os.path.dirname(filePath)) if os.path.dirname(filePath) else "Unknown"
    fileName = os.path.basename(filePath)
    
    with open(filePath, 'r', encoding=encoding) as textFile:
        
        for line in textFile:

            line = line.strip() 
            lineCount += 1
            
            # Check the Health to Meters | Bypass Flag skips the Health Check
            # '#start' indicates healthy data is starting (meter comes online)
            # '#stop' indicates healthy data is stopping (meter goes offline)
            if healthCheck: 
                if line == '#stop':

                    # Capture the last datapoint timestamp before this #stop
                    if len(rawData) > 0 and rawData[-1]['Health']:
                        timestampFailure.append(rawData[-1]['Timestamp'].strftime("%Y-%m-%d %H:%M:%S"))

                    sensorHealth = False  # Flag Datapoint as Unhealthy
                    if debugFlag: print(f"Line {lineCount}: Sensor Unhealthy (#stop)")
                    continue
                elif line == '#start':
                    sensorHealth = True   # Flag Datapoint as Healthy
                    pendingStartMarker = True  # Mark that we need to capture next timestamp
                    if debugFlag: print(f"Line {lineCount}: Sensor Healthy (#start)")
                    continue
            
            # Skip empty lines or other comments
            if not line or line.startswith('#'):
                continue
            
            # Raw Data Line: "01.10.2025 00:00:00 9006.741" - Seperated by Whitespaces (Data | Time | Process Value)
            try:
                dataSegment = line.split()  # Split the Data by by whitespaces
                
                # Extract the Timestamp of the Datapoint
                if len(dataSegment) >= 2:    
                    
                    # Extract the Timestamp and convert into datetime (ISO format)
                    dateString = dataSegment[0]                    # 01.10.2025
                    timeString = dataSegment[1]                    # 00:00:00
                    timestampString = f"{dateString} {timeString}" # 01.10.2025 00:00:00
                    timestampISO = pd.to_datetime(timestampString, format="%d.%m.%Y %H:%M:%S")
                    
                    # Process the Process Value Data
                    if len(dataSegment) == 3:
                        processValue = float(dataSegment[2])  # 9006.741
                    else:
                        processValue = 0.0  # Default value if missing - 0.0

                    # If sensor is Unhealthy (After #stop)
                    if not sensorHealth:
                        processValue = 0.0  # Default value if missing - 0.0
                    
                    # Capture recovery timestamp (first datapoint after #start)
                    if pendingStartMarker and sensorHealth:
                        timestampRecovery.append(timestampISO.strftime("%Y-%m-%d %H:%M:%S"))
                        pendingStartMarker = False
                    
                    rawData.append({
                        'Timestamp': timestampISO,
                        'Value': processValue,
                        'Health': sensorHealth  
                    })

                else:
                    if debugFlag: 
                        print(f"Skipping line {lineCount}: Corrupted Data ({line})")
                    corruptedDataLines.append(lineCount)
                    
            except Exception as e:
                if debugFlag: 
                    print(f"Skipping line {lineCount}: Corrupted Data ({line}) - Error: {e}")
                corruptedDataLines.append(lineCount)

    totalData = len(rawData)
    totalHealthyData = sum(1 for row in rawData if row['Health'])
    totalFaultyData = totalData - totalHealthyData
    faultyDataPercentage = round((totalFaultyData/totalData * 100), 2) if totalData > 0 else 0.0

    diagnosticStatistics = {
        'meter': meterName,
        'file_name': fileName,
        'total_data': totalData,
        'raw_line_count': lineCount,
        'healthy_data': totalHealthyData,
        'faulty_data': totalFaultyData,
        'faulty_data_percentage': faultyDataPercentage,
        'failure_timestamps': timestampFailure,
        'recovery_timestamps': timestampRecovery,
        'corrupted_data_lines': len(corruptedDataLines)
    }
    
    if debugFlag: 
        print(f"\nMeter: {meterName} (File: {fileName})")
        print(f"\nNumber of Datapoints: {totalData} (Raw Number of Lines: {lineCount})")
        print(f"\nTotal Healthy Datapoints: {totalHealthyData}  |  Total Unhealthy Datapoints: {totalFaultyData}")
        print(f"\nFaulty Data Percentage: {faultyDataPercentage}  |  Total Corrupted Data Lines: {corruptedDataLines}")
        print(f"\nSensor Failure Time: {timestampFailure}")
        print(f"\nSensor Recovery Time: {timestampRecovery}")
    
    return rawData, diagnosticStatistics