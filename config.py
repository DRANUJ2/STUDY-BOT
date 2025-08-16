import os
import re
from os import environ, getenv
try:
    from dotenv import load_dotenv
except ImportError:
    from python_dotenv import load_dotenv

load_dotenv()

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
# ⭐ SESSION: Bot session name (can be any unique name)
SESSION = environ.get('SESSION', 'StudyBot_Session')

# ⭐ API_ID: Your Telegram API ID from https://my.telegram.org/apps
API_ID = int(environ.get('API_ID', '0')) if environ.get('API_ID') else 0

# ⭐ API_HASH: Your Telegram API Hash from https://my.telegram.org/apps
API_HASH = environ.get('API_HASH', '')

# ⭐ BOT_TOKEN: Main bot token from @BotFather
BOT_TOKEN = environ.get('BOT_TOKEN', "")

# ⭐ CONTENT_BOT_TOKEN: Content bot token from @BotFather (for file delivery)
CONTENT_BOT_TOKEN = environ.get('CONTENT_BOT_TOKEN', "")

# ============================
# Bot Settings Configuration
# ============================
# CACHE_TIME: How long to cache data (in seconds)
CACHE_TIME = int(environ.get('CACHE_TIME', 300))

# USE_CAPTION_FILTER: Enable/disable caption filtering for search
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))

# INDEX_CAPTION: Save captions in database for search
INDEX_CAPTION = bool(environ.get('SAVE_CAPTION', True))

# CUSTOM_FILE_CAPTION: Custom caption template for files
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "")

# BATCH_FILE_CAPTION: Custom caption for batch files
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)

# ============================
# Study Bot Specific Settings
# ============================
# PM_ON: Allow users to use bot in private messages
PM_ON = is_enabled(environ.get('PM_ON', "True"), True)

# PM_FILTER: Enable PM filtering
PM_FILTER = is_enabled(environ.get('PM_FILTER', "True"), True)

# AUTO_SUGGESTION: Enable auto-suggestions for users
AUTO_SUGGESTION = is_enabled(environ.get('AUTO_SUGGESTION', "True"), True)

# GAMIFICATION: Enable progress tracking and achievements
GAMIFICATION = is_enabled(environ.get('GAMIFICATION', "True"), True)

# MULTI_LANGUAGE: Enable multi-language support
MULTI_LANGUAGE = is_enabled(environ.get('MULTI_LANGUAGE', "False"), False)

# ============================
# Images and Media
# ============================
# PICS: Welcome images (space-separated URLs)
PICS = (environ.get('PICS', 'https://graph.org/file/56b5deb73f3b132e2bb73.jpg https://graph.org/file/5303692652d91d52180c2.jpg https://graph.org/file/425b6f46efc7c6d64105f.jpg https://graph.org/file/876867e761c6c7a29855b.jpg')).split()

# NOR_IMG: Default image for no results
NOR_IMG = environ.get("NOR_IMG", "https://graph.org/file/e20b5fdaf217252964202.jpg")

# MELCOW_PHOTO: Welcome photo for new users
MELCOW_PHOTO = environ.get("MELCOW_PHOTO", "https://graph.org/file/56b5deb73f3b132e2bb73.jpg")

# MELCOW_NEW_USERS: Enable welcome message for new users
MELCOW_NEW_USERS = is_enabled(environ.get('MELCOW_NEW_USERS', "False"), False)

# SPELL_IMG: Image for spell check results
SPELL_IMG = environ.get("SPELL_IMG", "https://graph.org/file/13702ae26fb05df52667c.jpg")

# SUBSCRIPTION: Premium subscription image
SUBSCRIPTION = environ.get('SUBSCRIPTION', 'https://graph.org/file/242b7f1b52743938d81f1.jpg')

# QR_CODE: QR code image for payments
QR_CODE = environ.get('QR_CODE', 'https://graph.org/file/e419f801841c2ee3db0fc.jpg')

