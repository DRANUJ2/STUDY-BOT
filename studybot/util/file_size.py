def get_file_size(file_path):
    """
    Get file size in bytes
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: File size in bytes, -1 if error
    """
    try:
        import os
        return os.path.getsize(file_path)
    except (OSError, IOError):
        return -1

def get_file_size_str(file_path):
    """
    Get file size as human readable string
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Human readable file size
    """
    from .human_readable import humanbytes
    
    size = get_file_size(file_path)
    if size == -1:
        return "Unknown"
    return humanbytes(size)

def is_file_size_valid(file_path, max_size=None):
    """
    Check if file size is within valid range
    
    Args:
        file_path (str): Path to the file
        max_size (int, optional): Maximum allowed size in bytes
        
    Returns:
        bool: True if file size is valid
    """
    size = get_file_size(file_path)
    if size == -1:
        return False
    
    if max_size is not None:
        return size <= max_size
    
    return True
