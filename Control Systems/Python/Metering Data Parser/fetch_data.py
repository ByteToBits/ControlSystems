
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
               

