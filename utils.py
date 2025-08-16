import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class temp:
    """Temporary storage for bot data"""
    # Basic bot info
    ME = None
    U_NAME = None
    B_NAME = None
    B_LINK = None
    
    # Study bot specific temp data
    BANNED_CHATS = set()  # Set of banned chat IDs
    
    # File upload tracking
    FILE_UPLOADS = {}
    
    # Broadcast state
    BROADCAST_STATE = {}
    
    # Index state
    CANCEL = False
    
    # Edit states
    EDIT_BAN_REASON = {}
    
    # Join request state
    ORIGINAL_JOIN_REQUEST_MESSAGE = None
    
    # Welcome message tracking
    MELCOW = {}
    
    START_TIME = time.time()
    
    # Study bot specific temp data
    USER_SESSIONS = {}  # Store user study sessions
    BATCH_CACHE = {}    # Cache batch information
    CONTENT_CACHE = {}  # Cache content data

def get_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def get_elapsed_time(start_time: float) -> str:
    """Get elapsed time since start"""
    elapsed = time.time() - start_time
    return format_time(int(elapsed))

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a progress bar string"""
    filled = int(length * current // total)
    bar = "█" * filled + "░" * (length - filled)
    percentage = (current / total) * 100
    return f"{bar} {percentage:.1f}%"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200-len(ext)-1] + '.' + ext if ext else name[:200]
    
    return filename

def parse_filename_pattern(filename: str) -> Dict[str, str]:
    """Parse filename pattern to extract study information"""
    # Expected pattern: {Batch Name}{Subject}{Teacher name}{Chapter No.}{Lecture No.}{NOTES}{DPP}{other materials}
    pattern = {}
    
    # Split by common separators
    parts = filename.replace('_', ' ').replace('-', ' ').split()
    
    if len(parts) >= 4:
        # Try to identify components
        for i, part in enumerate(parts):
            if part.upper() in ['PHYSICS', 'CHEMISTRY', 'BIOLOGY']:
                pattern['subject'] = part
            elif part.upper() in ['MR', 'SALEEM']:
                pattern['teacher'] = part
            elif part.upper().startswith('CH') and len(part) >= 3:
                pattern['chapter_no'] = part
            elif part.upper().startswith('L') and len(part) >= 2:
                pattern['lecture_no'] = part
            elif part.upper() in ['NOTES', 'DPP', 'LECTURE']:
                pattern['content_type'] = part
    
    return pattern

def generate_achievement(user_stats: Dict) -> Optional[str]:
    """Generate achievement based on user statistics"""
    achievements = []
    
    # Study time achievements
    if user_stats.get('total_time_spent', 0) >= 60:
        achievements.append("⏰ First Hour - Studied for 1 hour")
    if user_stats.get('total_time_spent', 0) >= 300:
        achievements.append("📚 Study Warrior - Studied for 5 hours")
    if user_stats.get('total_time_spent', 0) >= 600:
        achievements.append("🎓 Study Master - Studied for 10 hours")
    
    # Download achievements
    if user_stats.get('total_downloads', 0) >= 10:
        achievements.append("📥 Downloader - Downloaded 10 files")
    if user_stats.get('total_downloads', 0) >= 50:
        achievements.append("📚 File Collector - Downloaded 50 files")
    if user_stats.get('total_downloads', 0) >= 100:
        achievements.append("🏆 Content Master - Downloaded 100 files")
    
    # Subject completion achievements
    subjects_completed = len(user_stats.get('study_progress', {}))
    if subjects_completed >= 3:
        achievements.append("🧪 Subject Explorer - Studied 3 subjects")
    if subjects_completed >= 5:
        achievements.append("📖 Knowledge Seeker - Studied 5 subjects")
    
    return achievements[-1] if achievements else None

def calculate_study_score(user_stats: Dict) -> int:
    """Calculate study score based on user activity"""
    score = 0
    
    # Time spent (1 point per minute)
    score += user_stats.get('total_time_spent', 0)
    
    # Downloads (10 points per download)
    score += user_stats.get('total_downloads', 0) * 10
    
    # Subject variety (50 points per subject)
    subjects = len(user_stats.get('study_progress', {}))
    score += subjects * 50
    
    # Recent activity bonus (if active in last 7 days)
    if user_stats.get('last_active'):
        last_active = user_stats['last_active']
        if isinstance(last_active, str):
            try:
                last_active = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
            except:
                last_active = datetime.now()
        
        if datetime.now() - last_active < timedelta(days=7):
            score += 100  # Active user bonus
    
    return score

def get_study_level(score: int) -> str:
    """Get study level based on score"""
    if score < 100:
        return "🆕 Beginner"
    elif score < 500:
        return "📚 Learner"
    elif score < 1000:
        return "🎯 Student"
    elif score < 2000:
        return "📖 Scholar"
    elif score < 5000:
        return "🎓 Graduate"
    else:
        return "🏆 Master"

def create_study_summary(user_stats: Dict) -> str:
    """Create a comprehensive study summary"""
    score = calculate_study_score(user_stats)
    level = get_study_level(score)
    
    summary = f"📊 **Study Summary**\n\n"
    summary += f"🏆 **Level:** {level}\n"
    summary += f"⭐ **Score:** {score} points\n"
    summary += f"⏱️ **Total Time:** {format_time(user_stats.get('total_time_spent', 0))}\n"
    summary += f"📥 **Downloads:** {user_stats.get('total_downloads', 0)}\n"
    summary += f"🧪 **Subjects:** {len(user_stats.get('study_progress', {}))}\n"
    summary += f"📅 **Joined:** {user_stats.get('joined_at', 'Unknown')}\n"
    summary += f"🕐 **Last Active:** {user_stats.get('last_active', 'Unknown')}\n"
    
    # Add achievements
    achievements = user_stats.get('achievements', [])
    if achievements:
        summary += f"\n🏅 **Recent Achievements:**\n"
        for achievement in achievements[-3:]:  # Show last 3
            summary += f"• {achievement}\n"
    
    # Add progress bars for subjects
    study_progress = user_stats.get('study_progress', {})
    if study_progress:
        summary += f"\n📈 **Subject Progress:**\n"
        for subject_key, progress in study_progress.items():
            batch_name, subject, chapter = subject_key.split('.')
            total_files = sum(progress.values())
            summary += f"📚 {batch_name} - {subject}: {total_files} files\n"
    
    return summary

def validate_batch_name(batch_name: str) -> bool:
    """Validate batch name format"""
    if not batch_name or len(batch_name) < 2:
        return False
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    if any(char in batch_name for char in invalid_chars):
        return False
    
    return True

def validate_chapter_number(chapter_no: str) -> bool:
    """Validate chapter number format"""
    if not chapter_no:
        return False
    
    # Check if it matches CH## pattern
    import re
    pattern = r'^CH\d{2}$'
    return bool(re.match(pattern, chapter_no))

def validate_lecture_number(lecture_no: str) -> bool:
    """Validate lecture number format"""
    if not lecture_no:
        return False
    
    # Check if it matches L## pattern
    import re
    pattern = r'^L\d{2}$'
    return bool(re.match(pattern, lecture_no))

def create_cache_key(*args) -> str:
    """Create a cache key from arguments"""
    return "_".join(str(arg) for arg in args)

def is_cache_valid(cache_data: Dict, expiry_minutes: int = 60) -> bool:
    """Check if cache data is still valid"""
    if not cache_data or 'timestamp' not in cache_data:
        return False
    
    cache_time = cache_data['timestamp']
    if isinstance(cache_time, str):
        try:
            cache_time = datetime.fromisoformat(cache_time.replace('Z', '+00:00'))
        except:
            return False
    
    return datetime.now() - cache_time < timedelta(minutes=expiry_minutes)

def update_cache(cache_dict: Dict, key: str, data: any, expiry_minutes: int = 60):
    """Update cache with new data"""
    cache_dict[key] = {
        'data': data,
        'timestamp': datetime.now().isoformat(),
        'expiry_minutes': expiry_minutes
    }

def get_cached_data(cache_dict: Dict, key: str):
    """Get cached data if valid"""
    if key in cache_dict:
        cache_data = cache_dict[key]
        if is_cache_valid(cache_data, cache_data.get('expiry_minutes', 60)):
            return cache_data['data']
        else:
            # Remove expired cache
            del cache_dict[key]
    
    return None

def clear_expired_cache(cache_dict: Dict):
    """Clear all expired cache entries"""
    expired_keys = []
    for key, cache_data in cache_dict.items():
        if not is_cache_valid(cache_data, cache_data.get('expiry_minutes', 60)):
            expired_keys.append(key)
    
    for key in expired_keys:
        del cache_dict[key]
    
    if expired_keys:
        logger.info(f"Cleared {len(expired_keys)} expired cache entries")

# Rate limiting utilities
class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make a request"""
        now = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests outside the window
        self.requests[user_id] = [req_time for req_time in self.requests[user_id] 
                                if now - req_time < self.window_seconds]
        
        # Check if user has exceeded limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[user_id].append(now)
        return True
    
    def get_remaining_requests(self, user_id: int) -> int:
        """Get remaining requests for user"""
        now = time.time()
        
        if user_id not in self.requests:
            return self.max_requests
        
        # Remove old requests outside the window
        self.requests[user_id] = [req_time for req_time in self.requests[user_id] 
                                if now - req_time < self.window_seconds]
        
        return max(0, self.max_requests - len(self.requests[user_id]))

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