# OWNER_UPI_ID: Your UPI ID for payments
OWNER_UPI_ID = environ.get('OWNER_UPI_ID', 'ɴᴏ ᴀᴠᴀɪʟᴀʙʟᴇ ʀɪɢʜᴛ ɴᴏᴡ')

# FSUB_PICS: Force subscribe images
FSUB_PICS = (environ.get('FSUB_PICS', 'https://graph.org/file/7478ff3eac37f4329c3d8.jpg https://graph.org/file/56b5deb73f3b132e2bb73.jpg')).split()

# ============================
# Admin, Channels & Users Configuration
# ============================
# ⭐ ADMINS: List of admin user IDs (space-separated)
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]

# OWNER_ID: Owner IDs (automatically extracted from ADMINS)
OWNER_ID = [int(admin) for admin in environ.get('ADMINS', '').split() if id_pattern.search(admin)]

# ⭐ CHANNELS: List of channel IDs where bot will work (space-separated)
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-100').split()]

# ⭐ LOG_CHANNEL: Channel ID for bot logs
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-100'))

# BIN_CHANNEL: Channel ID for deleted files
BIN_CHANNEL = int(environ.get('BIN_CHANNEL', '-100'))

# PREMIUM_LOGS: Channel ID for premium logs
PREMIUM_LOGS = int(environ.get('PREMIUM_LOGS', '-100'))

# DELETE_CHANNELS: Channels to delete files from
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '-100').split()]

# support_chat_id: Support chat ID
support_chat_id = environ.get('SUPPORT_CHAT_ID', '-100')

# reqst_channel: Request channel ID
reqst_channel = environ.get('REQST_CHANNEL_ID', '-100')

# SUPPORT_CHAT: Support chat link
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'https://t.me/')

# INDEX_REQ_CHANNEL: Index request channel
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))

# FORCE_SUB 
# auth_req_channels: Channels for force subscribe
auth_req_channels = environ.get("AUTH_REQ_CHANNELS", "-100")

# auth_channels: Auth channels
auth_channels = environ.get("AUTH_CHANNELS", "-100")

# AUTH_CHANNEL: Force subscribe channels
AUTH_CHANNEL = environ.get("AUTH_CHANNEL", "")

# AUTH_USERS: Authorized users
AUTH_USERS = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]

# ============================
# Study Content Channels
# ============================
# ⭐ STUDY_CONTENT_CHANNELS: Channels containing study materials
STUDY_CONTENT_CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('STUDY_CONTENT_CHANNELS', '-100').split()]

# ⭐ PHYSICS_CHANNEL: Channel ID for Physics content
PHYSICS_CHANNEL = int(environ.get('PHYSICS_CHANNEL', '-100'))

# ⭐ CHEMISTRY_CHANNEL: Channel ID for Chemistry content
CHEMISTRY_CHANNEL = int(environ.get('CHEMISTRY_CHANNEL', '-100'))

# ⭐ BIOLOGY_CHANNEL: Channel ID for Biology content
BIOLOGY_CHANNEL = int(environ.get('BIOLOGY_CHANNEL', '-100'))

# ============================
# Bot Information
# ============================
# ⭐ BOT_USERNAME: Your main bot username (without @)
BOT_USERNAME = environ.get('BOT_USERNAME', 'StudyBot')

# ⭐ CONTENT_BOT_USERNAME: Your content bot username (without @)
CONTENT_BOT_USERNAME = environ.get('CONTENT_BOT_USERNAME', 'StudyContentBot')

# ⭐ MAIN_CHANNEL: Your main channel link
MAIN_CHANNEL = environ.get('MAIN_CHANNEL', 'https://t.me/your_channel')

# ⭐ SUPPORT_GROUP: Your support group link
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', 'https://t.me/your_support_group')

# ⭐ OWNER_LNK: Your personal Telegram link
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/your_username')

# ============================
# MongoDB Configuration
# ============================
# ⭐ DATABASE_URI: MongoDB connection string
DATABASE_URI = environ.get('DATABASE_URI', "")

