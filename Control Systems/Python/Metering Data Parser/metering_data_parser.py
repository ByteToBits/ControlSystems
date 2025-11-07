
# Project: Metering Data Parser
# Description: 
# Main Program that executes the Metering Data Parsing from Raw txt. file to Excel 
# (With Totalized Monthly Value for Billing)

# Aurthor: Tristan Sim
# Date: 11/6/2025
# Version: 1.01
# Changelog: 

# Fetch Data From File (Meters Serve Individual Blocks)

# File Structure - Folder: J_B_82_10_27
#                      File: X01_01_20250801_70_01_ACCBTUReadingS11MIN.txt - RTH Data
#                      File: X01_01_20250801_70_01_BTUREADINGS11MIN.txt - RT Data
#                      File: ... Next Month

# J_B_82_10_27
# Block 82: B_82
# Unique BTU ID based on Block: 10_27

# X01_01_20250801_70_01_ACCBTUReadingS11MIN.txt - RTH Data
# Constants: X01_01_  70_01_ACCBTUReadingS11MIN.txt
# Dynamic Variable: 20250801   Year (2025) Month (08) Day (01)

# Raw Data Format (Old)
"""
#start (Question: Newer Data Set Does not Contain this - Will it be omitted from future data?)
15.08.2025 10:08:55 1.2908564
15.08.2025 10:09:00 2.5826838
.... 
31.08.2025 00:24:00 4.3564544
31.08.2025 00:25:00 4.2770133
#stop (Question: Newer Data Set Does not Contain this - Will it be omitted from future data?)
"""

# Raw Data Format (New - 44640 Datapoints)
"""
01.10.2025 00:00:00 7763.3203  - First Data 
01.10.2025 00:01:00 7763.422
01.10.2025 00:02:00 7763.5176
...
31.10.2025 23:57:00 14842.312s
31.10.2025 23:58:00 14842.435
31.10.2025 23:59:00 14842.554  - Last Data
"""

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

# Initial: Initialize Data
pathDataFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\data'
DEBUG_FLAG = True
DELIMITER = ';'

# Dynamically Populated - Can be Statically Assigned herein these Array
btuNameList = []        # BTU Name List
btuFileList_RT = []     # RT File Name List
btuFileList_RTH = []    # RTH File Name List

btuNamePrefix = ["J_B_"]
dataFilePrefix = ["X01_01_"]
dataFilePostfix = ["ACCBTUReadingS11MIN.txt", "BTUREADINGS11MIN.txt"]

# Fetch All Folder Name of Each BTU Meter and Store it in List
if os.path.exists(pathDataFolder): 
    # Get all the subdirectories in the Metering Data Folder
    for folder in os.listdir(pathDataFolder): 
        if os.path.isdir(os.path.join(pathDataFolder, folder)): 
            if folder.startswith(tuple(btuNamePrefix)): 
               btuNameList.append(folder)   
    if DEBUG_FLAG == True: 
        print(f'Found {len(btuNameList)} BTU Meters:')
        for btuName in btuNameList: 
            print(f"- {btuName}")
else: 
    print(f"Error:No Data folder found in {pathDataFolder}")

# Fetch All File Name (With Folder Name Information) and Store it in List
# for btuName in btuNameList: 
#     if os.path.exists(os.path.join(pathDataFolder, btuName)): 
        



# # Fetch All File Name (With Folder Name Information) and Store it in List
# for btuName in btuNameList: 
#     folderPath = os.path.join(pathDataFolder, btuName)
    
#     if os.path.exists(folderPath): 
#         # Get all files in this BTU folder
#         for file in os.listdir(folderPath):
#             filePath = os.path.join(folderPath, file)
            
#             # Check if it's a file (not a subdirectory)
#             if os.path.isfile(filePath):
#                 # Check if file matches the prefix and postfix criteria
#                 if file.startswith(tuple(dataFilePrefix)) and file.endswith(tuple(dataFilePostfix)):
#                     # Create the concatenated string: btu_name;filename.txt
#                     concatenatedName = f"{btuName}{DELIMITER}{file}"
                    
#                     # Categorize based on file ending
#                     if file.endswith("BTUREADINGS11MIN.txt"):  # RT ends with BTU
#                         btuFileList_RT.append(concatenatedName)
#                     elif file.endswith("ACCBTUReadingS11MIN.txt"):  # RTH ends with ACCBTU
#                         btuFileList_RTH.append(concatenatedName)



# Step 1: Load Data from Text File (Try & Catch to Handle Abnormal Data)

# Step 2: Parse the Text Data (Date & Process Value) to a Data Frame 

# Step 3: Data Filter (Missing Data - Or Abnormal Data)

# Step 4: Process the Data into Required Output

# Step 5: Save a Data into an Excel File (Named by Month) - Alternative Exports are .txt file or csv


# Post-Task
# Compiled into Execute / Use Raw Py Script (Requires Python Runtime on Host)
# Run based on Windows Task Scheduler