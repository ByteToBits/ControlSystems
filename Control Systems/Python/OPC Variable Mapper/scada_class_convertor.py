import re
import csv
import os
from datetime import datetime

def convert_scada_variables():
    # Define file paths based on the folder structure
    output_file = os.path.join("Control Systems", "Python", "OPC Variable Mapper", "Data", "SCADA Class", "SCADAClass.csv")
    input_file = os.path.join("Control Systems", "Python", "OPC Variable Mapper", "Data", "PLC Class", "ClassSource.csv")

    # Read input data from ClassSource.csv
    try:
        with open(input_file, 'r') as f:
            input_data = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    # Parse input data containing SCADA variables
    lines = input_data.strip().split('\n')
    variables = []
    
    for line in lines:
        if '"SCADA_' in line:
            # Extract the variable name from the line (removing quotes)
            var_name = line.split(',')[0].strip('"')
            variables.append(var_name)
    
    # Create output content
    output = []
    
    # Add EquipmentClass header
    output.append("#EquipmentClass,,,,,,,,,,,,,,,,,,,,,,,,,,,")
    output.append("{LocationPath},Name,ExtraParameters,IconName,IconDescription,IconBlob,IconBlob16,IconBlob32,DisplayName,Description,SortOrder,Guid,ItemOrigin,Enabled,IconDefinitionID,CustomIdentifier,Created,Updated,Author,LevelID,EquipmentClassID,SelectedProducts,PollingGroupID,UseExternalLink,ExternalLinkType,ExternalLink,TimeZoneType,TimeZone")
    output.append("\\EquipmentClassesRoot\\[Dyson Equipment Class],Fan Cooling Unit Type 1,,,,,,,,,0,4af3fecc-5960-4833-8d19-dfb1d6d1b287,0,True,,,2018-10-17 13:19:49Z,2025-04-24 07:10:39Z,User,,,63,,False,0,,0,")
    output.append("")
    
    # Add EquipmentClassProperty header
    output.append("#EquipmentClassProperty,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
    output.append("{LocationPath},Name,ExtraParameters,DisplayName,Description,SortOrder,Guid,ItemOrigin,Enabled,UnitOfMeasureID,RangeMinimum,RangeMaximum,TimeZoneType,TimeZone,SelectedProducts,RuntimeParameters,RealtimePointType,RealtimePointName,RealtimeValue,RealtimeDataType,RealtimeReadExpression,RealtimeWriteExpressionEnabled,RealtimeWriteExpression,RealtimeAlwaysOnScan,RealtimeScanRate,RealtimeQualityFilter,UseDatabaseCache,PollingGroupID,HistoryPointType,HistoryPointDifferent,HistoryPointName,DatasetType,DatasetPointName,EventsType")
    
    # Process each variable
    guid_counter = 31  # Start with GUID suffix 031
    base_guid = "dd963c6e-bf2f-41b3-99d6-b0932447a"
    
    # Keep track of unique component parts to avoid duplicates
    unique_components = {}
    
    for var in variables:
        # Remove "SCADA_" prefix
        without_prefix = var[6:]
        
        # Extract device prefix using regex
        match = re.match(r"FCU_\d+_\d+_", without_prefix)
        if match:
            device_prefix = match.group(0)
            component_part = without_prefix[len(device_prefix):]
            
            # Skip if we've already seen this component (to avoid duplicates)
            if component_part in unique_components:
                continue
                
            # Create formatted name with spaces
            name_with_spaces = component_part.replace("_", " ")
            
            # Create GUID with incremented counter
            guid_suffix = f"{guid_counter:03d}"  # Format to 3 digits with leading zeros
            full_guid = f"{base_guid}{guid_suffix}"
            
            # Create formatted output line
            #line = f"\\EquipmentClassesRoot\\[Dyson Equipment Class]\\Fan Cooling Unit Type 1,{name_with_spaces},,,,0,{full_guid},0,True,,,,0,,32,,2,/?TagPath?/_{component_part},,12,,False,,True,1000,0,True,,0,True,,0,,0"
            line = f"\\EquipmentClassesRoot\\[Dyson Equipment Class]\\Fan Cooling Unit Type 1,{name_with_spaces},,,,0,{full_guid},0,True,,,,0,,32,,2,/?TagPath?/_{component_part},,12,,False,,False,1000,0,True,,0,True,,0,,0"
            
            output.append(line)
            unique_components[component_part] = full_guid
            guid_counter += 1
    
    # Add EquipmentClassParameterDefinition section
    output.append("")
    output.append("#EquipmentClassParameterDefinition,,,")
    output.append("{LocationPath},Name,Description,DefaultValue")
    output.append("\\EquipmentClassesRoot\\[Dyson Equipment Class]\\Fan Cooling Unit Type 1,TagPath,,")
    output.append("")
    
    # Add VersionTable section
    current_time = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
    output.append("#VersionTable,,,")
    output.append("ExportTime,IEVersion,SupportedVersion,Description")
    output.append(f"{current_time},10.97.306.00,2.6,Assets Configuration")
    
    # Write to output file
    with open(output_file, 'w', newline='') as f:
        for line in output:
            f.write(line + '\n')
    
    print(f"Conversion complete! Processed {len(variables)} variables, created {len(unique_components)} unique components.")
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    convert_scada_variables()