import time
from datetime import datetime, timedelta

def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to human readable time format
    
    Args:
        seconds (int): Time in seconds
        
    Returns:
        str: Human readable time string
    """
    if seconds < 0:
        return "Invalid time"
    
    if seconds == 0:
        return "0 seconds"
    
    time_units = [
        ("year", 365 * 24 * 60 * 60),
        ("month", 30 * 24 * 60 * 60),
        ("week", 7 * 24 * 60 * 60),
        ("day", 24 * 60 * 60),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1)
    ]
    
    parts = []
    for unit_name, unit_seconds in time_units:
        if seconds >= unit_seconds:
            unit_value = seconds // unit_seconds
            seconds = seconds % unit_seconds
            
            if unit_value == 1:
                parts.append(f"1 {unit_name}")
            else:
                parts.append(f"{unit_value} {unit_name}s")
    
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{', '.join(parts[:-1])}, and {parts[-1]}"

def get_time_difference(timestamp1: int, timestamp2: int = None) -> str:
    """
    Get time difference between two timestamps
    
    Args:
        timestamp1 (int): First timestamp
        timestamp2 (int, optional): Second timestamp (defaults to current time)
        
    Returns:
        str: Human readable time difference
    """
    if timestamp2 is None:
        timestamp2 = int(time.time())
    
    diff = abs(timestamp2 - timestamp1)
    return get_readable_time(diff)

def format_duration(seconds: int) -> str:
    """
    Format duration in HH:MM:SS format
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 0:
        return "00:00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_relative_time(timestamp: int) -> str:
    """
    Get relative time (e.g., "2 hours ago", "yesterday")
    
    Args:
        timestamp (int): Timestamp to compare
        
    Returns:
        str: Relative time string
    """
    now = int(time.time())
    diff = now - timestamp
    
    if diff < 0:
        return "in the future"
    
    if diff < 60:
        return "just now"
    elif diff < 3600:
        minutes = diff // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < 86400:
        hours = diff // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < 172800:
        return "yesterday"
    elif diff < 259200:
        return "2 days ago"
    elif diff < 604800:
        days = diff // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif diff < 2592000:
        weeks = diff // 604800
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif diff < 31536000:
        months = diff // 2592000
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = diff // 31536000
        return f"{years} year{'s' if years != 1 else ''} ago"

def get_time_ago(timestamp: int) -> str:
    """
    Alias for get_relative_time for backward compatibility
    
    Args:
        timestamp (int): Timestamp to compare
        
    Returns:
        str: Relative time string
    """
    return get_relative_time(timestamp)

def format_datetime(timestamp: int, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp to datetime string
    
    Args:
        timestamp (int): Timestamp to format
        format_str (str): Format string for datetime
        
    Returns:
        str: Formatted datetime string
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime(format_str)
    except (ValueError, OSError):
        return "Invalid timestamp"

def get_current_timestamp() -> int:
    """
    Get current timestamp
    
    Returns:
        int: Current timestamp
    """
    return int(time.time())

def is_today(timestamp: int) -> bool:
    """
    Check if timestamp is from today
    
    Args:
        timestamp (int): Timestamp to check
        
    Returns:
        bool: True if timestamp is from today
    """
    now = datetime.now()
    dt = datetime.fromtimestamp(timestamp)
    return now.date() == dt.date()

def is_yesterday(timestamp: int) -> bool:
    """
    Check if timestamp is from yesterday
    
    Args:
        timestamp (int): Timestamp to check
        
    Returns:
        bool: True if timestamp is from yesterday
    """
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    dt = datetime.fromtimestamp(timestamp)
    return yesterday.date() == dt.date()

def get_week_start(timestamp: int = None) -> int:
    """
    Get start of week timestamp
    
    Args:
        timestamp (int, optional): Timestamp to get week start for (defaults to current time)
        
    Returns:
        int: Start of week timestamp
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    dt = datetime.fromtimestamp(timestamp)
    week_start = dt - timedelta(days=dt.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(week_start.timestamp())

def get_month_start(timestamp: int = None) -> int:
    """
    Get start of month timestamp
    
    Args:
        timestamp (int, optional): Timestamp to get month start for (defaults to current time)
        
    Returns:
        int: Start of month timestamp
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    dt = datetime.fromtimestamp(timestamp)
    month_start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return int(month_start.timestamp())
