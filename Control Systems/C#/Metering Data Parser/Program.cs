
// Project: Metering Data Parser
// File: Program.cs
// Description: Main Program File that runs the Metering Data Parser Process. 
//              Use to process multiple raw data stored in text files (each 44640 data lines) and
//              compiles them into Excel Files and calculates the Billing Information.
// 
// Author: Tristan Sim
// Date: 18/11/2025
// Version: 1.0

using System; 
using System.IO;
using System.Linq;
using System.Collections.Generic;
using MeteringDataParser.Services;

namespace MeteringDataParser
{
    class Program
    {   

        // Program Configurations (Constants Variables - Fixed at Compile Time)
        private const string PATH_DATA_FOLDER = @"C:\Repository\ControlSystems\Control Systems\C#\Metering Data Parser\Data\Actual Data"; 
        private const string PATH_OUTPUT_FOLDER = @"C:\Repository\ControlSystems\Control Systems\C#\Metering Data Parser\Output\Metering Summary Report";
        private const string DELIMITER = ";"; 
        private const bool DEBUG_FLAG = true;
        private const int NUMBER_OF_CORES = 10;  // Computer must have at least 10 cores


        // (Static Variables - One Variable that is shared accross Instances & Is Not Fixed During Compile Time(Mutable))
        private static string targetMonth = "10";
        private static string targetYear = "2025";
        private static List<string> meterNamePrefix = new List<string> {"J_B_"};
        private static List<string> dataFilePrefix = new List<string> {"X01_01_"};
        private static List<string> dataFilePostfix = new List<string> {"BTUREADINGS11MIN.txt", "ACCBTUReadingS11MIN.txt"};
        private static List<string> blockNumbers = new List<string> {"80", "82", "84", "86", "88", "90", "92", "94", "96", "98"};



        static void Main(string[] args)
        {   
            // Process 1: Fetch Available Data Folders
            Console.WriteLine($"\nProcess 1: Fetch Available Data Folders ----------------------------------------------------------------------------- ");
            Console.WriteLine($"\nTarget Processing Month: {targetMonth}    |   Target Processing Year: {targetYear}");
            
            // Listing all Meter Folder Names & Block Numbers
            List<string> meterNameList = FetchDataService.ListFolderNames(folderPath: PATH_DATA_FOLDER, namePrefixes: meterNamePrefix, DEBUG_FLAG);
            List<string> discoveredBlockList = FetchDataService.ListMeterBlocks(meterNameList);

            if (DEBUG_FLAG)
            {
                Console.WriteLine($"\n{discoveredBlockList.Count} Building Blocks Discovered: ");
                foreach (var block in discoveredBlockList) { Console.WriteLine($"- Block {block}"); }
            }
            
            // Build search criteria for file names
            string prefixSearchCriteria = dataFilePrefix[0] + targetYear + targetMonth;
            // Console.WriteLine($"\nSearching for files with prefix: '{prefixSearchCriteria}'");

            // Create a List with all the RT File Data
            List<string> meterFileList_RT = FetchDataService.ListFileNames(
                parentFolderPath: PATH_DATA_FOLDER,
                childFolderNames: meterNameList,
                prefix: prefixSearchCriteria,
                postfix: dataFilePostfix[0],
                delimiter: DELIMITER,
                debugFlag: DEBUG_FLAG
            );

            // Create a List with all the RTH (Accumulated) File Data
            List<string> meterFileList_RTH = FetchDataService.ListFileNames(
                parentFolderPath: PATH_DATA_FOLDER,
                childFolderNames: meterNameList,
                prefix: prefixSearchCriteria,
                postfix: dataFilePostfix[1],
                delimiter: DELIMITER,
                debugFlag: DEBUG_FLAG
            );~

            Console.WriteLine($"\nNumber of RT Files Retrieved: {meterFileList_RT.Count}   |   Number of RTH Files Retrieved: {meterFileList_RT.Count}");

            Console.WriteLine($"\nProcess 1: Completed ------------------------------------------------------------------------------------------------- ");





            // Process 2: Load Data from Text File Parse into an Array (Clean Data)
            Console.WriteLine($"\n\nProcess 2: Load Data from Text File and Parse into an Array (Clean Data) ---------------------------------------------- ");

            



            


            Console.WriteLine($"\nProcess 2: Completed ------------------------------------------------------------------------------------------------- ");

            // Step 3: Analyze and Process the Data into Required Output 
            Console.WriteLine($"\n\nProcess 3: Analyze and Process the Data into Required Output --------------------------------------------------------- ");
            Console.WriteLine($"\nProcess 3: Completed ------------------------------------------------------------------------------------------------- ");

            // Step 4: Save a Data into invidual Excel Files by Blocks (Sheet: Summary, RT, RTH) 'Block_88_Oct_2025'
            Console.WriteLine($"\n\nProcess 4: Save a Data into invidual Excel Files by Blocks ----------------------------------------------------------- ");
            Console.WriteLine($"\nProcess 4: Completed ------------------------------------------------------------------------------------------------- ");

        }

    }
}