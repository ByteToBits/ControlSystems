
# Project: Metering Data Parser
# File Type: Function File

# Description: Analyze Data
# Contains Functions that Analyzes and Process Data based on End-Users Requirements

# Aurthor: Tristan Sim
# Date: 11/11/2025
# Version: 1.01
# Changelog: 

import pandas as pd

def analyze_Meter_RT_Data(blockDataFrame: pd.DataFrame, meterName: str) -> dict:
    """
    Process RT meter data and extract statistics for 1 Meter. 
    Args:
        blockDataFrame: DataFrame containing meter data
        meterName: Full meter name (e.g., 'J_B_82_10_27')
    Returns:
        Dictionary containing RT statistics
    """
    
    rt_Column = f'{meterName}_RT'
    rt_Data = blockDataFrame[rt_Column]
    rt_healthy = rt_Data[rt_Data > 0]
    
    # Average Value of the RT Data
    if not rt_healthy.empty:
        average_value = rt_healthy.mean()
    else:
        average_value = 0.0
    
    # Calculate operating/uptime hours (RT > 0 means operating)
    operating_minutes = len(rt_healthy)
    operating_hours = operating_minutes / 60.0
    
    # Statistics of the Process Data
    total_datapoints = len(rt_Data)
    healthy_datapoints = len(rt_healthy)
    faulty_datapoints = total_datapoints - healthy_datapoints
    
    data_completeness = (healthy_datapoints / total_datapoints * 100) if total_datapoints > 0 else 0.0
    
    analyzed_MeterData_RT = {
        'Totalized_Value': rt_healthy.sum(),
        'Number_of_DataPoints': total_datapoints,
        'Average_Value': average_value,
        'Operating_Hours': operating_hours,
        'Number_of_Healthy_DataPoints': healthy_datapoints,
        'Number_of_Faulty_DataPoints': faulty_datapoints,
        'Data_Completeness_Percentage': round(data_completeness, 2)
    }
    
    return analyzed_MeterData_RT


def analyze_Block_RT_Data(blockDataFrame: pd.DataFrame, meterList: list, blockNumber: str) -> dict:
    """
    Process and totalize RT data for all meters in a block.
    Args:
        blockDataFrame: DataFrame containing all meter data for the block
        meterList: List of all meter names
        blockNumber: Block number ('82')
    Returns:
        Dictionary containing block-level RT statistics
    """
    
    # Find all meters in this block
    meters_in_block = [meter for meter in meterList if meter.split('_')[2] == blockNumber]
    
    # Initialize aggregated values
    total_totalized = 0.0
    total_operating_hours = 0.0
    total_healthy_datapoints = 0
    total_faulty_datapoints = 0
    total_datapoints = 0
    meter_statistics = {}
    
    # Process each meter and aggregate
    for meter in meters_in_block:
        meter_stats = analyze_Meter_RT_Data(blockDataFrame, meter)
        meter_statistics[meter] = meter_stats
        
        # Aggregate totals
        total_totalized += meter_stats['Totalized_Value']
        total_operating_hours += meter_stats['Operating_Hours']
        total_healthy_datapoints += meter_stats['Number_of_Healthy_DataPoints']
        total_faulty_datapoints += meter_stats['Number_of_Faulty_DataPoints']
        total_datapoints += meter_stats['Number_of_DataPoints']
    
    # Calculate block-level metrics
    block_average = total_totalized / total_healthy_datapoints if total_healthy_datapoints > 0 else 0.0
    block_data_completeness = (total_healthy_datapoints / total_datapoints * 100) if total_datapoints > 0 else 0.0
    
    analyzed_BlockData_RT = {
        'Block_Number': blockNumber,
        'Number_of_Meters': len(meters_in_block),
        'Block_Totalized_Value': total_totalized,
        'Block_Average_Value': block_average,
        'Block_Total_Operating_Hours': total_operating_hours,
        'Block_Total_Healthy_DataPoints': total_healthy_datapoints,
        'Block_Total_Faulty_DataPoints': total_faulty_datapoints,
        'Block_Data_Completeness_Percentage': round(block_data_completeness, 2),
        'Individual_Meters': meter_statistics
    }
    
    return analyzed_BlockData_RT


