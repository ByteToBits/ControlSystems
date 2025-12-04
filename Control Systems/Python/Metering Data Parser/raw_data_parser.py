# Project: Metering Data Parser
# File: convert_dat_to_txt.py
# Description: Convert .dat files to .txt files filtered by target day
# 
# Author: Tristan Sim
# Date: 04/12/2025
# Version: 1.0

import os
import time
from datetime import datetime

# Import Custom Library
import fetch_data

# Configuration
targetDay = "07"  # Extract specific day from monthly file
targetMonth = '10'
targetYear = '2025'
pathDataFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\data\Raw Data Files'
pathOutputFolder = r'C:\Repository\ControlSystems\Control Systems\Python\Metering Data Parser\Output'

DEBUG_FLAG = True
DELIMITER = ';'

# File types to process
dataFilePrefix = ["X01_01_"]
dataFilePostfix = [
    "BTUREADINGS11MIN.dat", 
    "ACCBTUReadingS11MIN.dat", 
    "FLOWS11MIN.dat", 
    "TEMPS1SUPPLY1MIN.dat", 
    "TEMPS1RETURN1MIN.dat", 
    "TEMPDeltaS11MIN.dat"
]

# Output file names
outputFileNames = [
    "RT_Data", 
    "RTH_Data", 
    "Flow_Data", 
    "CHWST_Data", 
    "CHWRT_Data", 
    "DeltaTemp_Data"
]

# Track runtime
start_time = time.time()


def filter_data_by_day(input_file_path: str, output_file_path: str, target_date: str, debug: bool = False) -> dict:
    """
    Read .dat file and filter data by target day, save to .txt file.
    
    Args:
        input_file_path: Path to input .dat file
        output_file_path: Path to output .txt file
        target_date: Target date in format 'YYYY-MM-DD' (e.g., '2025-10-02')
        debug: Enable debug output
    
    Returns:
        Dictionary with statistics about the conversion
    """
    lines_read = 0
    lines_written = 0
    skipped_comments = 0
    skipped_empty = 0
    parse_errors = 0
    date_mismatches = 0
    
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        # Try opening with different encodings
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        file_opened = False
        used_encoding = None
        
        for enc in encodings_to_try:
            try:
                with open(input_file_path, 'r', encoding=enc) as test_file:
                    test_file.read(100)  # Try reading first 100 chars
                    used_encoding = enc
                    file_opened = True
                    break
            except:
                continue
        
        if not file_opened:
            return {
                'lines_read': 0,
                'lines_written': 0,
                'success': False,
                'error': 'Could not open file with any encoding'
            }
        
        with open(input_file_path, 'r', encoding=used_encoding) as input_file:
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                
                first_data_line = None
                
                for line in input_file:
                    lines_read += 1
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        skipped_empty += 1
                        continue
                    
                    # Skip comments (including #start and #stop)
                    if line.startswith('#'):
                        skipped_comments += 1
                        continue
                    
                    # Parse data line: "02.10.2025 00:00:00 9006.741"
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            date_string = parts[0]  # "02.10.2025"
                            time_string = parts[1]  # "00:00:00"
                            
                            # Save first data line for debugging
                            if first_data_line is None:
                                first_data_line = line
                            
                            # Convert to standard format for comparison
                            timestamp_string = f"{date_string} {time_string}"
                            timestamp = datetime.strptime(timestamp_string, "%d.%m.%Y %H:%M:%S")
                            formatted_date = timestamp.strftime('%Y-%m-%d')
                            
                            # Check if this line matches target date
                            if formatted_date == target_date:
                                output_file.write(line + '\n')
                                lines_written += 1
                            else:
                                date_mismatches += 1
                    
                    except Exception as e:
                        parse_errors += 1
                        if debug and parse_errors <= 3:
                            print(f"    Parse error on line {lines_read}: {line[:50]}... - {e}")
                        continue
        
        stats = {
            'lines_read': lines_read,
            'lines_written': lines_written,
            'skipped_comments': skipped_comments,
            'skipped_empty': skipped_empty,
            'parse_errors': parse_errors,
            'date_mismatches': date_mismatches,
            'first_data_line': first_data_line,
            'success': True
        }
        
        return stats
    
    except Exception as e:
        print(f"Error processing file {input_file_path}: {e}")
        return {
            'lines_read': lines_read,
            'lines_written': lines_written,
            'success': False,
            'error': str(e)
        }


