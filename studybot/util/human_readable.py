def humanbytes(B):
    """
    Convert bytes to human readable format
    
    Args:
        B (int): Size in bytes
        
    Returns:
        str: Human readable size string
    """
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)
    
    if B < KB:
        return f"{B:.2f} B"
    elif KB <= B < MB:
        return f"{B/KB:.2f} KB"
    elif MB <= B < GB:
        return f"{B/MB:.2f} MB"
    elif GB <= B < TB:
        return f"{B/GB:.2f} GB"
    else:
        return f"{B/TB:.2f} TB"

def humanbytes_alt(B):
    """
    Alternative human readable bytes converter
    
    Args:
        B (int): Size in bytes
        
    Returns:
        str: Human readable size string
    """
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)
    PB = float(KB ** 5)
    
    if B < KB:
        return f"{B:.1f} B"
    elif KB <= B < MB:
        return f"{B/KB:.1f} KB"
    elif MB <= B < GB:
        return f"{B/MB:.1f} MB"
    elif GB <= B < TB:
        return f"{B/GB:.1f} GB"
    elif TB <= B < PB:
        return f"{B/TB:.1f} TB"
    else:
        return f"{B/PB:.1f} PB"

def humanbytes_simple(B):
    """
    Simple human readable bytes converter
    
    Args:
        B (int): Size in bytes
        
    Returns:
        str: Human readable size string
    """
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    
    if B < KB:
        return f"{B:.0f} B"
    elif KB <= B < MB:
        return f"{B/KB:.0f} KB"
    elif MB <= B < GB:
        return f"{B/MB:.0f} MB"
    else:
        return f"{B/GB:.1f} GB"

def humanbytes_compact(B):
    """
    Compact human readable bytes converter
    
    Args:
        B (int): Size in bytes
        
    Returns:
        str: Compact human readable size string
    """
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)
    
    if B < KB:
        return f"{B:.0f}B"
    elif KB <= B < MB:
        return f"{B/KB:.0f}K"
    elif MB <= B < GB:
        return f"{B/MB:.0f}M"
    elif GB <= B < TB:
        return f"{B/GB:.1f}G"
    else:
        return f"{B/TB:.1f}T"

def humanbytes_precise(B, precision=2):
    """
    Precise human readable bytes converter
    
    Args:
        B (int): Size in bytes
        precision (int): Decimal precision
        
    Returns:
        str: Precise human readable size string
    """
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)
    PB = float(KB ** 5)
    EB = float(KB ** 6)
    
    if B < KB:
        return f"{B:.{precision}f} B"
    elif KB <= B < MB:
        return f"{B/KB:.{precision}f} KB"
    elif MB <= B < GB:
        return f"{B/MB:.{precision}f} MB"
    elif GB <= B < TB:
        return f"{B/GB:.{precision}f} GB"
    elif TB <= B < PB:
        return f"{B/TB:.{precision}f} TB"
    elif PB <= B < EB:
        return f"{B/PB:.{precision}f} PB"
    else:
        return f"{B/EB:.{precision}f} EB"

def humanbytes_smart(B):
    """
    Smart human readable bytes converter that chooses appropriate precision
    
    Args:
        B (int): Size in bytes
        
    Returns:
        str: Smart human readable size string
    """
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)
    
    if B < KB:
        return f"{B:.0f} B"
    elif KB <= B < MB:
        if B/KB < 10:
            return f"{B/KB:.1f} KB"
        else:
            return f"{B/KB:.0f} KB"
    elif MB <= B < GB:
        if B/MB < 10:
            return f"{B/MB:.1f} MB"
        else:
            return f"{B/MB:.0f} MB"
    elif GB <= B < TB:
        if B/GB < 10:
            return f"{B/GB:.2f} GB"
        else:
            return f"{B/GB:.1f} GB"
    else:
        return f"{B/TB:.2f} TB"

# Alias for backward compatibility
humanbytes = humanbytes_smart
