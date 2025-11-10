import pandas as pd
from datetime import datetime
from calendar import monthrange

targetMonth = '10'
targetYear = '2025'

def initialize_DataFrame(targetMonth: str, targetYear: str):
    """
    Initialize a DataFrame for metering data with 1-minute interval timestamps  for the specified month.
    Args:
        targetMonth: Month as string ('10' for October)
        targetYear: Year as string ('2025')
    Returns:
        DataFrame with timestamp, date, and time columns at 1-minute intervals
    """
    
    month = int(targetMonth)
    year = int(targetYear)
    
    # Get the first day of the target month at 00:00:00
    first_day = datetime(year, month, 1, 0, 0, 0)
    
    # Get the last day of the month
    last_day_num = monthrange(year, month)[1]
    
    # Get the last timestamp of the month (23:59:00)
    last_moment = datetime(year, month, last_day_num, 23, 59, 0)
    
    # Create timestamp range with 1-minute intervals
    timestamps = pd.date_range(start = first_day, end = last_moment, freq = '1T')
    
    # Create DataFrame
    df = pd.DataFrame({'timestamp': timestamps})
    
    # Create timestamp and a separate date and time columns
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')
    df = df[['timestamp', 'date', 'time']] # Reorder columns
    
    return df
