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
    /// <summary>
    /// Represents a single meter data point with timestamp, value, and health status
    /// </summary>
    public class MeterDataPoint
    {
        public DateTime Timestamp { get; set; }
        public double Value { get; set; }
        public bool IsHealthy { get; set; }
    }
}