def process_all_meters(meter_list: list, file_lists: list, file_types: list, output_names: list,
                       data_folder: str, output_folder: str, target_date: str, 
                       year: str, month: str, day: str, delimiter: str, debug: bool = False):
    """
    Process all meters and convert .dat files to .txt files for target day.
    """
    
    total_files_processed = 0
    total_files_success = 0
    total_lines_written = 0
    conversion_stats = []
    
    # Process each file type
    for file_type_idx, file_list in enumerate(file_lists):
        output_name = output_names[file_type_idx]
        print(f"\nProcessing {output_name}...")
        
        for file_entry in file_list:
            total_files_processed += 1
            
            # Parse file entry
            parts = file_entry.split(delimiter)
            meter_name = parts[0]
            file_name = parts[1]
            
            # Construct paths
            input_path = os.path.join(data_folder, meter_name, file_name)
            output_dir = os.path.join(output_folder, f"Year={year}", f"Month={month}", 
                                     f"Date={day}", meter_name)
            output_filename = f"{year}_{month}_{day}_{output_name}.txt"
            output_path = os.path.join(output_dir, output_filename)
            
            # Check if input exists
            if not os.path.exists(input_path):
                print(f"  Missing: {meter_name} - File not found: {input_path}")
                continue
            
            # Check file size
            file_size = os.path.getsize(input_path)
            if file_size == 0:
                print(f"  Empty: {meter_name} - File size: 0 bytes")
                continue
            
            if debug:
                print(f"Processing: {meter_name} - Size: {file_size} bytes")
            
            # Process the file
            stats = filter_data_by_day(input_path, output_path, target_date, debug)
            
            if stats['success']:
                total_files_success += 1
                total_lines_written += stats['lines_written']
                if stats['lines_written'] > 0:
                    print(f"{meter_name}: {stats['lines_written']} lines")
                else:
                    print(f"{meter_name}: 0 lines (read:{stats['lines_read']}, comments:{stats['skipped_comments']}, mismatches:{stats['date_mismatches']}, first_line:{stats.get('first_data_line', 'None')[:40]}...)")
            else:
                print(f"{meter_name}: Failed")
            
            conversion_stats.append({
                'meter': meter_name,
                'file_type': output_name,
                'stats': stats
            })
    
    return total_files_processed, total_files_success, total_lines_written, conversion_stats


# Main execution
print(f"\nDAT TO TXT CONVERTER - {targetYear}-{targetMonth}-{targetDay}")
print(f"Input:  {pathDataFolder}")
print(f"Output: {pathOutputFolder}\n")

# Step 1: Fetch meter folders
print("Fetching meters...")
btuNameList = fetch_data.list_Folder_Names(
    folderPath=pathDataFolder, 
    namePrefix=["J_B_"], 
    debugFlag=False
)
btuBlockList = fetch_data.list_Meter_Blocks(nameList=btuNameList)
print(f"Found {len(btuNameList)} meters in {len(btuBlockList)} blocks")

# Step 2: Fetch file names
print("\nFetching files...")
prefixSearchCriteria = dataFilePrefix[0] + targetYear + targetMonth

all_file_lists = []
for postfix in dataFilePostfix:
    file_list = fetch_data.list_File_Names(
        parentFolderPath=pathDataFolder,
        childFolderNames=btuNameList,
        prefix=prefixSearchCriteria,
        postfix=postfix,
        delimiter=DELIMITER,
        debugFlag=False
    )
    all_file_lists.append(file_list)

total_files = sum(len(fl) for fl in all_file_lists)
print(f"Found {total_files} files to process")

# Step 3: Convert files
print("\nConverting files...")
target_date = f"{targetYear}-{targetMonth}-{targetDay}"

processed, success, lines, stats = process_all_meters(
    meter_list=btuNameList,
    file_lists=all_file_lists,
    file_types=dataFilePostfix,
    output_names=outputFileNames,
    data_folder=pathDataFolder,
    output_folder=pathOutputFolder,
    target_date=target_date,
    year=targetYear,
    month=targetMonth,
    day=targetDay,
    delimiter=DELIMITER,
    debug=DEBUG_FLAG
)

# Summary
end_time = time.time()
runtime = end_time - start_time

print(f"Files processed: {processed}")
print(f"Files success:   {success}")
print(f"Files failed:    {processed - success}")
print(f"Lines written:   {lines:,}")
print(f"Runtime:         {runtime:.2f}s")