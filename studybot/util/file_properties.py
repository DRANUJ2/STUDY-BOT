import os
import mimetypes
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

def get_file_properties(file_path: str) -> Dict[str, Any]:
    """
    Get comprehensive file properties
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Dict[str, Any]: Dictionary containing file properties
    """
    try:
        path = Path(file_path)
        stat = path.stat()
        
        properties = {
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'size': stat.st_size,
            'size_human': human_readable_size(stat.st_size),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'exists': path.exists(),
            'absolute': str(path.absolute()),
            'parent': str(path.parent),
            'mime_type': get_mime_type(file_path),
            'hash': get_file_hash(file_path),
            'permissions': oct(stat.st_mode)[-3:],
            'owner': stat.st_uid,
            'group': stat.st_gid
        }
        
        return properties
        
    except (OSError, IOError) as e:
        return {
            'error': str(e),
            'exists': False
        }

def get_mime_type(file_path: str) -> str:
    """
    Get MIME type of file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: MIME type string
    """
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        
        # Fallback for common file extensions
        ext = Path(file_path).suffix.lower()
        mime_map = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json',
            '.xml': 'application/xml'
        }
        
        return mime_map.get(ext, 'application/octet-stream')
        
    except Exception:
        return 'application/octet-stream'

def get_file_hash(file_path: str, algorithm: str = 'md5', chunk_size: int = 8192) -> str:
    """
    Calculate file hash
    
    Args:
        file_path (str): Path to the file
        algorithm (str): Hash algorithm (md5, sha1, sha256)
        chunk_size (int): Chunk size for reading file
        
    Returns:
        str: Hexadecimal hash string
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception:
        return ''

def human_readable_size(size_bytes: int) -> str:
    """
    Convert bytes to human readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Human readable size string
    """
    from .human_readable import humanbytes
    return humanbytes(size_bytes)

def get_file_extension(file_path: str) -> str:
    """
    Get file extension
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File extension (with dot)
    """
    return Path(file_path).suffix.lower()

def is_video_file(file_path: str) -> bool:
    """
    Check if file is a video file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is a video
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp', '.ogv'}
    return get_file_extension(file_path) in video_extensions

def is_audio_file(file_path: str) -> bool:
    """
    Check if file is an audio file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is an audio
    """
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.amr'}
    return get_file_extension(file_path) in audio_extensions

def is_image_file(file_path: str) -> bool:
    """
    Check if file is an image file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is an image
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'}
    return get_file_extension(file_path) in image_extensions

def is_document_file(file_path: str) -> bool:
    """
    Check if file is a document file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is a document
    """
    document_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'}
    return get_file_extension(file_path) in document_extensions

def is_archive_file(file_path: str) -> bool:
    """
    Check if file is an archive file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is an archive
    """
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lzma'}
    return get_file_extension(file_path) in archive_extensions

def get_file_category(file_path: str) -> str:
    """
    Get file category based on extension
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File category
    """
    if is_video_file(file_path):
        return 'video'
    elif is_audio_file(file_path):
        return 'audio'
    elif is_image_file(file_path):
        return 'image'
    elif is_document_file(file_path):
        return 'document'
    elif is_archive_file(file_path):
        return 'archive'
    else:
        return 'other'

def format_file_date(timestamp: float) -> str:
    """
    Format file date timestamp
    
    Args:
        timestamp (float): Unix timestamp
        
    Returns:
        str: Formatted date string
    """
    from .time_format import format_datetime
    return format_datetime(int(timestamp), "%Y-%m-%d %H:%M:%S")

def get_file_info_summary(file_path: str) -> str:
    """
    Get a summary of file information
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Formatted file information summary
    """
    props = get_file_properties(file_path)
    
    if 'error' in props:
        return f"❌ Error: {props['error']}"
    
    summary = f"📁 **File Information**\n\n"
    summary += f"📝 **Name:** {props['name']}\n"
    summary += f"📏 **Size:** {props['size_human']}\n"
    summary += f"🔗 **Type:** {props['mime_type']}\n"
    summary += f"📅 **Modified:** {format_file_date(props['modified'])}\n"
    summary += f"🏷️ **Category:** {get_file_category(file_path).title()}"
    
    return summary
