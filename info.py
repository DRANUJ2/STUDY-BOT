import re
import os
from os import environ, getenv
from Script import script

# Utility functions
id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# ============================
# Bot Information Configuration
# ============================
SESSION = environ.get('SESSION', 'study_bot_search')   # Session name for the bot
API_ID = int(environ.get('API_ID', '')) # API ID from my.telegram.org
API_HASH = environ.get('API_HASH', '')  # API Hash from my.telegram.org
BOT_TOKEN = environ.get('BOT_TOKEN', "")    # Bot token from @BotFather

# ============================
# Bot Settings Configuration
# ============================
CACHE_TIME = int(environ.get('CACHE_TIME', 300))    # Cache time in seconds (default: 5 minutes)
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))  # Use caption filter for search results (default: True)
INDEX_CAPTION = bool(environ.get('SAVE_CAPTION', True)) # Save caption db when indexing make it False if you dont use USE_CAPTION_FILTER for search results (default: True)
#Making it false will not save caption in db SO you can save some storage space

PICS = (environ.get('PICS', 'https://graph.org/file/56b5deb73f3b132e2bb73.jpg https://graph.org/file/5303692652d91d52180c2.jpg https://graph.org/file/425b6f46efc7c6d64105f.jpg https://graph.org/file/876867e761c6c7a29855b.jpg')).split()  # Sample pic
NOR_IMG = environ.get("NOR_IMG", "https://graph.org/file/e20b5fdaf217252964202.jpg")
MELCOW_PHOTO = environ.get("MELCOW_PHOTO", "https://graph.org/file/56b5deb73f3b132e2bb73.jpg")
SPELL_IMG = environ.get("SPELL_IMG", "https://graph.org/file/13702ae26fb05df52667c.jpg")
SUBSCRIPTION = (environ.get('SUBSCRIPTION', 'https://graph.org/file/242b7f1b52743938d81f1.jpg'))
FSUB_PICS = (environ.get('FSUB_PICS', 'https://graph.org/file/7478ff3eac37f4329c3d8.jpg https://graph.org/file/56b5deb73f3b132e2bb73.jpg')).split()  # Fsub pic

# ============================
# Admin, Channels & Users Configuration
# ============================
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()] # Replace with the actual admin ID(s) to add
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-100').split()]  # Channel id for auto indexing (make sure bot is admin)

LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-100'))  # Log channel id (make sure bot is admin)
BIN_CHANNEL = int(environ.get('BIN_CHANNEL', '-100'))  # Bin channel id (make sure bot is admin)
PREMIUM_LOGS = int(environ.get('PREMIUM_LOGS', '-100'))  # Premium logs channel id
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '-100').split()] #(make sure bot is admin)
support_chat_id = environ.get('SUPPORT_CHAT_ID', '-100')  # Support group id (make sure bot is admin)
reqst_channel = environ.get('REQST_CHANNEL_ID', '-100')  # Request channel id (make sure bot is admin)
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'https://t.me/')  # Support group link (make sure bot is admin)

# FORCE_SUB 
auth_req_channels = environ.get("AUTH_REQ_CHANNELS", "-100")# request to join Channel for force sub (make sure bot is admin) only for bot ADMINS  
auth_channels     = environ.get("AUTH_CHANNELS", "-100")# Channels for force sub (make sure bot is admin)

# ============================
# Study Bot Specific Configuration
# ============================
PM_FILTER = is_enabled(environ.get('PM_FILTER', "True"), True)  # Enable/disable PM filtering
PM_ON = is_enabled(environ.get('PM_ON', "True"), True)  # Enable/disable PM mode
AUTO_SUGGESTION = is_enabled(environ.get('AUTO_SUGGESTION', "True"), True)  # Enable/disable auto suggestions
GAMIFICATION = is_enabled(environ.get('GAMIFICATION', "True"), True)  # Enable/disable gamification features

# Bot Information
BOT_USERNAME = environ.get('BOT_USERNAME', 'StudyBot')
CONTENT_BOT_USERNAME = environ.get('CONTENT_BOT_USERNAME', 'StudyContentBot')
MAIN_CHANNEL = environ.get('MAIN_CHANNEL', 'https://t.me/your_channel')
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', 'https://t.me/your_support_group')
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/your_username')

# Index Request Channel
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))

# ============================
# Payment Configuration
# ============================
QR_CODE = environ.get('QR_CODE', 'https://graph.org/file/e419f801841c2ee3db0fc.jpg')    # QR code image for payments
OWNER_UPI_ID = environ.get('OWNER_UPI_ID', 'ɴᴏ ᴀᴠᴀɪʟᴀʙʟᴇ ʀɪɢʜᴛ ɴᴏᴡ')    # Owner UPI ID for payments

STAR_PREMIUM_PLANS = {
    10: "7day",
    20: "15day",    
    40: "1month", 
    55: "45day",
    75: "60day",
}  # Premium plans with their respective durations in days

# ============================
# MongoDB Configuration
# ============================
DATABASE_URI = environ.get('DATABASE_URI', "")  # MongoDB URI for the database
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0") # Database name (default: cluster)
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'study_bot_files') # Collection name (default: study_bot_files)

# If MULTIPLE_DB Is True Then Fill DATABASE_URI2 Value Else You Will Get Error.
MULTIPLE_DB = is_enabled(os.environ.get('MULTIPLE_DB', "False"), False) # Type True For Turn On MULTIPLE DB FUNCTION 
DATABASE_URI2 = environ.get('DATABASE_URI2', "")  # MongoDB URI for the second database (if MULTIPLE_DB is True)

