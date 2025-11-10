import pandas as pd
from datetime import datetime
from calendar import monthrange
from typing import List, Tuple
import os
import fetch_data

def initialize_Block_DataFrame(month: str, year: str, blockNumber: str, meterList: List[str]):
    """
    Initialize a DataFrame for a specific block with timestamp and meter columns.
    Args:
        targetMonth: Month as string ('10' for October)
        targetYear: Year as string ('2025')
        blockNumber: Block number as string ('82')
        meterList: List of all meter names to filter meters in this block
    
    Returns:
        DataFrame with timestamp, date, time, and meter RT/RTH columns initialized to 0.0
    """
    
    month = int(month)
    year = int(year)
    
    # Get the first day of the target month at 00:00:00
    first_day = datetime(year, month, 1, 0, 0, 0)
    
    # Get the last day of the month
    last_day_num = monthrange(year, month)[1]
    
    # Get the last timestamp of the month (23:59:00)
    last_moment = datetime(year, month, last_day_num, 23, 59, 0)
    
    # Create timestamp range with 1-minute intervals
    timestamps = pd.date_range(start=first_day, end=last_moment, freq='1min')
    
    # Create DataFrame with timestamp columns
    df = pd.DataFrame({'timestamp': timestamps})
    df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df[['timestamp', 'date', 'time']]
    
    # Find all meters in this block
    meters_In_Block = []

    for meter in meterList: 
        parts = meter.split('_')
        if parts[2] == blockNumber: 
            meters_In_Block.append(meter)
    
    # Add RT and RTH columns for each meter
    for meter in meters_In_Block:
        df[f'{meter}_RT'] = 0.0
        df[f'{meter}_RTH'] = 0.0

    return df

def populate_Meter_DataFrame(fileList: List[str], blockDataFrames: dict, diagnoseStatsRegisters: list, 
                             dataFolderPath: str, delimiter: str, columnSuffix: str):
    """
    Populate block DataFrames with meter data from file list.
    
    Args:
        fileList: List of files with format "MeterName;FileName"
        blockDataFrames: Dictionary of block DataFrames to populate
        diagnoseStatsRegisters: List to append diagnostic statistics
        dataFolderPath: Path to data folder
        delimiter: Delimiter separating meter name and file name
        columnSuffix: Suffix for column name ('RT' or 'RTH')
    """
    
    for i, file in enumerate(fileList):
        
        parts = file.split(delimiter)
        meterName = parts[0]
        fileName = parts[1]
        columnName = f'{meterName}_{columnSuffix}'
        blockNumber = meterName.split('_')[2]
        
        # Read the raw data
        targetFilePath = os.path.join(dataFolderPath, meterName, fileName)
        rawData, diagnosticStatistics = fetch_data.read_Raw_Text_Data(targetFilePath, debugFlag=False)
        diagnoseStatsRegisters.append(diagnosticStatistics)
        
        # Convert rawData to DataFrame for bulk merge
        temp_df = pd.DataFrame(rawData)
        temp_df['timestamp'] = temp_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        temp_df['value_to_use'] = temp_df.apply(lambda row: row['Value'] if row['Health'] else 0.0, axis=1)
        
        # Merge with main DataFrame
        blockDataFrames[blockNumber] = blockDataFrames[blockNumber].merge(
            temp_df[['timestamp', 'value_to_use']], 
            on='timestamp', 
            how='left'
        )
        
        # Fill the column and cleanup
        blockDataFrames[blockNumber][columnName] = blockDataFrames[blockNumber]['value_to_use'].fillna(0.0)
        blockDataFrames[blockNumber].drop(columns=['value_to_use'], inplace=True)