# DATABASE_NAME: Database name
DATABASE_NAME = environ.get('DATABASE_NAME', "StudyBotDB")

# COLLECTION_NAME: Collection name for files
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'study_files')

# Multiple Database Support
# MULTIPLE_DB: Enable multiple database support
MULTIPLE_DB = is_enabled(os.environ.get('MULTIPLE_DB', "False"), False)

# DATABASE_URI2: Second database URI (if MULTIPLE_DB is True)
DATABASE_URI2 = environ.get('DATABASE_URI2', "")

# DB_CHANGE_LIMIT: Database size limit for switching
DB_CHANGE_LIMIT = int(environ.get('DB_CHANGE_LIMIT', "432"))

# ============================
# Web Server Configuration
# ============================
# PORT: Web server port
PORT = int(environ.get('PORT', 8080))

# ON_HEROKU: Set to True if deploying on Heroku
ON_HEROKU = environ.get('ON_HEROKU', False)

# ============================
# Premium Features
# ============================
# PREMIUM_FEATURES: Enable premium features
PREMIUM_FEATURES = is_enabled(environ.get('PREMIUM_FEATURES', "True"), True)

# PREMIUM_PLANS: Premium subscription plans
PREMIUM_PLANS = {
    10: "7day",
    20: "15day",    
    40: "1month", 
    55: "45day",
    75: "60day",
}

# STAR_PREMIUM_PLANS: Star-based premium plans
STAR_PREMIUM_PLANS = {
    10: "7day",
    20: "15day",    
    40: "1month", 
    55: "45day",
    75: "60day",
}

# ============================
# Study Bot Features
# ============================
# AUTO_TAGGING: Enable automatic content tagging
AUTO_TAGGING = is_enabled(environ.get('AUTO_TAGGING', "True"), True)

# BULK_UPLOAD: Enable bulk file upload
BULK_UPLOAD = is_enabled(environ.get('BULK_UPLOAD', "True"), True)

# UPDATE_NOTIFICATIONS: Enable update notifications
UPDATE_NOTIFICATIONS = is_enabled(environ.get('UPDATE_NOTIFICATIONS', "True"), True)

# FULL_TEXT_SEARCH: Enable full-text search
FULL_TEXT_SEARCH = is_enabled(environ.get('FULL_TEXT_SEARCH', "True"), True)

# HYBRID_STORAGE: Enable hybrid storage system
HYBRID_STORAGE = is_enabled(environ.get('HYBRID_STORAGE', "True"), True)

# IS_VERIFY: Enable verification system
IS_VERIFY = is_enabled(environ.get('IS_VERIFY', "False"), False)

# TUTORIAL: Tutorial link for verification
TUTORIAL = environ.get("TUTORIAL", "https://t.me/")

# TUTORIAL_2: Second tutorial link
TUTORIAL_2 = environ.get("TUTORIAL_2", "https://t.me/")

# TUTORIAL_3: Third tutorial link
TUTORIAL_3 = environ.get("TUTORIAL_3", "https://t.me/")

# IMDB: Enable IMDB search feature
IMDB = is_enabled(environ.get('IMDB', "False"), False)

# AUTO_DELETE: Enable auto-delete feature
AUTO_DELETE = is_enabled(environ.get('AUTO_DELETE', "True"), True)

# WELCOME: Enable welcome messages
WELCOME = is_enabled(environ.get('WELCOME', "True"), True)

# WELCOME_MESSAGE: Enable welcome message text
WELCOME_MESSAGE = is_enabled(environ.get('WELCOME_MESSAGE', "True"), True)

# AUTO_FILTER: Enable auto-filtering
AUTO_FILTER = is_enabled(environ.get('AUTO_FILTER', "True"), True)

# AUTO_SEARCH: Enable auto-search
AUTO_SEARCH = is_enabled(environ.get('AUTO_SEARCH', "True"), True)

# SPELL_CHECK_REPLY: Enable spell check
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)

