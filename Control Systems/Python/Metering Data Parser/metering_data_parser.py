
# Project: Metering Data Parser
# Description: 
# Main Program that executes the Metering Data Parsing from Raw txt. file to Excel 
# (With Totalized Monthly Value for Billing)

# Aurthor: Tristan Sim
# Date: 11/6/2025
# Version: 1.01
# Changelog: 

# Fetch Data From File (Meters Serve Individual Blocks)

# Monthly BTU Data per Block
# Purpoaw (Billing)
# B22 BTU 1 RTH = Last Data - First Data = 14842.554 - 7763.3203 = 7,079.2337 RTH
# B22 BTU 2 RTH = Last Data - First Data = 14842.554 - 7763.3203 = 7,079.2337 RTH
# B22 BTU 3 RTH = Last Data - First Data = 14842.554 - 7763.3203 = 7,079.2337 RTH
# BTU B22 Total = B22 BTU 1 RTH + B22 BTU 2 RTH + B22 BTU 3 RTH = 7,079.2337 + 7,079.2337 + 7,079.2337 = 21,237.7011 RTH

# Totalize RT
# Average RT
# Purpose (Knowledge?)


# Input Dependencies: Execution Month & Year (Variable) - Default (System Clock subtracted to Previous Months)
import pandas as pd
import numpy as np
import time
# import openpyxl
import os

# Import Custom Library
import fetch_data
import parse_data

# Initial: Initialize Data
targetMonth = '10'
targetYear = '2025'
pathDataFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\data' # Absolute Path to Working Directory
pathOutputFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\data\Metering Summary Report'

MONTHS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
DEBUG_FLAG = True
DELIMITER = ';'
DATETIME_START_INDEX = 7 # Datetime starts frpm the 7th Character in the File Name

# Dynamically Populated - Can also be Statically Assigned herein these Array
btuNameList = []          # BTU Name List         J_B_82_10_27
btuBlockList = []         # BTU Blocks            J_B_82 = Block 82
btuFileList_RT = []       # RT File Name List     J_B_82_10_27/X01_01_20250801_70_01_BTUREADINGS11MIN.txt
btuFileList_RTH = []      # RTH File Name List    J_B_82_10_27/X01_01_20250801_70_01_ACCBTUReadingS11MIN.txt

targetTimestamp = targetYear + targetMonth
btuNamePrefix = ["J_B_"]
dataFilePrefix = ["X01_01_"]
dataFilePostfix = ["BTUREADINGS11MIN.txt", "ACCBTUReadingS11MIN.txt"]

# For Step 2: Converting Raw Data into Data Frame
diagnoseStatsRegisters = []
blockDataFrames  = {}  # Dictionary (Key-Value Pair: Key - Block 22: Data Frame)

# Step 1: Fetch all the File and Folder Information 
print("\nStep 1: Fetch all the File and Folder Information")

# Fetch All Folder Name of Each BTU Meter and Store it in List
btuNameList = fetch_data.list_Folder_Names(folderPath = pathDataFolder, namePrefix = btuNamePrefix, debugFlag = DEBUG_FLAG)

# List the Blocks that the Meters exist in (Use Set - Unqiue)
# Extract block names from meter names ("J_B_82_10_27" to "J_B_82")
btuBlockList = fetch_data.list_Meter_Blocks(nameList = btuNameList)

# Specify the Search Criteria for Prefix that matches "X01_01_202508"
prefixSearchCriteria = dataFilePrefix[0] + targetTimestamp 

# Fetch All File Names (With Parent Folder Name Information) and Store it in List:
btuFileList_RT = fetch_data.list_File_Names(parentFolderPath = pathDataFolder,
                                            childFolderNames = btuNameList,
                                            prefix = prefixSearchCriteria,
                                            postfix = (dataFilePostfix[0]),
                                            delimiter = DELIMITER,
                                            debugFlag = DEBUG_FLAG)

btuFileList_RTH = fetch_data.list_File_Names(parentFolderPath = pathDataFolder,
                                            childFolderNames = btuNameList,
                                            prefix = prefixSearchCriteria,
                                            postfix = (dataFilePostfix[1]),
                                            delimiter = DELIMITER,
                                            debugFlag = DEBUG_FLAG)
               
# Print the Files Retrieved based on Search Criteria     
if DEBUG_FLAG == True: 
   print(f"\nFound {len(btuBlockList)} Unique Blocks:")
   for block in btuBlockList: print(f"- {block}")
   print("\nFiles Retrieve for RT Data (Month: " + targetMonth + " and Year: " + targetYear + "):")
   for file in btuFileList_RT: print("- " + file)
   print("\nFiles Retrieve for RTH Data (Month: " + targetMonth + " and Year: " + targetYear + "):")
   for file in btuFileList_RTH: print("- " + file)
   
print("\nStep 1: Completed...\n")



# Step 2: Load Data from Text File to a Raw Data into a Dataframe 
print("\nStep 2: Load Data from Text File to a Raw Data into a Dataframe ")

# Initialize the Data Frame with Timestamps & Default Values
for block in btuBlockList: 
   blockDataFrames[block] = parse_data.initialize_Block_DataFrame(month=targetMonth, year=targetYear, blockNumber=block, meterList=btuNameList) 

# Populate RT data
parse_data.populate_Meter_DataFrame(btuFileList_RT, blockDataFrames, diagnoseStatsRegisters, pathDataFolder, DELIMITER, 'RT')

# Populate RTH data
parse_data.populate_Meter_DataFrame(btuFileList_RTH, blockDataFrames, diagnoseStatsRegisters, pathDataFolder, DELIMITER, 'RTH')

# Print results
if DEBUG_FLAG:
    for block, df in blockDataFrames.items():
        print(f"\nBlock {block}:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(df.head())

print("\nStep 2: Completed...\n")


# Step 3: Process the Data into Required Output





# Step 5: Save a Data into an Excel File (Named by Month) - Alternative Exports are .txt file or csv


# Post-Task
# Compiled into Execute / Use Raw Py Script (Requires Python Runtime on Host)
# Run based on Windows Task Scheduler