def check_rate_limit(user_id: int) -> bool:
    """Check if user is within rate limit"""
    return rate_limiter.is_allowed(user_id)

def get_rate_limit_info(user_id: int) -> Dict:
    """Get rate limit information for user"""
    remaining = rate_limiter.get_remaining_requests(user_id)
    return {
        'remaining': remaining,
        'max_requests': rate_limiter.max_requests,
        'window_seconds': rate_limiter.window_seconds
    }

async def get_settings(group_id):
    """Get group settings (compatibility method)"""
    try:
        # This is a compatibility method for the p_ttishow plugin
        # It should get settings from the database
        from database.study_db import get_settings as db_get_settings
        return await db_get_settings(group_id)
    except Exception as e:
        # Return default settings if database is not available
        return type('Settings', (), {
            'welcome': True,
            'auto_delete': False,
            'auto_filter': True,
            'pm_filter': True,
            'auto_search': True,
            'welcome_message': True
        })()

async def save_group_settings(group_id, key, value):
    """Save group settings (compatibility method)"""
    try:
        # This is a compatibility method for other plugins
        # It should save settings to the database
        from database.study_db import save_group_settings as db_save_group_settings
        return await db_save_group_settings(group_id, **{key: value})
    except Exception as e:
        # Return False if database is not available
        return False

def get_size(size):
    """Get human readable file size"""
    if not isinstance(size, (int, float)):
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def get_readable_time(seconds):
    """Convert seconds to human readable time format"""
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "0s"
    
    intervals = [
        ('y', 31536000),  # 60 * 60 * 24 * 365
        ('mo', 2592000),  # 60 * 60 * 24 * 30
        ('w', 604800),    # 60 * 60 * 24 * 7
        ('d', 86400),     # 60 * 60 * 24
        ('h', 3600),      # 60 * 60
        ('m', 60),        # 60
        ('s', 1)          # 1
    ]
    
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                result.append(f"{value}{name}")
            else:
                result.append(f"{value}{name}")
    
    return ' '.join(result[:3]) if result else "0s"
