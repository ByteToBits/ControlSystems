// Project: Metering Data Parser
// File: BlockData.cs
// Description: Container for block raw data and statistics
// 
// Author: Tristan Sim
// Date: 18/11/2025
// Version: 1.0

using System;
using System.Collections.Generic;
using MeteringDataParser.Models;

namespace MeteringDataParser.Models
{
    public class BlockData
    {
        // Block Identity
        public string BlockNumber { get; set; }
        public string TargetMonth { get; set; }
        public string TargetYear { get; set; }
        
        // Raw data storage (either RT or RTH, not both simultaneously)
        public Dictionary<string, List<MeterDataPoint>> MeterData { get; set; }
        
        // Statistics (always kept)
        public BlockStatistics Statistics { get; set; }
        
        // Constructor
        public BlockData(string blockNumber, string month, string year)
        {
            BlockNumber = blockNumber;
            TargetMonth = month;
            TargetYear = year;
            MeterData = new Dictionary<string, List<MeterDataPoint>>();
            Statistics = new BlockStatistics(blockNumber);
        }
        
        // Clear raw data to free memory
        public void ClearRawData()
        {
            MeterData.Clear();
            MeterData = null;
            GC.Collect();
            GC.WaitForPendingFinalizers();
        }
    }
}