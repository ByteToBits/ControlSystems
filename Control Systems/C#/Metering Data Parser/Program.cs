
using System; 
using System.IO;
using System.Linq;
using System.Collections.Generic;

namespace MeteringDataParser
{
    class Program
    {   

        // Program Configurations (Constants Variables - Fixed at Compile Time)
        private const string PATH_DATA_FOLDER = @"C:\Repository\ControlSystems\Control Systems\C#\Metering Data Parser\Data\Actual Data"; 
        private const string PATH_OUTPUT_FOLDER = @"C:\Repository\ControlSystems\Control Systems\C#\Metering Data Parser\Output\Metering Summary Report";
        private const string DELIMTER = ";"; 
        private const bool DEBUG_FLAG = true;
        private const int NUMBER_OF_CORES = 10;  // Computer must have at least 10 cores


        // (Static Variables - One Variable that is shared accross Instances & Is Not Fixed During Compile Time(Mutable))
        private static string targetMonth = "10";
        private static string targetYear = "2025";
        private static List<string> meterNamePrefix = new List<string> {"J_B_"};
        private static List<string> dataFilePrefix = new List<string> {"X01_01_"};
        private static List<string> dataFilePostfix = new List<string> {"BTUREADINGS11MIN.txt", "ACCBTUReadingS11MIN.txt"};
        private static List<string> blockNumbers = new List<string> {"80", "82", "84", "86", "88", "90", "92", "94", "96", "98"};



        // Main Program
        static void Main(string[] args)
        {
            Console.WriteLine("Process 1: Fetch Data from Raw Data Files");

        }

    }
}