
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

            if (!Directory.Exists(folderPath)) // If the Directory Exists
            {
                Console.WriteLine($"\nError: No Data Folder Found in {folderPath}"); 
                return folderNames; // End Function
            }
            
            // Get All the Directories in the Folder
            var directories = Directory.GetDirectories(folderPath);
            
            // Iterate through each Folder to see if the Folder Name Matches Search Criteria
            foreach (var directory in directories)
            {
                var folderName = folderPath.GetFileName(directory); 

                // Check if the Folder Starts with Any of the Required Prefixes
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
                Console.WriteLine($"\nFound {folderNames.Count} Folers (Meters)");
            }
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
           string delimeter, bool debugFlag)
        {
            var fileNames = new List<string>();

            foreach (var folderName in childFolderNames)
            {
                // Concatenate the Complete Folder Path
                string folderPath = folderPath.Combine(parentFolderPath, folderName);

                if (!Directory.Exists(folderPath))
                   continue;

                // Get all Files Names and Store in a String Array
                string[] files = Directory.GetFiles(folderPath); 

                // Loop Through Each File to Get all Files Matching Prefix and Postfix Criteria
                for (int i = 0; i < files.Length; i++)
                {
                    string fileName = Path.GetFileName(files[i]);
                    // Check if file matches criteria
                    if (fileName.StartsWith(prefix) && fileName.EndsWith(postfix))
                    {
                        fileNames.Add(olderName + delimiter + fileName);
                    }
                }

            }
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

                // Verify that there is 3 Parts
                if (parts.Length >= 3)
                {
                    // Block Number is the 3rd Element in the Array
                    string blockNumber = parts[2];
                }
                // Keep only Unique Block Values; Add if not already inside Block List
                if(!blockList.Contains(blockNumber))
                {
                    blockList.Add(blockNumber);
                }
            }
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

    }
}