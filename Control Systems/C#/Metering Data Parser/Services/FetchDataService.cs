// Project: Metering Data Parser
// File: FetchDataService.cs
// Description: Fetch Data - Retrieves and lists raw data files
// 
// Author: Tristan Sim
// Date: 18/11/2025
// Version: 1.0

using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;
using MeteringDataParser.Models;

namespace MeteringDataParser.Services
{
    /// <summary>
    /// Fetch Data Service fetches and list the Meter Data File Names
    /// </summary>
    public static class FetchDataService
    {
        /// <summary>
        /// List all folder names matching the given prefixes.
        /// </summary>
        /// <param name="folderPath">Path to the parent data folder</param>
        /// <param name="namePrefixes">List of valid folder name prefixes</param>
        /// <param name="debugFlag">Enable debug output</param>
        /// <returns>Sorted list of folder names</returns>
        public static List<string> ListFolderNames(string folderPath, List<string> namePrefixes, bool debugFlag)
        {
            var folderNames = new List<string>();
            try
            {
                if (!Directory.Exists(folderPath)) // If the Directory Exists
                {
                    Console.WriteLine($"\nError: No Data Folder Found in {folderPath}"); 
                    return folderNames; // End Function
                }
                
                var directories = Directory.GetDirectories(folderPath); // Get All the Directories in the Folder          
               
                foreach (var directory in directories)  // Iterate through each Folder to see if the Folder Name Matches Search Criteria
                {
                    var folderName = Path.GetFileName(directory); // Check if the Folder Starts with Any of the Required Prefixes
                    
                    if (string.IsNullOrEmpty(folderName)) // Skip if folder name is null or empty
                        continue;
                    
                    bool matchesPrefix = false; 
                    for (int i = 0; i < namePrefixes.Count; i++) // Loop Through all listed Prefixes
                    {
                        if (folderName.StartsWith(namePrefixes[i]))
                        {
                            matchesPrefix = true;
                            break; // If Match Break Loop
                        }
                    }
                    if (matchesPrefix) // Add it to the Folder Names List
                    {
                        folderNames.Add(folderName);
                    }
                }
                folderNames.Sort(); // Sort the Contents of the List
                if (debugFlag)
                {
                    Console.WriteLine($"\nMetering Data Folders Discovered: {folderNames.Count}");
                }
            }
            catch (UnauthorizedAccessException)
            {
                Console.WriteLine($"Error: Access Denied to Raw Data Folder");
            }
            catch (IOException ex)
            {
                Console.WriteLine($"Error: Function (FetchDataService.ListFolderNames) Exception - {ex.Message} ");
            }
            return folderNames;
        }


        /// <summary>
        /// List all file names matching the given prefix and postfix from child folders.
        /// </summary>
        /// <param name="parentFolderPath">Path to the parent data folder</param>
        /// <param name="childFolderNames">List of child folder names to search</param>
        /// <param name="prefix">File name prefix to match</param>
        /// <param name="postfix">File name postfix to match</param>
        /// <param name="delimiter">Delimiter to separate folder name and file name</param>
        /// <param name="debugFlag">Enable debug output</param>
        /// <returns>Sorted list of file names with folder prefix</returns>
        public static List<string> ListFileNames(string parentFolderPath, List<string> childFolderNames, string prefix, string postfix,
           string delimiter, bool debugFlag)
        {
            var fileNames = new List<string>();
            try
            {
                foreach (var folderName in childFolderNames)
                {
                    // Concatenate the Complete Folder Path
                    string folderPath = Path.Combine(parentFolderPath, folderName);
                    if (!Directory.Exists(folderPath))
                       continue;
                    // Get all Files Names and Store in a String Array
                    string[] files = Directory.GetFiles(folderPath); 
                    // Loop Through Each File to Get all Files Matching Prefix and Postfix Criteria
                    for (int i = 0; i < files.Length; i++)
                    {
                        string? fileName = Path.GetFileName(files[i]);
                        
                        if (string.IsNullOrEmpty(fileName)) // Skip if file name is null or empty
                            continue;
                        
                        // Check if file matches criteria
                        if (fileName.StartsWith(prefix) && fileName.EndsWith(postfix))
                        {
                            fileNames.Add(folderName + delimiter + fileName);
                        }
                    }
                }
            }
            catch (IOException ex)
            {
                Console.WriteLine($"Error: Function (FetchDataService.ListFileNames) Exception - {ex.Message} ");
            }
            return fileNames;
        }


