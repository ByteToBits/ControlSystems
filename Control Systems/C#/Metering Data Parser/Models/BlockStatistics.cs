// Project: Metering Data Parser
// File: BlockStatistics.cs
// Description: Block-level aggregated statistics
// 
// Author: Tristan Sim
// Date: 18/11/2025
// Version: 1.0

using System.Collections.Generic;

namespace MeteringDataParser.Models
{
    public class BlockStatistics
    {
        public string BlockNumber { get; set; }
        public int NumberOfMeters { get; set; }
        
        // Block RT Aggregates
        public double Block_RT_TotalizedValue { get; set; }
        public double Block_RT_AverageValue { get; set; }
        public double Block_RT_TotalOperatingHours { get; set; }
        public int Block_RT_TotalHealthyDataPoints { get; set; }
        public int Block_RT_TotalFaultyDataPoints { get; set; }
        public double Block_RT_DataCompletenessPercentage { get; set; }
        
        // Block RTH Aggregates
        public double Block_RTH_MonthlyConsumption { get; set; }
        public double Block_RTH_TotalizedValue { get; set; }
        public int Block_RTH_TotalHealthyDataPoints { get; set; }
        public int Block_RTH_TotalFaultyDataPoints { get; set; }
        public double Block_RTH_DataCompletenessPercentage { get; set; }
        
        // Individual Meter Statistics (kept in memory)
        public Dictionary<string, MeterStatistics> MeterStatistics { get; set; }
        
        public BlockStatistics(string blockNumber)
        {
            BlockNumber = blockNumber;
            MeterStatistics = new Dictionary<string, MeterStatistics>();
        }
    }
}