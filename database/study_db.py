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
except ImportError as e:
    print(f"Warning: Could not import motor: {e}")
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

# Initialize variables to None first
client = None
db = None
instance = None
client2 = None
db2 = None
instance2 = None

# Database connections - only initialize if dependencies are available
try:
    if AsyncIOMotorClient and Instance and DATABASE_URI:
        client = AsyncIOMotorClient(DATABASE_URI)
        raw_db = client[DATABASE_NAME]
        instance = Instance.from_db(raw_db)
        
        # Create a custom wrapper that doesn't expose command method
        class DatabaseWrapper:
            def __init__(self, database):
                self._db = database
                # Copy all attributes except command
                for attr in dir(database):
                    if not attr.startswith('_') and attr != 'command':
                        setattr(self, attr, getattr(database, attr))
            
            def __getattr__(self, name):
                if name == 'command':
                    raise AttributeError("'DatabaseWrapper' object has no attribute 'command'")
                return getattr(self._db, name)
        
        db = DatabaseWrapper(raw_db)
        
        # Secondary database if enabled
        if MULTIPLE_DB and DATABASE_URI2:
            client2 = AsyncIOMotorClient(DATABASE_URI2)
            raw_db2 = client2[DATABASE_NAME]
            instance2 = Instance.from_db(raw_db2)
            
            # Create a custom wrapper that doesn't expose command method
            db2 = DatabaseWrapper(raw_db2)
except Exception as e:
    print(f"Warning: Could not initialize database connections in study_db.py: {e}")
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
        is_active = fields.BooleanField(default_factory=lambda: True)
        
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
        """Batches collection"""
        batch_id = fields.StringField(attribute="_id")
        batch_name = fields.StringField(required=True, unique=True)
        description = fields.StringField(allow_none=True)
        subjects = fields.ListField(fields.StringField(), default_factory=list)
        teachers = fields.ListField(fields.StringField(), default_factory=list)
        is_active = fields.BooleanField(default_factory=lambda: True)
        created_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
              indexes = [("is_active",)]   # ✅ "batch_name" hata diya
              collection_name = "batches"

    @instance.register
    class Chapters(Document):
        """Chapters collection"""
        chapter_id = fields.StringField(attribute="_id")
        batch_name = fields.StringField(required=True)
        subject = fields.StringField(required=True)
        chapter_no = fields.StringField(required=True)
        chapter_name = fields.StringField(required=True)
        description = fields.StringField(allow_none=True)
        is_active = fields.BooleanField(default_factory=lambda: True)
        created_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [("batch_name",), ("subject",), ("chapter_no",)]
            collection_name = "chapters"

    @instance.register
    class Users(Document):
        """Users collection"""
        user_id = fields.IntegerField(attribute="_id")
        username = fields.StringField(allow_none=True)
        first_name = fields.StringField(allow_none=True)
        last_name = fields.StringField(allow_none=True)
        is_premium = fields.BooleanField(default_factory=lambda: False)
        premium_expires = fields.DateTimeField(allow_none=True)
        joined_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        last_active = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [("username",), ("is_premium",)]
            collection_name = "users"

    @instance.register
    class StudySessions(Document):
        """Study sessions collection"""
        session_id = fields.StringField(attribute="_id")
        user_id = fields.IntegerField(required=True)
        batch_name = fields.StringField(required=True)
        subject = fields.StringField(required=True)
        chapter_no = fields.StringField(allow_none=True)
        start_time = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        end_time = fields.DateTimeField(allow_none=True)
        duration_minutes = fields.IntegerField(default_factory=lambda: 0)
        
        class Meta:
            indexes = [("user_id",), ("batch_name",), ("start_time",)]
            collection_name = "study_sessions"

    @instance.register
    class ContentAnalytics(Document):
        """Content analytics collection"""
        content_id = fields.StringField(attribute="_id")
        file_id = fields.StringField(required=True)
        batch_name = fields.StringField(required=True)
        subject = fields.StringField(required=True)
        chapter_no = fields.StringField(allow_none=True)
        content_type = fields.StringField(required=True)
        views = fields.IntegerField(default_factory=lambda: 0)
        downloads = fields.IntegerField(default_factory=lambda: 0)
        created_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [("file_id",), ("batch_name",), ("content_type",)]
            collection_name = "content_analytics"

    @instance.register
    class BotSettings(Document):
        """Bot settings collection"""
        setting_id = fields.StringField(attribute="_id")
        setting_name = fields.StringField(required=True, unique=True)
        setting_value = fields.StringField(required=True)
        description = fields.StringField(allow_none=True)
        updated_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [("setting_name",)]
            collection_name = "bot_settings"

    @instance.register
    class JoinRequests(Document):
        """Join requests collection"""
        request_id = fields.StringField(attribute="_id")
        user_id = fields.IntegerField(required=True)
        username = fields.StringField(allow_none=True)
        first_name = fields.StringField(allow_none=True)
        batch_name = fields.StringField(required=True)
        status = fields.StringField(default_factory=lambda: "pending", choices=["pending", "approved", "rejected"])
        requested_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        processed_at = fields.DateTimeField(allow_none=True)
        processed_by = fields.IntegerField(allow_none=True)
        
        class Meta:
            indexes = [("user_id",), ("batch_name",), ("status",)]
            collection_name = "join_requests"

    @instance.register
    class Chats(Document):
        """Chats collection"""
        chat_id = fields.IntegerField(attribute="_id")
        chat_type = fields.StringField(required=True, choices=["private", "group", "supergroup", "channel"])
        title = fields.StringField(allow_none=True)
        username = fields.StringField(allow_none=True)
        is_active = fields.BooleanField(default_factory=lambda: True)
        joined_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [("chat_type",), ("username",), ("is_active",)]
            collection_name = "chats"

    @instance.register
    class GroupSettings(Document):
        """Group settings collection"""
        group_id = fields.IntegerField(attribute="_id")
        group_name = fields.StringField(required=True)
        allowed_batches = fields.ListField(fields.StringField(), default_factory=list)
        allowed_subjects = fields.ListField(fields.StringField(), default_factory=list)
        auto_approve_requests = fields.BooleanField(default_factory=lambda: False)
        is_active = fields.BooleanField(default_factory=lambda: True)
        updated_at = fields.DateTimeField(default_factory=lambda: datetime.now(timezone.utc))
        
        class Meta:
            indexes = [("group_name",), ("is_active",)]
            collection_name = "group_settings"

