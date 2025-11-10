
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
btuFileList_RT = []       # RT File Name List     J_B_82_10_27/X01_01_20250801_70_01_BTUREADINGS11MIN.txt
btuFileList_RTH = []      # RTH File Name List    J_B_82_10_27/X01_01_20250801_70_01_ACCBTUReadingS11MIN.txt

targetTimestamp = targetYear + targetMonth
btuNamePrefix = ["J_B_"]
dataFilePrefix = ["X01_01_"]
dataFilePostfix = ["ACCBTUReadingS11MIN.txt", "BTUREADINGS11MIN.txt"]


# Step 1: Fetch all the File and Folder Information 

# Fetch All Folder Name of Each BTU Meter and Store it in List
btuNameList = fetch_data.list_Folder_Names(folderPath = pathDataFolder, namePrefix = btuNamePrefix, debugFlag = DEBUG_FLAG)

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
   print("\nFiles Retrieve for RT Data (Month: " + targetMonth + " and Year: " + targetYear + "):")
   for file in btuFileList_RT: print("- " + file)
   print("\nFiles Retrieve for RTH Data (Month: " + targetMonth + " and Year: " + targetYear + "):")
   for file in btuFileList_RTH: print("- " + file)
   


# Step 2: Load Data from Text File to a Raw Data into a Dataframe 


print("\n" + "="*80)
print("TESTING WITH SINGLE FILE")
print("="*80)

# Test with the first RT file
if len(btuFileList_RT) > 0:
    testFileInfo = btuFileList_RT[0]  # Get first file
    
    # Parse the file info: "meterName;fileName"
    parts = testFileInfo.split(DELIMITER)
    if len(parts) == 2:
        meterName = parts[0]
        fileName = parts[1]
        filePath = os.path.join(pathDataFolder, meterName, fileName)
        
        print(f"\n📁 Testing with: {meterName} - {fileName}")
        print(f"📂 Full path: {filePath}")
        
        try:
            # Call the function and unpack both returns
            rawData, diagnostics = fetch_data.read_Raw_Text_Data(
                filePath=filePath,
                encoding='utf-8',
                healthCheck=True,
                debugFlag=True  # Enable debug to see detailed output
            )
            
            print("\n" + "="*80)
            print("RESULTS")
            print("="*80)
            
            # Show diagnostics
            print("\n📊 Diagnostic Statistics:")
            for key, value in diagnostics.items():
                print(f"  {key}: {value}")
            
            # Show first few data points
            print("\n📋 First 5 Data Points:")
            for i, datapoint in enumerate(rawData[:5]):
                print(f"  {i+1}. {datapoint}")
            
            # Show last few data points
            print("\n📋 Last 5 Data Points:")
            for i, datapoint in enumerate(rawData[-5:]):
                print(f"  {i+1}. {datapoint}")
            
            # Convert to DataFrame to see structure
            df_test = pd.DataFrame(rawData)
            print("\n📊 DataFrame Info:")
            print(df_test.info())
            print("\n📊 DataFrame Head:")
            print(df_test.head(10))
            print("\n📊 DataFrame Tail:")
            print(df_test.tail(10))
            
            # Check health distribution
            print("\n🏥 Health Status Distribution:")
            print(df_test['Health'].value_counts())
            
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            import traceback
            traceback.print_exc()
else:
    print("⚠️ No RT files found to test!")





# RAW Data (Timestamp & Process Value)
# 01.10.2025 00:00:00 6.0966177
# 01.10.2025 00:01:00 5.730138

# Raw Data Format (Faulty #start (Start of Faulty Data) & #stop (End of Faulty Data))
"""
#start (Indicates BTU Meter is Offline)
15.08.2025 10:08:55 1.2908564
15.08.2025 10:09:00 2.5826838
.... 
31.08.2025 00:24:00 4.3564544
31.08.2025 00:25:00 4.2770133
#stop (Indicates BTU Meter is Offline)
"""
# Raw Data Format (Healty Data Has No - 44640 Datapoints)
"""
01.10.2025 00:00:00 7763.3203  - First Data 
01.10.2025 00:01:00 7763.422
01.10.2025 00:02:00 7763.5176
...
31.10.2025 23:57:00 14842.312
31.10.2025 23:58:00 14842.435
31.10.2025 23:59:00 14842.554  - Last Data
"""





# Timestamp will need to be converted into ISO Form
# Pandas Frame Output: Timestamp | J_B_82_10_27 Process Value | J_B_82_10_27 Health |  J_B_82_11_27 Process Value | J_B_82_11_27 Health | 


# Step 2: Parse the Text Data (Date & Process Value) to a Data Frame 

# Step 3: Data Filter (Missing Data - Or Abnormal Data)

# Step 4: Process the Data into Required Output

# Step 5: Save a Data into an Excel File (Named by Month) - Alternative Exports are .txt file or csv


# Post-Task
# Compiled into Execute / Use Raw Py Script (Requires Python Runtime on Host)
# Run based on Windows Task Scheduler