# ============================
# Study Content Configuration
# ============================
DEFAULT_SUBJECTS = ["Physics", "Chemistry", "Biology"]
DEFAULT_TEACHERS = ["Mr Sir", "Saleem Sir"]
DEFAULT_CHAPTERS = {
    "Physics": ["WAVES", "OPTICS", "MECHANICS", "THERMODYNAMICS", "ELECTROMAGNETISM"],
    "Chemistry": ["ORGANIC", "INORGANIC", "PHYSICAL", "ANALYTICAL", "BIOCHEMISTRY"],
    "Biology": ["CELL BIOLOGY", "GENETICS", "ECOLOGY", "ANATOMY", "PHYSIOLOGY"]
}

# ============================
# Web Server Configuration
# ============================
WEB_SERVER_HOST = environ.get('WEB_SERVER_HOST', '0.0.0.0')
WEB_SERVER_PORT = int(environ.get('WEB_SERVER_PORT', 8080))
WEB_SERVER_URL = environ.get('WEB_SERVER_URL', 'https://your-domain.com')

# ============================
# Redis Configuration (Optional)
# ============================
REDIS_URL = environ.get('REDIS_URL', '')  # Redis URL for caching (optional)
REDIS_HOST = environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = environ.get('REDIS_PASSWORD', '')

# ============================
# Telegraph Configuration
# ============================
TELEGRAPH_TOKEN = environ.get('TELEGRAPH_TOKEN', '')  # Telegraph API token

# ============================
# License Management
# ============================
LICENSE_KEY = environ.get('LICENSE_KEY', '')  # Bot license key
LICENSE_VERIFICATION = is_enabled(environ.get('LICENSE_VERIFICATION', "False"), False)

# ============================
# Study Bot Features
# ============================
STUDY_BOT_FEATURES = {
    "dual_bot_system": True,
    "hierarchical_navigation": True,
    "batch_based_content": True,
    "progress_tracking": True,
    "admin_management": True,
    "file_upload_management": True,
    "user_analytics": True,
    "broadcasting_system": True,
    "join_request_management": True,
    "ban_unban_system": True,
    "content_delivery": True,
    "study_materials": True,
    "lectures": True,
    "dpp": True,
    "mind_maps": True,
    "revision_notes": True,
    "short_notes": True,
    "pyqs": True,
    "kpp_pdf": True,
    "kpp_solutions": True,
    "practice_sheets": True,
    "important_notes": True,
    "handwritten_notes": True,
    "module_questions": True
}

# ============================
# Content Types
# ============================
CONTENT_TYPES = [
    "Lectures",
    "DPP (Daily Practice Problems)",
    "All Study Materials"
]

STUDY_MATERIALS = [
    "Mind Maps",
    "Revision Notes",
    "Short Notes",
    "Previous Year Questions",
    "KPP PDF",
    "KPP Solutions",
    "Practice Sheets",
    "Important Notes",
    "Handwritten Notes",
    "Module Questions"
]

# ============================
# Bot Version and Info
# ============================
__version__ = "1.0.0"
__author__ = "Study Bot Team"
__description__ = "Advanced Study Bot with Dual Bot System"
__license__ = "MIT"

BOT_INFO = {
    "name": "Study Bot",
    "version": __version__,
    "description": "Your Personal Learning Companion",
    "features": list(STUDY_BOT_FEATURES.keys()),
    "subjects": DEFAULT_SUBJECTS,
    "content_types": CONTENT_TYPES,
    "study_materials": STUDY_MATERIALS
}

TECH_INFO = {
    "framework": "Pyrogram",
    "database": "MongoDB with Motor & Umongo",
    "python_version": "3.8+",
    "async_support": True,
    "web_server": "aiohttp",
    "deployment": ["Docker", "Heroku", "Railway", "Render"],
    "features": [
        "Async/Await",
        "Rate Limiting",
        "File Handling",
        "Template Rendering",
        "Configuration Management",
        "Logging System",
        "Error Handling",
        "Plugin Architecture"
    ]
}

CONTACT_INFO = {
    "support": "@support_group",
    "main_channel": "@main_channel",
    "updates": "@updates_channel",
    "email": "support@studybot.com",
    "website": "https://studybot.com"
}

DEV_INFO = {
    "repository": "https://github.com/studybot/study-bot",
    "issues": "https://github.com/studybot/study-bot/issues",
    "documentation": "https://docs.studybot.com",
    "contributing": "https://github.com/studybot/study-bot/blob/main/CONTRIBUTING.md"
}

def get_bot_info() -> dict:
    """Get complete bot information"""
    return {
        "bot": BOT_INFO,
        "technical": TECH_INFO,
        "contact": CONTACT_INFO,
        "development": DEV_INFO,
        "version": __version__
    }

def get_version() -> str:
    """Get bot version"""
    return __version__

def get_features() -> list:
    """Get bot features"""
    return list(STUDY_BOT_FEATURES.keys())

def get_subjects() -> list:
    """Get available subjects"""
    return DEFAULT_SUBJECTS

def get_teachers() -> list:
    """Get available teachers"""
    return DEFAULT_TEACHERS

def get_chapters(subject: str) -> list:
    """Get chapters for a specific subject"""
    return DEFAULT_CHAPTERS.get(subject, [])

def get_content_types() -> list:
    """Get available content types"""
    return CONTENT_TYPES

def get_study_materials() -> list:
    """Get available study materials"""
    return STUDY_MATERIALS