def analyze_Meter_RTH_Data(blockDataFrame: pd.DataFrame, meterName: str) -> dict:
    """
    Process RTH (accumulated) meter data and extract statistics for 1 Meter.
    
    Args:
        blockDataFrame: DataFrame containing meter data
        meterName: Full meter name (e.g., 'J_B_82_10_27')
    
    Returns:
        Dictionary containing RTH statistics
    """
    
    rth_Column = f'{meterName}_RTH'
    rth_Data = blockDataFrame[rth_Column]
    rth_healthy = rth_Data[rth_Data > 0]
    
    # Find first and last healthy RTH values with timestamps
    if not rth_healthy.empty:
        first_rth_idx = rth_healthy.first_valid_index()
        last_rth_idx = rth_healthy.last_valid_index()
        
        first_rth_value = rth_healthy.iloc[0]
        last_rth_value = rth_healthy.iloc[-1]
        
        first_rth_timestamp = blockDataFrame.loc[first_rth_idx, 'timestamp']
        last_rth_timestamp = blockDataFrame.loc[last_rth_idx, 'timestamp']
        
        # Monthly consumption (Last - First for billing)
        monthly_consumption = last_rth_value - first_rth_value
    else:
        first_rth_value = 0.0
        last_rth_value = 0.0
        first_rth_timestamp = 'N/A'
        last_rth_timestamp = 'N/A'
        monthly_consumption = 0.0
    
    # Totalized value (sum of all healthy RTH data)
    totalized_value = rth_healthy.sum()
    
    # Totalized value unfiltered (sum of all RTH regardless of health)
    totalized_value_unfiltered = rth_Data.sum()
    
    # Calculate data completeness
    total_datapoints = len(rth_Data)
    healthy_datapoints = len(rth_healthy)
    faulty_datapoints = total_datapoints - healthy_datapoints
    data_completeness = (healthy_datapoints / total_datapoints * 100) if total_datapoints > 0 else 0.0
    
    analyzed_MeterData_RTH = {
        'First_Healthy_RTH_ProcessValue': first_rth_value,
        'First_Healthy_RTH_Timestamp': first_rth_timestamp,
        'Last_Healthy_RTH_ProcessValue': last_rth_value,
        'Last_Healthy_RTH_Timestamp': last_rth_timestamp,
        'Monthly_Consumption': monthly_consumption,  # For billing (Last - First)
        'Totalized_Value': totalized_value,  # Sum of all healthy data
        'Totalized_Value_Unfiltered': totalized_value_unfiltered,
        'Number_of_DataPoints': total_datapoints,
        'Number_of_Healthy_DataPoints': healthy_datapoints,
        'Number_of_Faulty_DataPoints': faulty_datapoints,
        'Data_Completeness_Percentage': round(data_completeness, 2)
    }
    
    return analyzed_MeterData_RTH


def analyze_Block_RTH_Data(blockDataFrame: pd.DataFrame, meterList: list, blockNumber: str) -> dict:
    """
    Process and totalize RTH data for all meters in a block.
    
    Args:
        blockDataFrame: DataFrame containing all meter data for the block
        meterList: List of all meter names
        blockNumber: Block number (e.g., '82')
    
    Returns:
        Dictionary containing block-level RTH statistics
    """
    
    # Find all meters in this block
    meters_in_block = [meter for meter in meterList if meter.split('_')[2] == blockNumber]
    
    # Initialize aggregated values
    total_monthly_consumption = 0.0
    total_totalized = 0.0
    total_healthy_datapoints = 0
    total_faulty_datapoints = 0
    total_datapoints = 0
    
    meter_statistics = {}
    
    # Process each meter and aggregate
    for meter in meters_in_block:
        meter_stats = analyze_Meter_RTH_Data(blockDataFrame, meter)
        meter_statistics[meter] = meter_stats
        
        # Aggregate totals
        total_monthly_consumption += meter_stats['Monthly_Consumption']
        total_totalized += meter_stats['Totalized_Value']
        total_healthy_datapoints += meter_stats['Number_of_Healthy_DataPoints']
        total_faulty_datapoints += meter_stats['Number_of_Faulty_DataPoints']
        total_datapoints += meter_stats['Number_of_DataPoints']
    
    # Calculate block-level metrics
    block_data_completeness = (total_healthy_datapoints / total_datapoints * 100) if total_datapoints > 0 else 0.0
    
    analyzed_BlockData_RTH = {
        'Block_Number': blockNumber,
        'Number_of_Meters': len(meters_in_block),
        'Block_Monthly_Consumption': total_monthly_consumption,  # For billing
        'Block_Totalized_Value': total_totalized,
        'Block_Total_Healthy_DataPoints': total_healthy_datapoints,
        'Block_Total_Faulty_DataPoints': total_faulty_datapoints,
        'Block_Data_Completeness_Percentage': round(block_data_completeness, 2),
        'Individual_Meters': meter_statistics
    }
    
    return analyzed_BlockData_RTH