        /// <summary>
        /// List all the Buidling Blocks Numbers (for example, block 82, 84, 86....)
        /// </summary>
        /// <param name="nameList">List of meter names (e.g., ["J_B_82_10_27", "J_B_82_11_28"])</param>
        /// <returns>Sorted list of unique block numbers (e.g., ["82", "84"])</returns>
        public static List<string> ListMeterBlocks(List<string> nameList)
        {
            var blockList = new List<string>();
            foreach (string name in nameList)
            {
                // Split the name by underscore
                // Example: "J_B_82_10_27" → ["J", "B", "82", "10", "27"]
                string[] parts = name.Split('_');     
                if (parts.Length >= 3) // Verify that there is 3 Parts
                {          
                    string blockNumber = parts[2];  // Block Number is the 3rd Element in the Array
                    
                    if(!blockList.Contains(blockNumber)) // Keep only Unique Block Values; Add if not already inside Block List
                    {
                        blockList.Add(blockNumber);
                    }
                }
            }
            return blockList;
        }

        
        /// <summary>
        /// Read raw BTU meter text data and parse into list of data points with diagnostics.
        /// Python equivalent: read_Raw_Text_Data()
        /// </summary>
        /// <param name="filePath">Full path to the text file</param>
        /// <param name="encoding">File encoding (default: "utf-8")</param>
        /// <param name="healthCheck">Whether to check for #start/#stop health markers (default: true)</param>
        /// <param name="debugFlag">Whether to print debug information (default: false)</param>
        /// <returns>Tuple containing (list of data points, diagnostic statistics dictionary)</returns>
        public static (List<MeterDataPoint> data, MeterDiagnosticStatistics stats) ReadTextData(
            string filePath,
            string encoding = "utf-8",
            bool healthCheck = true,
            bool debugFlag = false
        )
        {
            // Initialize Variables
            var rawData = new List<MeterDataPoint>();
            int lineCount = 0;
            bool sensorHealth = true; 
            var timestampFailure = new List<string>();
            var timestampRecovery = new List<string>();
            int corruptedDataLines = 0;
            bool pendingStartMarker = false;
            string meterName = "Unknown";
            string fileName = "Unknown";

            try // Get the Meter and File Names
            {
                meterName = Path.GetFileName(Path.GetDirectoryName(filePath)) ?? "Unknown";
                fileName = Path.GetFileName(filePath) ?? "Unknown";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: Could not extract file/folder names - {ex.Message}");
            }

            // Read Raw Data File Process Begins
            try
            {
                // Check if File Exist First
                if (!File.Exists(filePath))
                {
                    Console.WriteLine($"Error: (FetchDataService.ReadTextData) File Not Found ({filePath})");
                    return (rawData, new MeterDiagnosticStatistics 
                    {
                        MeterName = meterName,
                        FileName = fileName,
                        TotalData = 0,
                        RawLineCount = 0,
                        HealthyData = 0,
                        FaultyData = 0,
                        FaultyDataPercentage = 0.0,
                        FailureTimestamps = timestampFailure,
                        RecoveryTimestamps = timestampRecovery,
                        CorruptedDataLines = 0
                    });
                }
                
                // Read Line by Line (Use 'Using' - Automatically Close File and Reader Resouses)
                using (var reader = new StreamReader(filePath, System.Text.Encoding.GetEncoding(encoding)))
                {
                    string? line;
                    while ((line = reader.ReadLine()) != null)
                    {
                        line = line.Trim();
                        lineCount++;   
                        if (healthCheck) // Check Health Markers if Enabled
                        {
                            // '#stop' indicates meter went offline
                            if (line == "#stop")
                            {
                                // Capture the last Healthy Datapoint Timestamp before #stop // Format the Timestamp to ISO Format
                                if (rawData.Count > 0 && rawData[rawData.Count - 1].IsHealthy)
                                {
                                    try { timestampFailure.Add(rawData[rawData.Count - 1].Timestamp.ToString("yyyy-MM-dd HH:mm:ss"));}
                                    catch {  } // Ignore any Formatting Errors
                                }
                                sensorHealth = false;
                                if (debugFlag) {Console.WriteLine($"Line {lineCount}: Sensor Unhealthy (#stop)");}
                                continue;
                            }
                            // '#start' indicates meter came online
                            else if (line == "#start") 
                            {
                                sensorHealth = true;
                                pendingStartMarker = true; 
                                if (debugFlag) {Console.WriteLine($"Line {lineCount}: Sensor Healthy (#start)");}
                                continue;
                            }
                        }

                        // Skip Empty Lines or Other Comments
                        if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#")) { continue; }

                        // Parse Data Process
                        // Raw Format: "01.10.2025 00:00:00 9006.741"
                        try
                        {
                            // Split the Data Line by the Whitespaces
                            string[] dataSegment = line.Split(new[] {' '}, StringSplitOptions.RemoveEmptyEntries);

                            // Check for Date and Time
                            if (dataSegment.Length >= 2)
                            {
                                // Extract timestamp components
                                string dateString = dataSegment[0];      // "01.10.2025"
                                string timeString = dataSegment[1];      // "00:00:00"
                                string timestampString = $"{dateString} {timeString}";

                                // Parse timestamp into ISO format (DD.MM.YYYY HH:mm:ss format)
                                DateTime timestampISO;
                                try
                                {
                                    timestampISO = DateTime.ParseExact(timestampString,"dd.MM.yyyy HH:mm:ss", CultureInfo.InvariantCulture);
                                }
                                catch (FormatException)
                                {
                                        corruptedDataLines++;
                                        if (debugFlag)  { Console.WriteLine($"Skipping line {lineCount}: Invalid timestamp format ({timestampString})"); }
                                        continue;
                                }

                                // Extract Process Value (3rd Element)
                                double processValue = 0.0;
                                if (dataSegment.Length >= 3)
                                {
                                    try
                                    {
                                        processValue = double.Parse(dataSegment[2], CultureInfo.InvariantCulture);
                                    }
                                    catch
                                    {  
                                        if (debugFlag)
                                           Console.WriteLine($"Error: Line {lineCount} cannot be parsed");
                                    }
                                }
          
                                if (!sensorHealth) { processValue = 0.0; }   // If sensor is unhealthy, force value to 0.0
                                
                                // Capture recovery timestamp (first healthy datapoint after #start)
                                if (pendingStartMarker && sensorHealth)
                                {
                                    try { timestampRecovery.Add(timestampISO.ToString("yyyy-MM-dd HH:mm:ss")); }
                                    catch { } // Ignore timestamp formatting errors
                                    pendingStartMarker = false;
                                }
                                
                                // Add data point to list
                                rawData.Add(new MeterDataPoint
                                {
                                    Timestamp = timestampISO,
                                    Value = processValue,
                                    IsHealthy = sensorHealth
                                });
                                
                            }
                        }
                        catch (Exception ex)
                        {
                            corruptedDataLines++; 
                            if (debugFlag) { Console.WriteLine($"Error: Skipping line {lineCount} - {ex.Message}"); }
                        }
                    }
                }

            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: (FetchDataService.ReadTextData) Exception - {ex.Message}");
            }
            
            // Calculate the Raw Data Statistics
            int totalData = rawData.Count;
            int totalHealthyData = 0;
            int totalFaultyData = 0;
            double faultyDataPercentage = 0.0;
            
            try
            {
                totalHealthyData = rawData.Count(d => d.IsHealthy);
                totalFaultyData = totalData - totalHealthyData;
                if (totalData > 0 && totalFaultyData > 0) { faultyDataPercentage = Math.Round((double)totalFaultyData/totalData*100, 2); }
                else { faultyDataPercentage = 0.0; }

            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Error calculating statistics - {ex.Message}");
            }
            
            // Build diagnostic statistics
            var diagnosticStatistics = new MeterDiagnosticStatistics 
            {
                MeterName = meterName,
                FileName = fileName,
                TotalData = totalData,
                RawLineCount = lineCount,
                HealthyData = totalHealthyData,
                FaultyData = totalFaultyData,
                FaultyDataPercentage = faultyDataPercentage,
                FailureTimestamps = timestampFailure,
                RecoveryTimestamps = timestampRecovery,
                CorruptedDataLines = corruptedDataLines
            };
            
            // Print debug information if enabled
            if (debugFlag)
            {
                Console.WriteLine($"\nMeter: {meterName} (File: {fileName})");
                Console.WriteLine($"Number of Datapoints: {totalData} (Raw Number of Lines: {lineCount})");
                Console.WriteLine($"Total Healthy Datapoints: {totalHealthyData}  |  Total Unhealthy Datapoints: {totalFaultyData}");
                Console.WriteLine($"Faulty Data Percentage: {faultyDataPercentage}%  |  Total Corrupted Data Lines: {corruptedDataLines}");
                Console.WriteLine($"Sensor Failure Times: {string.Join(", ", timestampFailure)}");
                Console.WriteLine($"Sensor Recovery Times: {string.Join(", ", timestampRecovery)}");
            }
            
            return (rawData, diagnosticStatistics);

        }
    }
}