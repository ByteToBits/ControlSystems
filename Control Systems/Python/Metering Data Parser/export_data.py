
# export_data.py
import os
from datetime import datetime
import pandas as pd

def write_Analysis_Report(blockDataFrames: dict, blockList: list, meterList: list, 
                          outputPath: str, targetMonth: str, targetYear: str,
                          analyze_data_module):
    """
    Generate complete analysis report and save to text file.
    
    Args:
        blockDataFrames: Dictionary of block DataFrames
        blockList: List of block numbers
        meterList: List of all meter names
        outputPath: Path to output folder
        targetMonth: Target month
        targetYear: Target year
        analyze_data_module: Reference to analyze_data module for analysis functions
    """
    
    # Create output file path
    output_filename = f"Metering_Report_{targetMonth}_{targetYear}.txt"
    full_output_path = os.path.join(outputPath, "Reports", output_filename)
    
    # Ensure output directory exists
    os.makedirs(os.path.join(outputPath, "Reports"), exist_ok=True)
    
    # Open file for writing
    with open(full_output_path, 'w') as report_file:
        
        # Write header
        report_file.write("="*80 + "\n")
        report_file.write(f"METERING DATA ANALYSIS REPORT\n")
        report_file.write(f"Month: {targetMonth}/{targetYear}\n")
        report_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_file.write("="*80 + "\n\n")
        
        # Process all blocks and meters
        for block in blockList:
            
            # Find all meters in this block
            meters_in_block = [meter for meter in meterList if meter.split('_')[2] == block]
            
            # Analyze block-level statistics
            block_rt_stats = analyze_data_module.analyze_Block_RT_Data(blockDataFrames[block], meterList, block)
            block_rth_stats = analyze_data_module.analyze_Block_RTH_Data(blockDataFrames[block], meterList, block)
            
            # Write block summary
            write_Block_Statistics(report_file, block, block_rt_stats, block_rth_stats)
            
            # Write individual meter statistics
            for meter in meters_in_block:
                rt_stats = analyze_data_module.analyze_Meter_RT_Data(blockDataFrames[block], meter)
                rth_stats = analyze_data_module.analyze_Meter_RTH_Data(blockDataFrames[block], meter)
                # write_Meter_Statistics(report_file, meter, rt_stats, rth_stats)
        
        # Write footer
        report_file.write("\n" + "="*80 + "\n")
        report_file.write("END OF REPORT\n")
        report_file.write("="*80 + "\n")
    
    print(f"\nAnalysis report saved to: {full_output_path}")
    return full_output_path


def write_Meter_Statistics(file, meter_name: str, rt_stats: dict, rth_stats: dict):
    """Write meter statistics to file (internal helper)."""
    
    file.write(f"\n{'='*80}\n")
    file.write(f"METER: {meter_name}\n")
    file.write(f"{'='*80}\n")
    
    file.write(f"\n--- RT Statistics ---\n")
    file.write(f"  Totalized Value:        {rt_stats['Totalized_Value']:>15,.4f}\n")
    file.write(f"  Average Value:          {rt_stats['Average_Value']:>15,.4f}\n")
    file.write(f"  Operating Hours:        {rt_stats['Operating_Hours']:>15,.2f}\n")
    file.write(f"  Healthy Data Points:    {rt_stats['Number_of_Healthy_DataPoints']:>15,}\n")
    file.write(f"  Faulty Data Points:     {rt_stats['Number_of_Faulty_DataPoints']:>15,}\n")
    file.write(f"  Data Completeness:      {rt_stats['Data_Completeness_Percentage']:>15,.2f}%\n")
    
    file.write(f"\n--- RTH Statistics ---\n")
    file.write(f"  Monthly Consumption:    {rth_stats['Monthly_Consumption']:>15,.4f}  (BILLING)\n")
    file.write(f"  Totalized Value:        {rth_stats['Totalized_Value']:>15,.4f}\n")
    file.write(f"  First Value:            {rth_stats['First_Healthy_RTH_ProcessValue']:>15,.4f}\n")
    file.write(f"  First Timestamp:        {rth_stats['First_Healthy_RTH_Timestamp']:>15}\n")
    file.write(f"  Last Value:             {rth_stats['Last_Healthy_RTH_ProcessValue']:>15,.4f}\n")
    file.write(f"  Last Timestamp:         {rth_stats['Last_Healthy_RTH_Timestamp']:>15}\n")
    file.write(f"  Healthy Data Points:    {rth_stats['Number_of_Healthy_DataPoints']:>15,}\n")
    file.write(f"  Faulty Data Points:     {rth_stats['Number_of_Faulty_DataPoints']:>15,}\n")
    file.write(f"  Data Completeness:      {rth_stats['Data_Completeness_Percentage']:>15,.2f}%\n")


