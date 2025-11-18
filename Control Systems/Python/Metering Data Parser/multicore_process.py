
# process_block.py
# Worker function for parallel block processing

import pandas as pd
import os
import fetch_data
import parse_data
import analyze_data
import export_data


def process_single_block(block_number: str, 
                         target_month: str, 
                         target_year: str,
                         path_data_folder: str,
                         path_output_folder: str,
                         btu_name_list: list,
                         data_file_prefix: list,
                         data_file_postfix: list,
                         delimiter: str,
                         debug_flag: bool = False) -> dict:
    """
    Process a single block completely - from data loading to export.
    This function runs in a separate process/core.
    
    Returns:
        Dictionary containing block summary statistics for district aggregation
    """
    
    print(f"\n[Core Processing Block {block_number}] Starting...")
    
    # Filter meters that belong to this block
    meters_in_block = [meter for meter in btu_name_list if meter.split('_')[2] == block_number]
    
    # Check if block has any meters
    if not meters_in_block:
        print(f"[Block {block_number}] No meters found - skipping")
        return {
            'block_number': block_number,
            'status': 'empty',
            'num_meters': 0
        }
    
    print(f"[Block {block_number}] Found {len(meters_in_block)} meters")
    
    # Initialize diagnostics for this block
    block_diagnostics = []
    
    # Step 2A: Get file lists for this block's meters
    target_timestamp = target_year + target_month
    prefix_search = data_file_prefix[0] + target_timestamp
    
    # Filter file lists for this block only
    all_rt_files = fetch_data.list_File_Names(
        parentFolderPath=path_data_folder,
        childFolderNames=meters_in_block,
        prefix=prefix_search,
        postfix=data_file_postfix[0],
        delimiter=delimiter,
        debugFlag=False
    )
    
    all_rth_files = fetch_data.list_File_Names(
        parentFolderPath=path_data_folder,
        childFolderNames=meters_in_block,
        prefix=prefix_search,
        postfix=data_file_postfix[1],
        delimiter=delimiter,
        debugFlag=False
    )
    
    if not all_rt_files and not all_rth_files:
        print(f"[Block {block_number}] No data files found - skipping")
        return {
            'block_number': block_number,
            'status': 'no_data',
            'num_meters': len(meters_in_block)
        }
    
    print(f"[Block {block_number}] Found {len(all_rt_files)} RT files, {len(all_rth_files)} RTH files")
    
    # Step 2B: Initialize DataFrame for this block
    block_dataframe = parse_data.initialize_Block_DataFrame(
        month=target_month,
        year=target_year,
        blockNumber=block_number,
        meterList=btu_name_list
    )
    
    # Step 2C: Populate RT Data
    if all_rt_files:
        print(f"[Block {block_number}] Populating RT data...")
        block_df_dict = {block_number: block_dataframe}
        
        parse_data.populate_Meter_DataFrame(
            fileList=all_rt_files,
            blockDataFrames=block_df_dict,
            diagnoseStatsRegisters=block_diagnostics,
            dataFolderPath=path_data_folder,
            delimiter=delimiter,
            columnSuffix='RT'
        )
    
    # Extract the updated DataFrame back
    block_dataframe = block_df_dict[block_number]
    print(f"[Block {block_number}] RT data populated - checking first RT column sum: {block_dataframe.filter(regex='_RT$').iloc[:, 0].sum() if len(block_dataframe.filter(regex='_RT$').columns) > 0 else 0}")

    # Step 2D: Populate RTH Data
    if all_rth_files:
        print(f"[Block {block_number}] Populating RTH data...")
        block_df_dict = {block_number: block_dataframe}
        
        parse_data.populate_Meter_DataFrame(
            fileList=all_rth_files,
            blockDataFrames=block_df_dict,
            diagnoseStatsRegisters=block_diagnostics,
            dataFolderPath=path_data_folder,
            delimiter=delimiter,
            columnSuffix='RTH'
        )
        
        # Extract the updated DataFrame back
        block_dataframe = block_df_dict[block_number]
        print(f"[Block {block_number}] RTH data populated - checking first RTH column sum: {block_dataframe.filter(regex='_RTH$').iloc[:, 0].sum() if len(block_dataframe.filter(regex='_RTH$').columns) > 0 else 0}")

    print(f"[Block {block_number}] DataFrame populated - Shape: {block_dataframe.shape}")
    print(f"[Block {block_number}] Sample data check - Row 100:")
    print(block_dataframe.iloc[100])
    
    # Step 3: Analyze block data
    block_rt_stats = analyze_data.analyze_Block_RT_Data(
        blockDataFrame=block_dataframe,
        meterList=btu_name_list,
        blockNumber=block_number,
        includeFaultyData=True
    )
    
    block_rth_stats = analyze_data.analyze_Block_RTH_Data(
        blockDataFrame=block_dataframe,
        meterList=btu_name_list,
        blockNumber=block_number
    )
    
    print(f"[Block {block_number}] Analysis complete")
    
    # Step 4: Export block data
    output_folder = os.path.join(path_output_folder, f"{target_month}_{target_year}")
    os.makedirs(output_folder, exist_ok=True)
    
    # Export to Excel with multiple sheets
    export_block_to_excel(
        block_dataframe=block_dataframe,
        block_number=block_number,
        block_rt_stats=block_rt_stats,
        block_rth_stats=block_rth_stats,
        meters_in_block=meters_in_block,
        output_folder=output_folder,
        target_month=target_month,
        target_year=target_year,
        analyze_data_module=analyze_data
    )
    
    print(f"[Block {block_number}] Export complete")
    
    # Return lightweight summary for district aggregation
    summary = {
        'block_number': block_number,
        'status': 'success',
        'num_meters': len(meters_in_block),
        'rt_totalized': block_rt_stats['Block_Totalized_Value'],
        'rt_operating_hours': block_rt_stats['Block_Total_Operating_Hours'],
        'rt_data_completeness': block_rt_stats['Block_Data_Completeness_Percentage'],
        'rth_monthly_consumption': block_rth_stats['Block_Monthly_Consumption'],
        'rth_totalized': block_rth_stats['Block_Totalized_Value'],
        'rth_data_completeness': block_rth_stats['Block_Data_Completeness_Percentage'],
        'diagnostics': block_diagnostics
    }
    
    print(f"[Block {block_number}] Processing complete ✓")
    
    return summary


