
# Project: Metering Data Parser
# Description: 
# Main Program that executes the Metering Data Parsing from Raw txt. file to Excel 
# (With Totalized Monthly Value for Billing)

# Aurthor: Tristan Sim
# Date: 11/6/2025
# Version: 1.01
# Changelog: 


# Input Dependencies: Execution Month & Year (Variable) - Default (System Clock subtracted to Previous Months)
import pandas as pd
import numpy as np
import openpyxl
import time

# Import Custom Library
import fetch_data
import parse_data
import analyze_data
import export_data

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

# Track Python Runtime
start_time = time.time()



# Step 1: Fetch all the File and Folder Information -------------------------------------------------------------------------------------- Step 1
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



# Step 2: Load Data from Text File to a Raw Data into a Dataframe ------------------------------------------------------------------------------ Step 2
print("\nStep 2: Load Data from Text File to a Raw Data into a Dataframe ")

# Initialize the Data Frame with Timestamps & Default Values for Missing Data(Filter Data)
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



# Step 3: Analyze and Process the Data into Required Output ------------------------------------------------------------------------------------- Step 3

print("\nStep 3: Analyze and Process the Data into Required Output...")

# Process all blocks and meters
for block in btuBlockList:
    
    # Find all meters in this block
    meters_in_block = [meter for meter in btuNameList if meter.split('_')[2] == block]
    
    # Analyze block-level statistics
    block_rt_stats = analyze_data.analyze_Block_RT_Data(blockDataFrames[block], btuNameList, block, includeFaultyData = True)
    block_rth_stats = analyze_data.analyze_Block_RTH_Data(blockDataFrames[block], btuNameList, block)
    
    # Print block summary
    analyze_data.print_Block_Statistics(block, block_rt_stats, block_rth_stats)
    
    # Print individual meter statistics for this block
    for meter in meters_in_block:
        rt_stats = analyze_data.analyze_Meter_RT_Data(blockDataFrames[block], meter, includeFaultyData = True)
        rth_stats = analyze_data.analyze_Meter_RTH_Data(blockDataFrames[block], meter)
        # analyze_data.print_Meter_Statistics(meter, rt_stats, rth_stats)



# Step 4: Save a Data into an Excel File (Named by Month) - Alternative Exports are .txt file or csv
print("\nStep 4: Save a Data into an Excel File (Named by Month)...")

# Export to text file
export_data.write_Analysis_Report(blockDataFrames, btuBlockList, btuNameList, pathOutputFolder, targetMonth, targetYear, analyze_data)

# Export DataFrames to Excel
export_data.write_DataFrames_to_Excel(blockDataFrames, pathOutputFolder, targetMonth, targetYear)

# Record the Python Script Runtime
end_time = time.time()
runtime = end_time - start_time

# Export diagnostic log
export_data.write_Diagnostic_Log(diagnoseStatsRegisters, pathOutputFolder, targetMonth, targetYear, runtime)

print("\nStep 4: Completed...\n")

print(f"\nTotal Runtime: {runtime:.2f} seconds ({runtime/60:.2f} minutes)\n")

# Post-Task
# Compiled into Execute / Use Raw Py Script (Requires Python Runtime on Host)
# Run based on Windows Task Scheduler
