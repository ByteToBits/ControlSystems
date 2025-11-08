
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

def list_Folder_Names(folderPath: str, namePrefix: List[str], debugFlag: bool):
    """
    Fetch All Folder Name of Each BTU Meter matching the given prefixes  and Store it in List  
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




