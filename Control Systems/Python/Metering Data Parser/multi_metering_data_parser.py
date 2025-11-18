# multi_metering_data_parser.py
# Main Program with Multiprocessing

import pandas as pd
import time
import os
from multiprocessing import Pool, cpu_count, freeze_support
from datetime import datetime

# Import Custom Library
import fetch_data
import multicore_process  # NEW: Import the worker module


def main():
    """Main execution function - must be called from if __name__ == '__main__' block"""
    
    # Configuration
    targetMonth = '10'
    targetYear = '2025'
    pathDataFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\data'
    pathOutputFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\data\Metering Summary Report'

    DEBUG_FLAG = True
    DELIMITER = ';'
    NUM_CORES = 10  # Fixed: 10 blocks = 10 cores

    btuNamePrefix = ["J_B_"]
    dataFilePrefix = ["X01_01_"]
    dataFilePostfix = ["BTUREADINGS11MIN.txt", "ACCBTUReadingS11MIN.txt"]

    # Define block numbers (80, 82, 84, ..., 98)
    BLOCK_NUMBERS = [str(80 + i*2) for i in range(10)]  # ['80', '82', '84', ..., '98']

    # Track runtime
    start_time = time.time()


    # ============================================================================
    # Step 1: Fetch all File and Folder Information (Sequential)
    # ============================================================================
    print("\n" + "="*80)
    print("Step 1: Fetch all File and Folder Information")
    print("="*80)

    # Fetch all BTU meter folder names
    btuNameList = fetch_data.list_Folder_Names(
        folderPath=pathDataFolder,
        namePrefix=btuNamePrefix,
        debugFlag=DEBUG_FLAG
    )

    # List all unique blocks
    btuBlockList = fetch_data.list_Meter_Blocks(nameList=btuNameList)

    if DEBUG_FLAG:
        print(f"\nFound {len(btuNameList)} BTU Meters")
        print(f"Found {len(btuBlockList)} Unique Blocks: {btuBlockList}")
        print(f"Processing blocks: {BLOCK_NUMBERS}")

    print("\nStep 1: Completed ✓\n")


    # ============================================================================
    # Step 2-4: Parallel Block Processing (10 Cores)
    # ============================================================================
    print("\n" + "="*80)
    print("Step 2-4: Parallel Block Processing (Using 10 Cores)")
    print("="*80)

    # Prepare arguments for each block
    block_args = [
        (
            block_num,
            targetMonth,
            targetYear,
            pathDataFolder,
            pathOutputFolder,
            btuNameList,
            dataFilePrefix,
            dataFilePostfix,
            DELIMITER,
            False  # debug_flag per process
        )
        for block_num in BLOCK_NUMBERS
    ]

    # Execute parallel processing
    print(f"\nSpawning {NUM_CORES} processes...\n")

    with Pool(processes=NUM_CORES) as pool:
        # Use starmap to unpack arguments
        block_summaries = pool.starmap(multicore_process.process_single_block, block_args)

    print("\n" + "="*80)
    print("All Block Processing Complete ✓")
    print("="*80)


    # ============================================================================
    # Step 5: Aggregate District-Level Summary (Sequential)
    # ============================================================================
    print("\n" + "="*80)
    print("Step 5: Aggregate District-Level Summary")
    print("="*80)

    # Filter successful blocks
    successful_blocks = [s for s in block_summaries if s['status'] == 'success']
    empty_blocks = [s for s in block_summaries if s['status'] == 'empty']
    no_data_blocks = [s for s in block_summaries if s['status'] == 'no_data']

    print(f"\nSuccessful: {len(successful_blocks)} blocks")
    print(f"Empty: {len(empty_blocks)} blocks")
    print(f"No Data: {len(no_data_blocks)} blocks")

    # Calculate district totals
    district_summary = {
        'total_meters': sum(s['num_meters'] for s in successful_blocks),
        'total_rt_totalized': sum(s['rt_totalized'] for s in successful_blocks),
        'total_rt_operating_hours': sum(s['rt_operating_hours'] for s in successful_blocks),
        'total_rth_consumption': sum(s['rth_monthly_consumption'] for s in successful_blocks),
        'total_rth_totalized': sum(s['rth_totalized'] for s in successful_blocks),
        'avg_rt_completeness': sum(s['rt_data_completeness'] for s in successful_blocks) / len(successful_blocks) if successful_blocks else 0,
        'avg_rth_completeness': sum(s['rth_data_completeness'] for s in successful_blocks) / len(successful_blocks) if successful_blocks else 0
    }

    # Write District Summary
    output_folder = os.path.join(pathOutputFolder, f"{targetMonth}_{targetYear}")
    os.makedirs(output_folder, exist_ok=True)
    district_summary_path = os.path.join(output_folder, "District_Summary.txt")

    with open(district_summary_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("DISTRICT-LEVEL SUMMARY\n")
        f.write(f"Month: {targetMonth}/{targetYear}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Total Meters Processed: {district_summary['total_meters']}\n")
        f.write(f"Successful Blocks: {len(successful_blocks)}\n")
        f.write(f"Empty Blocks: {len(empty_blocks)}\n")
        f.write(f"No Data Blocks: {len(no_data_blocks)}\n\n")
        
        f.write("--- RT Statistics (District) ---\n")
        f.write(f"  Total Totalized Value:        {district_summary['total_rt_totalized']:>20,.4f}\n")
        f.write(f"  Total Operating Hours:        {district_summary['total_rt_operating_hours']:>20,.2f}\n")
        f.write(f"  Average Data Completeness:    {district_summary['avg_rt_completeness']:>20,.2f}%\n\n")
        
        f.write("--- RTH Statistics (District) ---\n")
        f.write(f"  Total Monthly Consumption:    {district_summary['total_rth_consumption']:>20,.4f}  (BILLING)\n")
        f.write(f"  Total Totalized Value:        {district_summary['total_rth_totalized']:>20,.4f}\n")
        f.write(f"  Average Data Completeness:    {district_summary['avg_rth_completeness']:>20,.2f}%\n\n")
        
        f.write("="*80 + "\n")
        f.write("BLOCK-BY-BLOCK BREAKDOWN\n")
        f.write("="*80 + "\n\n")
        
        for summary in sorted(successful_blocks, key=lambda x: x['block_number']):
            f.write(f"Block {summary['block_number']}:\n")
            f.write(f"  Meters: {summary['num_meters']}\n")
            f.write(f"  RT Totalized: {summary['rt_totalized']:.4f}\n")
            f.write(f"  RTH Monthly Consumption: {summary['rth_monthly_consumption']:.4f}\n")
            f.write(f"  RT Completeness: {summary['rt_data_completeness']:.2f}%\n")
            f.write(f"  RTH Completeness: {summary['rth_data_completeness']:.2f}%\n\n")

    print(f"\nDistrict summary saved: {district_summary_path}")

    # Aggregate all diagnostics
    all_diagnostics = []
    for summary in successful_blocks:
        all_diagnostics.extend(summary.get('diagnostics', []))

    # Write diagnostic log
    end_time = time.time()
    runtime = end_time - start_time

    diagnostic_path = os.path.join(output_folder, f"Diagnostic_Log_{targetMonth}_{targetYear}.txt")
    with open(diagnostic_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("DIAGNOSTIC LOG\n")
        f.write(f"Month: {targetMonth}/{targetYear}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Runtime: {runtime:.2f} seconds ({runtime/60:.2f} minutes)\n")
        f.write("="*80 + "\n\n")
        
        for diag in all_diagnostics:
            f.write(str(diag) + "\n\n")

    print(f"Diagnostic log saved: {diagnostic_path}")

    print("\nStep 5: Completed ✓\n")


    # ============================================================================
    # Final Summary
    # ============================================================================
    print("\n" + "="*80)
    print("PROCESSING COMPLETE")
    print("="*80)
    print(f"Total Runtime: {runtime:.2f} seconds ({runtime/60:.2f} minutes)")
    print(f"Output Location: {output_folder}")
    print(f"  - {len(successful_blocks)} Block Excel files")
    print(f"  - District_Summary.txt")
    print(f"  - Diagnostic_Log_{targetMonth}_{targetYear}.txt")
    print("="*80 + "\n")


# ============================================================================
# CRITICAL: This guard is REQUIRED for Windows multiprocessing
# ============================================================================
if __name__ == '__main__':
    freeze_support()  # Optional but recommended for frozen executables
    main()