# MAX_BTN: Enable max button feature
MAX_BTN = is_enabled(environ.get('MAX_BTN', "True"), True)

# MAX_B_TN: Maximum buttons per row
MAX_B_TN = environ.get("MAX_B_TN", "5")

# LONG_IMDB_DESCRIPTION: Enable long IMDB descriptions
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)

# LINK_MODE: Enable link mode for file sharing
LINK_MODE = is_enabled(environ.get('LINK_MODE', "False"), False)

# PROTECT_CONTENT: Enable content protection
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', "False"), False)

# INVITE_LINK: Bot invite link
INVITE_LINK = environ.get('INVITE_LINK', '')

# UPDATES_CHANNEL: Updates channel
UPDATES_CHANNEL = environ.get('UPDATES_CHANNEL', '')

# FILE_STORE_CHANNEL: File store channel
FILE_STORE_CHANNEL = environ.get('FILE_STORE_CHANNEL', '')

# PUBLIC_FILE_STORE: Enable public file store
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE', "True"), True)

# CUSTOM_QUERY_CAPTION: Custom query caption template
CUSTOM_QUERY_CAPTION = environ.get("CUSTOM_QUERY_CAPTION", "")

# DELETE_TIME: Auto-delete time in seconds
DELETE_TIME = int(environ.get('DELETE_TIME', 300))

# AUTO_FFILTER: Enable auto-filtering
AUTO_FFILTER = is_enabled(environ.get('AUTO_FFILTER', "True"), True)

# CHAT_LIMIT: Chat limit for file sharing
CHAT_LIMIT = int(environ.get('CHAT_LIMIT', 10))

# MAX_LIST_ELM: Maximum list elements
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)

# SINGLE_BUTTON: Enable single button mode
SINGLE_BUTTON = is_enabled(environ.get('SINGLE_BUTTON', "False"), False)

# WATERMARK_TEXT: Watermark text for files
WATERMARK_TEXT = environ.get('WATERMARK_TEXT', '')

# SUPPORT_CHAT_ID: Support chat ID
SUPPORT_CHAT_ID = environ.get('SUPPORT_CHAT_ID', '')

# REQST_CHANNEL_ID: Request channel ID
REQST_CHANNEL_ID = environ.get('REQST_CHANNEL_ID', '')

# ============================
# Default Study Settings
# ============================
# DEFAULT_SUBJECTS: Default subjects for study bot
DEFAULT_SUBJECTS = ["Physics", "Chemistry", "Biology"]

# DEFAULT_TEACHERS: Default teachers for study bot
DEFAULT_TEACHERS = ["Mr Sir", "Saleem Sir"]

# MAX_CHAPTERS: Maximum number of chapters
MAX_CHAPTERS = 50

# MAX_LECTURES: Maximum number of lectures
MAX_LECTURES = 100

# ============================
# File Size Limits
# ============================
# MAX_FILE_SIZE: Maximum file size (2GB in bytes)
MAX_FILE_SIZE = int(environ.get('MAX_FILE_SIZE', 2097152000))

# CHUNK_SIZE: File chunk size (50MB)
CHUNK_SIZE = int(environ.get('CHUNK_SIZE', 52428800))

# ============================
# Cache Settings
# ============================
# REDIS_URL: Redis connection URL (optional)
REDIS_URL = environ.get('REDIS_URL', "")

# CACHE_EXPIRY: Cache expiry time in seconds
CACHE_EXPIRY = int(environ.get('CACHE_EXPIRY', 3600))

# ============================
# Security Settings
# ============================
# ENCRYPTION_KEY: Encryption key for sensitive data
ENCRYPTION_KEY = environ.get('ENCRYPTION_KEY', "")

# RATE_LIMIT: Rate limit per minute
RATE_LIMIT = int(environ.get('RATE_LIMIT', 10))

# MAX_REQUESTS: Maximum requests per user per day
MAX_REQUESTS = int(environ.get('MAX_REQUESTS', 100))
