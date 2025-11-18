// Models/MeterDiagnosticStatistics.cs
public class MeterDiagnosticStatistics
{
    public string MeterName { get; set; }
    public string FileName { get; set; }
    public int TotalData { get; set; }
    public int RawLineCount { get; set; }
    public int HealthyData { get; set; }
    public int FaultyData { get; set; }
    public double FaultyDataPercentage { get; set; }
    public List<string> FailureTimestamps { get; set; }
    public List<string> RecoveryTimestamps { get; set; }
    public int CorruptedDataLines { get; set; }
    
    // Constructor - initialize all properties
    public MeterDiagnosticStatistics()
    {
        MeterName = string.Empty;       
        FileName = string.Empty;        
        FailureTimestamps = new List<string>();
        RecoveryTimestamps = new List<string>();
    }
}