def print_Meter_Statistics(meter_name: str, rt_stats: dict, rth_stats: dict):
    """Print meter statistics in a formatted way."""
    
    print(f"METER: {meter_name}")
    
    print(f"\n--- RT Statistics ---")
    print(f"  Totalized Value:        {rt_stats['Totalized_Value']:>15,.4f}")
    print(f"  Average Value:          {rt_stats['Average_Value']:>15,.4f}")
    print(f"  Operating Hours:        {rt_stats['Operating_Hours']:>15,.2f}")
    print(f"  Healthy Data Points:    {rt_stats['Number_of_Healthy_DataPoints']:>15,}")
    print(f"  Faulty Data Points:     {rt_stats['Number_of_Faulty_DataPoints']:>15,}")
    print(f"  Data Completeness:      {rt_stats['Data_Completeness_Percentage']:>15,.2f}%")
    
    print(f"\n--- RTH Statistics ---")
    print(f"  Monthly Consumption:    {rth_stats['Monthly_Consumption']:>15,.4f}  (BILLING)")
    print(f"  Totalized Value:        {rth_stats['Totalized_Value']:>15,.4f}")
    print(f"  First Value:            {rth_stats['First_Healthy_RTH_ProcessValue']:>15,.4f}")
    print(f"  First Timestamp:        {rth_stats['First_Healthy_RTH_Timestamp']:>15}")
    print(f"  Last Value:             {rth_stats['Last_Healthy_RTH_ProcessValue']:>15,.4f}")
    print(f"  Last Timestamp:         {rth_stats['Last_Healthy_RTH_Timestamp']:>15}")
    print(f"  Healthy Data Points:    {rth_stats['Number_of_Healthy_DataPoints']:>15,}")
    print(f"  Faulty Data Points:     {rth_stats['Number_of_Faulty_DataPoints']:>15,}")
    print(f"  Data Completeness:      {rth_stats['Data_Completeness_Percentage']:>15,.2f}%")


def print_Block_Statistics(block_number: str, block_rt_stats: dict, block_rth_stats: dict):
    """Print block statistics in a formatted way."""
    
    print(f"BLOCK {block_number} - SUMMARY")
    
    print(f"\n--- Block RT Statistics ---")
    print(f"  Number of Meters:       {block_rt_stats['Number_of_Meters']:>15}")
    print(f"  Block Totalized Value:  {block_rt_stats['Block_Totalized_Value']:>15,.4f}")
    print(f"  Block Average Value:    {block_rt_stats['Block_Average_Value']:>15,.4f}")
    print(f"  Total Operating Hours:  {block_rt_stats['Block_Total_Operating_Hours']:>15,.2f}")
    print(f"  Data Completeness:      {block_rt_stats['Block_Data_Completeness_Percentage']:>15,.2f}%")
    
    print(f"\n--- Block RTH Statistics ---")
    print(f"  Number of Meters:       {block_rth_stats['Number_of_Meters']:>15}")
    print(f"  Monthly Consumption:    {block_rth_stats['Block_Monthly_Consumption']:>15,.4f}  (BILLING)")
    print(f"  Block Totalized Value:  {block_rth_stats['Block_Totalized_Value']:>15,.4f}")
    print(f"  Data Completeness:      {block_rth_stats['Block_Data_Completeness_Percentage']:>15,.2f}%")