else:
    # Placeholder classes when database is not available
    class StudyFiles:
        pass
    class Batches:
        pass
    class Chapters:
        pass
    class Users:
        pass
    class StudySessions:
        pass
    class ContentAnalytics:
        pass
    class BotSettings:
        pass
    class JoinRequests:
        pass
    class Chats:
        pass
    class GroupSettings:
        pass

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
        # Create indexes for all registered documents
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
        
        # Create text index for search, handling if it already exists
        if db:
            try:
                await db[COLLECTION_NAME].create_index([("file_name", "text"), ("caption", "text")])
            except Exception as e:
                if "name already exists" in str(e) or "IndexKeySpecsConflict" in str(e):
                    logger.warning(f"Text index already exists or conflicts: {e}")
                else:
                    raise
        
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

# Additional utility functions for plugins
async def get_study_files(limit=10, skip=0, batch_name=None, subject=None, content_type=None):
    """Get study files with optional filtering"""
    if not instance:
        logger.warning("Database not initialized - cannot get study files")
        return []
        
    try:
        filter_query = {"is_active": True}
        if batch_name:
            filter_query["batch_name"] = batch_name
        if subject:
            filter_query["subject"] = subject
        if content_type:
            filter_query["content_type"] = content_type
            
        files = await StudyFiles.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
        return files
    except Exception as e:
        logger.error(f"Error getting study files: {e}")
        return []

async def search_study_files(query, limit=10, skip=0, batch_name=None, subject=None):
    """Search study files by query"""
    if not instance:
        logger.warning("Database not initialized - cannot search study files")
        return []
        
    try:
        # Create text search query
        search_query = {
            "$text": {"$search": query},
            "is_active": True
        }
        
        if batch_name:
            search_query["batch_name"] = batch_name
        if subject:
            search_query["subject"] = subject
            
        files = await StudyFiles.find(search_query).skip(skip).limit(limit).to_list(length=limit)
        return files
    except Exception as e:
        logger.error(f"Error searching study files: {e}")
        return []

async def get_batch_info(batch_name):
    """Get batch information"""
    if not instance:
        logger.warning("Database not initialized - cannot get batch info")
        return None
        
    try:
        batch = await Batches.find_one({"batch_name": batch_name, "is_active": True})
        return batch
    except Exception as e:
        logger.error(f"Error getting batch info: {e}")
        return None

async def create_batch(batch_name, description=None, subjects=None, teachers=None, created_by=None):
    """Create a new batch"""
    if not instance:
        logger.warning("Database not initialized - cannot create batch")
        return False
        
    try:
        # Check if batch already exists
        existing_batch = await Batches.find_one({"batch_name": batch_name})
        if existing_batch:
            logger.warning(f"Batch already exists: {batch_name}")
            return False
            
        # Create new batch
        batch_doc = Batches(
            batch_id=f"batch_{batch_name.lower().replace(' ', '_')}",
            batch_name=batch_name,
            description=description,
            subjects=subjects or DEFAULT_SUBJECTS,
            teachers=teachers or DEFAULT_TEACHERS
        )
        
        await batch_doc.commit()
        logger.info(f"Batch created: {batch_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating batch: {e}")
        return False

# Alias for save_study_file to match plugin expectations
save_file = save_study_file
