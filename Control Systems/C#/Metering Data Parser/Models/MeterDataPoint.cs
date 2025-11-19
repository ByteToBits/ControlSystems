// Project: Metering Data Parser
// File: MeterDataPoint.cs
// Description: Data model for individual meter readings
// 
// Author: Tristan Sim
// Date: 18/11/2025
// Version: 1.0

using System;

namespace MeteringDataParser.Models
{
    public struct MeterDataPoint
    {
        public DateTime Timestamp { get; set; }
        public double Value { get; set; }
        public bool IsHealthy { get; set; }
        
        // Constructor for easy creation
        public MeterDataPoint(DateTime timestamp, double value, bool isHealthy)
        {
            Timestamp = timestamp;
            Value = value;
            IsHealthy = isHealthy;
        }
    }
}