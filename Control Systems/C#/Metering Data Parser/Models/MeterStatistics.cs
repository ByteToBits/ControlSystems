// Project: Metering Data Parser
// File: BlockStatistics.cs
// Description: Block-level aggregated statistics
// 
// Author: Tristan Sim
// Date: 18/11/2025
// Version: 1.0

using System;

namespace MeteringDataParser.Models
{
    public class MeterStatistics
    {
        public string MeterName { get; set; }
        public string BlockNumber { get; set; }
        
        // RT Statistics
        public double RT_TotalizedValue { get; set; }
        public double RT_AverageValue { get; set; }
        public double RT_OperatingHours { get; set; }
        public int RT_HealthyDataPoints { get; set; }
        public int RT_FaultyDataPoints { get; set; }
        public int RT_TotalDataPoints { get; set; }
        public double RT_DataCompletenessPercentage { get; set; }
        
        // RTH Statistics
        public double RTH_FirstHealthyValue { get; set; }
        public DateTime RTH_FirstHealthyTimestamp { get; set; }
        public double RTH_LastHealthyValue { get; set; }
        public DateTime RTH_LastHealthyTimestamp { get; set; }
        public double RTH_MonthlyConsumption { get; set; }
        public double RTH_TotalizedValue { get; set; }
        public int RTH_HealthyDataPoints { get; set; }
        public int RTH_FaultyDataPoints { get; set; }
        public int RTH_TotalDataPoints { get; set; }
        public double RTH_DataCompletenessPercentage { get; set; }
        
        public MeterStatistics()
        {
            MeterName = string.Empty;
            BlockNumber = string.Empty;
            RTH_FirstHealthyTimestamp = DateTime.MinValue;
            RTH_LastHealthyTimestamp = DateTime.MinValue;
        }
    }
}