def write_Block_Statistics(file, block_number: str, block_rt_stats: dict, block_rth_stats: dict):
    """Write block statistics to file (internal helper)."""
    
    file.write(f"\n{'='*80}\n")
    file.write(f"BLOCK {block_number} - SUMMARY\n")
    file.write(f"{'='*80}\n")
    
    file.write(f"\n--- Block RT Statistics ---\n")
    file.write(f"  Number of Meters:       {block_rt_stats['Number_of_Meters']:>15}\n")
    file.write(f"  Block Totalized Value:  {block_rt_stats['Block_Totalized_Value']:>15,.4f}\n")
    file.write(f"  Block Average Value:    {block_rt_stats['Block_Average_Value']:>15,.4f}\n")
    file.write(f"  Total Operating Hours:  {block_rt_stats['Block_Total_Operating_Hours']:>15,.2f}\n")
    file.write(f"  Data Completeness:      {block_rt_stats['Block_Data_Completeness_Percentage']:>15,.2f}%\n")
    
    file.write(f"\n--- Block RTH Statistics ---\n")
    file.write(f"  Number of Meters:       {block_rth_stats['Number_of_Meters']:>15}\n")
    file.write(f"  Monthly Consumption:    {block_rth_stats['Block_Monthly_Consumption']:>15,.4f}  (BILLING)\n")
    file.write(f"  Block Totalized Value:  {block_rth_stats['Block_Totalized_Value']:>15,.4f}\n")
    file.write(f"  Data Completeness:      {block_rth_stats['Block_Data_Completeness_Percentage']:>15,.2f}%\n")


def write_DataFrames_to_Excel(blockDataFrames: dict, outputPath: str, targetMonth: str, targetYear: str):
    """
    Export block DataFrames to Excel file with each block as a separate sheet.
    
    Args:
        blockDataFrames: Dictionary of block DataFrames
        outputPath: Path to output folder
        targetMonth: Target month
        targetYear: Target year
    """
    
    # Create output file path
    output_filename = f"Metering_Report_{targetMonth}_{targetYear}.xlsx"
    full_output_path = os.path.join(outputPath, "Reports", output_filename)
    
    # Ensure output directory exists
    os.makedirs(os.path.join(outputPath, "Reports"), exist_ok=True)
    
    # Create Excel writer
    with pd.ExcelWriter(full_output_path, engine='openpyxl') as writer:
        
        # Create a placeholder first sheet (will be empty for now)
        placeholder_df = pd.DataFrame()
        placeholder_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Write each block DataFrame to a separate sheet
        for block, df in blockDataFrames.items():
            sheet_name = f'Block {block}'
            
            # Write DataFrame starting from row 2 (leave row 1 blank)
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
    
    print(f"\nDataFrames exported to Excel: {full_output_path}")
    return full_output_path


def write_Diagnostic_Log(diagnosticsList: list, outputPath: str, targetMonth: str, targetYear: str, runtime: float):
    """
    Write diagnostic statistics to a text file in raw format.
    
    Args:
        diagnosticsList: List of diagnostic dictionaries
        outputPath: Path to output folder
        targetMonth: Target month
        targetYear: Target year
    """
    
    # Create output file path
    output_filename = f"Diagnostic_Log_{targetMonth}_{targetYear}.txt"
    full_output_path = os.path.join(outputPath, "Output Log", output_filename)
    
    # Ensure output directory exists
    os.makedirs(os.path.join(outputPath, "Output Log"), exist_ok=True)
    
    # Write to file
    with open(full_output_path, 'w') as log_file:
        
        # Write header
        log_file.write("="*80 + "\n")
        log_file.write(f"DIAGNOSTIC LOG\n")
        log_file.write(f"Month: {targetMonth}/{targetYear}\n")
        log_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Total Runtime: {runtime:.2f} seconds ({runtime/60:.2f} minutes)\n")
        log_file.write("="*80 + "\n\n")
        
        # Write raw diagnostic data
        for diag in diagnosticsList:
            log_file.write(str(diag) + "\n\n")
    
    print(f"\nDiagnostic log saved to: {full_output_path}")
    return full_output_path

