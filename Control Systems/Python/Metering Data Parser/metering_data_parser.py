
# Project: Metering Data Parser
# Description: 
# Main Program that executes the Metering Data Parsing from Raw txt. file to Excel 
# (With Totalized Monthly Value for Billing)

# Aurthor: Tristan Sim
# Date: 11/6/2025
# Version: 1.01
# Changelog: 
# - 24/11/2025 - Introduce a Metering Filter to seperate the summation of different Meter Readings
#              - Step 2.5 - Calcuate the per minute sum of the RT for each Meter Category
#              - Format the Excel for Easy Readability


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
targetMonth = '04'
targetYear = '2025'
pathDataFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\data\PDD_BTUmeter' # Absolute Path to Working Directory
pathOutputFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\data\Metering Summary Report'
pathMeterFilterFile = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\filter\FilterList_CWSA.xlsx' # List of Meters to Filter

MONTHS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
DEBUG_FLAG = True
DELIMITER = ';'
DATETIME_START_INDEX = 7 # Datetime starts from the 7th Character in the File Name

# Dynamically Populated - Can also be Statically Assigned herein these Array
btuNameList = []          # BTU Name List         J_B_82_10_27
btuBlockList = []         # BTU Blocks            J_B_82 = Block 82
btuFileList_RT = []       # RT File Name List     J_B_82_10_27/X01_01_20250801_70_01_BTUREADINGS11MIN.txt
btuFileList_RTH = []      # RTH File Name List    J_B_82_10_27/X01_01_20250801_70_01_ACCBTUReadingS11MIN.txt

targetTimestamp = targetYear + targetMonth
btuNamePrefix = ["J_B_"]
dataFilePrefix = ["X01_01_"]
dataFilePostfix = ["BTUREADINGS11MIN.txt", "ACCBTUReadingS11MIN.txt"]
meterCategory = ["Total RT Sum", "CWSA RT", "Retail RT"]

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


# Step 2.5: Calculate the Sum for Each Meter based on the Type of Meter ------------------------------------------------------------------------- Step 2.5

# Insert new column after time based on the length of the list 'meterCategory' and name it after each item

print("\nStep 2.5: Add Aggregated Columns by Meter Category...")

# List all the CWSA Meter Names
meterClassification = pd.read_excel(pathMeterFilterFile)
meterList_CWSA_Filter = meterClassification['Device Name'].dropna().tolist() 

for block in btuBlockList:
    
    # List and Store all the Meters in the Current Process Block 
    metersInBlock = [] # Initialize with every new Block Processed
    for meter in btuNameList:   
        if meter.split('_')[2] == block: 
            metersInBlock.append(meter)

    # Sum all the RT of Values for the Current Process Block
    dataColumns_Total_RT = [] # Intialize a List to Store all the RT Names
    for meter in metersInBlock:
        dataColumns_Total_RT.append(f'{meter}_RT')

    # Segregate & Classify 
    dataColumns_CWSA_RT = []
    dataColumns_Retail_RT = []
    for meter in metersInBlock: 
        if meter in meterList_CWSA_Filter:
            dataColumns_CWSA_RT.append(f'{meter}_RT')
        else:
            dataColumns_Retail_RT.append(f'{meter}_RT')

    # Calculate Sum of RT for each Category
    sum_Total_RT = blockDataFrames[block][dataColumns_Total_RT].sum(axis=1)
    sum_CWSA_RT = blockDataFrames[block][dataColumns_CWSA_RT].sum(axis=1) if dataColumns_CWSA_RT else 0.0
    sum_Retail_RT = blockDataFrames[block][dataColumns_Retail_RT].sum(axis=1) if dataColumns_Retail_RT else 0.0

    # Insert Columns after the Time column (Index 3)
    blockDataFrames[block].insert(3, f'Block {block} Total RT Sum', round(sum_Total_RT, 3))
    blockDataFrames[block].insert(4, f'Block {block} CWSA RT Sum', round(sum_CWSA_RT,3))
    blockDataFrames[block].insert(5, f'Block {block} Retail RT Sum', round(sum_Retail_RT,3))
    blockDataFrames[block].insert(6, f'Block {block} Total Meters', len(metersInBlock))
    blockDataFrames[block].insert(7, f'Block {block} CWSA Meters', len(dataColumns_CWSA_RT))

print("Step 2.5: Completed...\n")



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
export_data.write_DataFrames_to_Excel(blockDataFrames, btuBlockList, pathOutputFolder, targetMonth, targetYear)

# Record the Python Script Runtime
end_time = time.time()
runtime = end_time - start_time

# Export diagnostic log
export_data.write_Diagnostic_Log(diagnoseStatsRegisters, pathOutputFolder, targetMonth, targetYear, runtime)

print("\nStep 4: Completed...\n")
print(f"\nTotal Runtime: {runtime:.2f} seconds ({runtime/60:.2f} minutes)\n")