import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

# Try to import dependencies with fallbacks
try:
    from pymongo.errors import DuplicateKeyError
except ImportError:
    DuplicateKeyError = Exception

try:
    from umongo import Instance, Document, fields
except ImportError:
    # Fallback for when umongo is not available
    Instance = None
    Document = None
    fields = None

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    AsyncIOMotorClient = None

try:
    from config import *
except ImportError:
    # Fallback configuration values
    DATABASE_URI = ""
    DATABASE_NAME = "StudyBotDB"
    COLLECTION_NAME = "study_files"
    MULTIPLE_DB = False
    DATABASE_URI2 = ""
    DEFAULT_SUBJECTS = ["Physics", "Chemistry", "Biology"]
    DEFAULT_TEACHERS = ["Mr Sir", "Saleem Sir"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Database connections - only initialize if dependencies are available
if AsyncIOMotorClient and Instance and DATABASE_URI:
    client = AsyncIOMotorClient(DATABASE_URI)
    db = client[DATABASE_NAME]
    instance = Instance.from_db(db)
    
    # Secondary database if enabled
    if MULTIPLE_DB and DATABASE_URI2:
        client2 = AsyncIOMotorClient(DATABASE_URI2)
        db2 = client2[DATABASE_NAME]
        instance2 = Instance.from_db(db2)
    else:
        client2 = None
        db2 = None
        instance2 = None
else:
    client = None
    db = None
    instance = None
    client2 = None
    db2 = None
    instance2 = None

# Only define document classes if instance is available
if instance:
    @instance.register
    class StudyFiles(Document):
        """Main collection for study files"""
        file_id = fields.StringField(attribute="_id")
        file_ref = fields.StringField(allow_none=True)
        file_name = fields.StringField(required=True)
        file_size = fields.IntegerField(required=True)
        file_type = fields.StringField(allow_none=True)
        mime_type = fields.StringField(allow_none=True)
        caption = fields.StringField(allow_none=True)
        
        # Study specific fields
        batch_name = fields.StringField(required=True)
        subject = fields.StringField(required=True)
        teacher = fields.StringField(allow_none=True)
        chapter_no = fields.StringField(allow_none=True)
        chapter_name = fields.StringField(allow_none=True)
        lecture_no = fields.StringField(allow_none=True)
        content_type = fields.StringField(required=True)  # NOTES, DPP, LECTURE, etc.
        tags = fields.ListField(fields.StringField(), default_factory=list)
        
        # Metadata
        uploaded_by = fields.IntegerField(required=True)
        uploaded_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        is_active = fields.BooleanField(default=True)
        
        class Meta:
            indexes = [
                ("$file_name",),
                ("batch_name",),
                ("subject",),
                ("chapter_no",),
                ("content_type",),
                ("tags",),
                ("uploaded_at",)
            ]
            collection_name = COLLECTION_NAME

    @instance.register
    class Batches(Document):
        """Collection for batch information"""
        batch_id = fields.StringField(attribute="_id")
        batch_name = fields.StringField(required=True, unique=True)
        batch_image = fields.StringField(allow_none=True)
        batch_caption = fields.StringField(allow_none=True)
        subjects = fields.ListField(fields.StringField(), default_factory=lambda: DEFAULT_SUBJECTS)
        teachers = fields.ListField(fields.StringField(), default_factory=lambda: DEFAULT_TEACHERS)
        is_active = fields.BooleanField(default=True)
        created_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        created_by = fields.IntegerField(required=True)
        
        class Meta:
            indexes = [("batch_name",), ("is_active",)]
            collection_name = "batches"

    @instance.register
    class Chapters(Document):
        """Collection for chapter information"""
        chapter_id = fields.StringField(attribute="_id")
        batch_name = fields.StringField(required=True)
        subject = fields.StringField(required=True)
        chapter_no = fields.StringField(required=True)
        chapter_name = fields.StringField(required=True)
        total_lectures = fields.IntegerField(default=0)
        total_dpp = fields.IntegerField(default=0)
        total_notes = fields.IntegerField(default=0)
        is_active = fields.BooleanField(default=True)
        created_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [
                ("batch_name", "subject", "chapter_no"),
                ("is_active",)
            ]
            collection_name = "chapters"

    @instance.register
    class Users(Document):
        """Collection for user information and progress"""
        user_id = fields.IntegerField(attribute="_id")
        first_name = fields.StringField(required=True)
        last_name = fields.StringField(allow_none=True)
        username = fields.StringField(allow_none=True)
        is_premium = fields.BooleanField(default=False)
        premium_expiry = fields.DateTimeField(allow_none=True)
        current_batch = fields.StringField(allow_none=True)
        study_progress = fields.DictField(default_factory=dict)
        total_downloads = fields.IntegerField(default=0)
        total_time_spent = fields.IntegerField(default=0)  # in minutes
        achievements = fields.ListField(fields.StringField(), default_factory=list)
        joined_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        last_active = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        banned = fields.BooleanField(default=False)
        ban_reason = fields.StringField(allow_none=True)
        banned_by = fields.IntegerField(allow_none=True)
        banned_at = fields.DateTimeField(allow_none=True)
        
        class Meta:
            indexes = [
                ("username",),
                ("is_premium",),
                ("current_batch",),
                ("last_active",)
            ]
            collection_name = "users"

    @instance.register
    class StudySessions(Document):
        """Collection for tracking study sessions"""
        session_id = fields.StringField(attribute="_id")
        user_id = fields.IntegerField(required=True)
        batch_name = fields.StringField(required=True)
        subject = fields.StringField(required=True)
        chapter_no = fields.StringField(required=True)
        content_type = fields.StringField(required=True)
        start_time = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        end_time = fields.DateTimeField(allow_none=True)
        duration = fields.IntegerField(default=0)  # in minutes
        files_accessed = fields.ListField(fields.StringField(), default_factory=list)
        
        class Meta:
            indexes = [
                ("user_id",),
                ("batch_name",),
                ("start_time",),
                ("end_time",)
            ]
            collection_name = "study_sessions"

    @instance.register
    class ContentAnalytics(Document):
        """Collection for content analytics and insights"""
        content_id = fields.StringField(attribute="_id")
        file_id = fields.StringField(required=True)
        batch_name = fields.StringField(required=True)
        subject = fields.StringField(required=True)
        chapter_no = fields.StringField(required=True)
        content_type = fields.StringField(required=True)
        total_views = fields.IntegerField(default=0)
        total_downloads = fields.IntegerField(default=0)
        unique_viewers = fields.ListField(fields.IntegerField(), default_factory=list)
        rating = fields.FloatField(default=0.0)
        total_ratings = fields.IntegerField(default=0)
        feedback = fields.ListField(fields.DictField(), default_factory=list)
        last_accessed = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [
                ("file_id",),
                ("batch_name",),
                ("subject",),
                ("content_type",),
                ("total_views",),
                ("rating",)
            ]
            collection_name = "content_analytics"

    @instance.register
    class BotSettings(Document):
        """Collection for bot configuration and settings"""
        setting_id = fields.StringField(attribute="_id")
        setting_name = fields.StringField(required=True, unique=True)
        setting_value = fields.RawField(required=True)
        setting_type = fields.StringField(required=True)  # string, int, bool, list, dict
        description = fields.StringField(allow_none=True)
        updated_by = fields.IntegerField(required=True)
        updated_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [("setting_name",), ("updated_at",)]
            collection_name = "bot_settings"

    @instance.register
    class JoinRequests(Document):
        """Collection for join requests"""
        request_id = fields.StringField(attribute="_id")
        user_id = fields.IntegerField(required=True)
        chat_id = fields.IntegerField(required=True)
        chat_title = fields.StringField(required=True)
        chat_type = fields.StringField(required=True)
        user_first_name = fields.StringField(required=True)
        user_last_name = fields.StringField(allow_none=True)
        user_username = fields.StringField(allow_none=True)
        status = fields.StringField(default="pending")  # pending, approved, rejected
        requested_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        processed_at = fields.DateTimeField(allow_none=True)
        processed_by = fields.IntegerField(allow_none=True)
        notes = fields.StringField(allow_none=True)
        
        class Meta:
            indexes = [
                ("user_id",),
                ("chat_id",),
                ("status",),
                ("requested_at",)
            ]
            collection_name = "join_requests"

    @instance.register
    class Chats(Document):
        """Collection for chat information"""
        chat_id = fields.IntegerField(attribute="_id")
        chat_title = fields.StringField(required=True)
        chat_type = fields.StringField(required=True)  # group, supergroup, channel
        is_active = fields.BooleanField(default=True)
        member_count = fields.IntegerField(default=0)
        created_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        last_activity = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [
                ("chat_type",),
                ("is_active",),
                ("last_activity",)
            ]
            collection_name = "chats"

    @instance.register
    class GroupSettings(Document):
        """Collection for group settings"""
        group_id = fields.IntegerField(attribute="_id")
        welcome = fields.BooleanField(default=True)
        auto_delete = fields.BooleanField(default=False)
        auto_filter = fields.BooleanField(default=True)
        pm_filter = fields.BooleanField(default=True)
        auto_search = fields.BooleanField(default=True)
        welcome_message = fields.BooleanField(default=True)
        created_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        updated_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [("group_id",), ("auto_filter",)]
            collection_name = "group_settings"

    # Secondary database models if enabled
    if MULTIPLE_DB and instance2:
        @instance2.register
        class StudyFiles2(StudyFiles):
            class Meta:
                collection_name = COLLECTION_NAME

# Database utility functions
async def save_study_file(media, batch_name, subject, teacher=None, 
                         chapter_no=None, chapter_name=None, lecture_no=None, 
                         content_type="NOTES", tags=None, uploaded_by=None):
    """Save study file in database"""
    if not instance:
        logger.warning("Database not initialized - cannot save file")
        return False
        
    try:
        file_id = str(media.file_id)
        file_name = media.file_name or "Unknown"
        file_size = media.file_size or 0
        file_type = media.file_type or "unknown"
        mime_type = getattr(media, 'mime_type', None)
        caption = getattr(media, 'caption', None)
        
        # Create file document
        file_doc = StudyFiles(
            file_id=file_id,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type,
            caption=caption,
            batch_name=batch_name,
            subject=subject,
            teacher=teacher,
            chapter_no=chapter_no,
            chapter_name=chapter_name,
            lecture_no=lecture_no,
            content_type=content_type,
            tags=tags or [],
            uploaded_by=uploaded_by or 0
        )
        
        await file_doc.commit()
        
        # Create analytics entry
        analytics_doc = ContentAnalytics(
            content_id=f"analytics_{file_id}",
            file_id=file_id,
            batch_name=batch_name,
            subject=subject,
            chapter_no=chapter_no or "",
            content_type=content_type
        )
        await analytics_doc.commit()
        
        logger.info(f"Study file saved: {file_name} for {batch_name} - {subject}")
        return True
        
    except DuplicateKeyError:
        logger.warning(f"File already exists: {file_id}")
        return False
    except Exception as e:
        logger.error(f"Error saving study file: {e}")
        return False

# Add other utility functions here...
async def ensure_indexes():
    """Ensure all database indexes are created"""
    if not instance:
        logger.warning("Database not initialized - cannot create indexes")
        return False
        
    try:
        await StudyFiles.ensure_indexes()
        await Batches.ensure_indexes()
        await Chapters.ensure_indexes()
        await Users.ensure_indexes()
        await StudySessions.ensure_indexes()
        await ContentAnalytics.ensure_indexes()
        await BotSettings.ensure_indexes()
        await JoinRequests.ensure_indexes()
        await Chats.ensure_indexes()
        await GroupSettings.ensure_indexes()
        
        # Create text index for search
        if db:
            await db[COLLECTION_NAME].create_index([("file_name", "text"), ("caption", "text")])
        
        logger.info("All database indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        return False

# Initialize database
async def init_db():
    """Initialize database connection and indexes"""
    try:
        if not instance:
            logger.warning("Database dependencies not available")
            return False
            
        await ensure_indexes()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