def export_block_to_excel(block_dataframe, block_number, block_rt_stats, block_rth_stats,
                          meters_in_block, output_folder, target_month, target_year,
                          analyze_data_module):
    """
    Export a single block to Excel with multiple sheets:
    1. Summary - Block-level statistics
    2. Data Statistics - Per-meter statistics
    3. Raw Data - Full DataFrame
    """
    
    import pandas as pd
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    
    output_filename = f"Block_{block_number}.xlsx"
    output_path = os.path.join(output_folder, output_filename)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: Summary
        summary_data = {
            'Metric': [
                'Block Number',
                'Number of Meters',
                'Month/Year',
                '',
                '=== RT Statistics ===',
                'Block Totalized Value',
                'Block Average Value',
                'Total Operating Hours',
                'Data Completeness (%)',
                '',
                '=== RTH Statistics ===',
                'Block Monthly Consumption (BILLING)',
                'Block Totalized Value',
                'Data Completeness (%)'
            ],
            'Value': [
                block_number,
                block_rt_stats['Number_of_Meters'],
                f"{target_month}/{target_year}",
                '',
                '',
                f"{block_rt_stats['Block_Totalized_Value']:.4f}",
                f"{block_rt_stats['Block_Average_Value']:.4f}",
                f"{block_rt_stats['Block_Total_Operating_Hours']:.2f}",
                f"{block_rt_stats['Block_Data_Completeness_Percentage']:.2f}",
                '',
                '',
                f"{block_rth_stats['Block_Monthly_Consumption']:.4f}",
                f"{block_rth_stats['Block_Totalized_Value']:.4f}",
                f"{block_rth_stats['Block_Data_Completeness_Percentage']:.2f}"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Data Statistics (per meter)
        stats_rows = []
        for meter in meters_in_block:
            rt_stats = analyze_data_module.analyze_Meter_RT_Data(block_dataframe, meter, includeFaultyData=True)
            rth_stats = analyze_data_module.analyze_Meter_RTH_Data(block_dataframe, meter)
            
            stats_rows.append({
                'Meter_Name': meter,
                'RT_Totalized': rt_stats['Totalized_Value'],
                'RT_Average': rt_stats['Average_Value'],
                'RT_Operating_Hours': rt_stats['Operating_Hours'],
                'RT_Data_Completeness': rt_stats['Data_Completeness_Percentage'],
                'RTH_Monthly_Consumption': rth_stats['Monthly_Consumption'],
                'RTH_Totalized': rth_stats['Totalized_Value'],
                'RTH_First_Value': rth_stats['First_Healthy_RTH_ProcessValue'],
                'RTH_Last_Value': rth_stats['Last_Healthy_RTH_ProcessValue'],
                'RTH_Data_Completeness': rth_stats['Data_Completeness_Percentage']
            })
        
        stats_df = pd.DataFrame(stats_rows)
        stats_df.to_excel(writer, sheet_name='Data Statistics', index=False)
        
        # Sheet 3: Raw Data
        block_dataframe.to_excel(writer, sheet_name='Raw Data', index=False)
    
    print(f"[Block {block_number}] Excel exported: {output_path}")