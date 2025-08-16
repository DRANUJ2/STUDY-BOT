import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from config import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Database connections
client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

# Secondary database if enabled
if MULTIPLE_DB:
    client2 = AsyncIOMotorClient(DATABASE_URI2)
    db2 = client2[DATABASE_NAME]
    instance2 = Instance.from_db(db2)

@instance.register
class StudyFiles(Document):
    """Main collection for study files"""
    file_id = fields.StrField(attribute="_id")
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)
    
    # Study specific fields
    batch_name = fields.StrField(required=True)
    subject = fields.StrField(required=True)
    teacher = fields.StrField(allow_none=True)
    chapter_no = fields.StrField(allow_none=True)
    chapter_name = fields.StrField(allow_none=True)
    lecture_no = fields.StrField(allow_none=True)
    content_type = fields.StrField(required=True)  # NOTES, DPP, LECTURE, etc.
    tags = fields.ListField(fields.StrField(), default=[])
    
    # Metadata
    uploaded_by = fields.IntField(required=True)
    uploaded_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    is_active = fields.BoolField(default=True)
    
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
    batch_id = fields.StrField(attribute="_id")
    batch_name = fields.StrField(required=True, unique=True)
    batch_image = fields.StrField(allow_none=True)
    batch_caption = fields.StrField(allow_none=True)
    subjects = fields.ListField(fields.StrField(), default=DEFAULT_SUBJECTS)
    teachers = fields.ListField(fields.StrField(), default=DEFAULT_TEACHERS)
    is_active = fields.BoolField(default=True)
    created_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    created_by = fields.IntField(required=True)
    
    class Meta:
        indexes = [("batch_name",), ("is_active",)]
        collection_name = "batches"

@instance.register
class Chapters(Document):
    """Collection for chapter information"""
    chapter_id = fields.StrField(attribute="_id")
    batch_name = fields.StrField(required=True)
    subject = fields.StrField(required=True)
    chapter_no = fields.StrField(required=True)
    chapter_name = fields.StrField(required=True)
    total_lectures = fields.IntField(default=0)
    total_dpp = fields.IntField(default=0)
    total_notes = fields.IntField(default=0)
    is_active = fields.BoolField(default=True)
    created_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    class Meta:
        indexes = [
            ("batch_name", "subject", "chapter_no"),
            ("is_active",)
        ]
        collection_name = "chapters"

@instance.register
class Users(Document):
    """Collection for user information and progress"""
    user_id = fields.IntField(attribute="_id")
    first_name = fields.StrField(required=True)
    last_name = fields.StrField(allow_none=True)
    username = fields.StrField(allow_none=True)
    is_premium = fields.BoolField(default=False)
    premium_expiry = fields.DateTimeField(allow_none=True)
    current_batch = fields.StrField(allow_none=True)
    study_progress = fields.DictField(default={})
    total_downloads = fields.IntField(default=0)
    total_time_spent = fields.IntField(default=0)  # in minutes
    achievements = fields.ListField(fields.StrField(), default=[])
    joined_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    last_active = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    banned = fields.BoolField(default=False)
    ban_reason = fields.StrField(allow_none=True)
    banned_by = fields.IntField(allow_none=True)
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
    session_id = fields.StrField(attribute="_id")
    user_id = fields.IntField(required=True)
    batch_name = fields.StrField(required=True)
    subject = fields.StrField(required=True)
    chapter_no = fields.StrField(required=True)
    content_type = fields.StrField(required=True)
    start_time = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    end_time = fields.DateTimeField(allow_none=True)
    duration = fields.IntField(default=0)  # in minutes
    files_accessed = fields.ListField(fields.StrField(), default=[])
    
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
    content_id = fields.StrField(attribute="_id")
    file_id = fields.StrField(required=True)
    batch_name = fields.StrField(required=True)
    subject = fields.StrField(required=True)
    chapter_no = fields.StrField(required=True)
    content_type = fields.StrField(required=True)
    total_views = fields.IntField(default=0)
    total_downloads = fields.IntField(default=0)
    unique_viewers = fields.ListField(fields.IntField(), default=[])
    rating = fields.FloatField(default=0.0)
    total_ratings = fields.IntField(default=0)
    feedback = fields.ListField(fields.DictField(), default=[])
    last_accessed = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
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
    setting_id = fields.StrField(attribute="_id")
    setting_name = fields.StrField(required=True, unique=True)
    setting_value = fields.RawField(required=True)
    setting_type = fields.StrField(required=True)  # string, int, bool, list, dict
    description = fields.StrField(allow_none=True)
    updated_by = fields.IntField(required=True)
    updated_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    class Meta:
        indexes = [("setting_name",), ("updated_at",)]
        collection_name = "bot_settings"

@instance.register
class JoinRequests(Document):
    """Collection for join requests"""
    request_id = fields.StrField(attribute="_id")
    user_id = fields.IntField(required=True)
    chat_id = fields.IntField(required=True)
    chat_title = fields.StrField(required=True)
    chat_type = fields.StrField(required=True)
    user_first_name = fields.StrField(required=True)
    user_last_name = fields.StrField(allow_none=True)
    user_username = fields.StrField(allow_none=True)
    status = fields.StrField(default="pending")  # pending, approved, rejected
    requested_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    processed_at = fields.DateTimeField(allow_none=True)
    processed_by = fields.IntField(allow_none=True)
    notes = fields.StrField(allow_none=True)
    
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
    chat_id = fields.IntField(attribute="_id")
    chat_title = fields.StrField(required=True)
    chat_type = fields.StrField(required=True)  # group, supergroup, channel
    is_active = fields.BoolField(default=True)
    member_count = fields.IntField(default=0)
    created_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    last_activity = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
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
    group_id = fields.IntField(attribute="_id")
    welcome = fields.BoolField(default=True)
    auto_delete = fields.BoolField(default=False)
    auto_filter = fields.BoolField(default=True)
    pm_filter = fields.BoolField(default=True)
    auto_search = fields.BoolField(default=True)
    welcome_message = fields.BoolField(default=True)
    created_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    class Meta:
        indexes = [("group_id",), ("auto_filter",)]
        collection_name = "group_settings"

# Secondary database models if enabled
if MULTIPLE_DB:
    @instance2.register
    class StudyFiles2(StudyFiles):
        class Meta:
            collection_name = COLLECTION_NAME

# Database utility functions
async def save_study_file(media, batch_name, subject, teacher=None, 
                         chapter_no=None, chapter_name=None, lecture_no=None, 
                         content_type="NOTES", tags=None, uploaded_by=None):
    """Save study file in database"""
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

async def get_study_files(batch_name=None, subject=None, chapter_no=None, 
                         content_type=None, limit=50, skip=0):
    """Get study files with filters"""
    try:
        filter_query = {"is_active": True}
        
        if batch_name:
            filter_query["batch_name"] = batch_name
        if subject:
            filter_query["subject"] = subject
        if chapter_no:
            filter_query["chapter_no"] = chapter_no
        if content_type:
            filter_query["content_type"] = content_type
            
        cursor = StudyFiles.find(filter_query).skip(skip).limit(limit).sort("uploaded_at", -1)
        files = await cursor.to_list(length=limit)
        
        return files
        
    except Exception as e:
        logger.error(f"Error getting study files: {e}")
        return []

async def search_study_files(query, batch_name=None, subject=None, limit=20):
    """Search study files with text query"""
    try:
        # Create text search query
        search_query = {
            "$text": {"$search": query}
        }
        
        if batch_name:
            search_query["batch_name"] = batch_name
        if subject:
            search_query["subject"] = subject
            
        cursor = StudyFiles.find(search_query).limit(limit).sort("score", {"$meta": "textScore"})
        files = await cursor.to_list(length=limit)
        
        return files
        
    except Exception as e:
        logger.error(f"Error searching study files: {e}")
        return []

async def get_batch_info(batch_name):
    """Get batch information"""
    try:
        batch = await Batches.find_one({"batch_name": batch_name, "is_active": True})
        return batch
    except Exception as e:
        logger.error(f"Error getting batch info: {e}")
        return None

async def create_batch(batch_name, batch_image=None, batch_caption=None, 
                      subjects=None, teachers=None, created_by=None):
    """Create new batch"""
    try:
        batch_doc = Batches(
            batch_id=f"batch_{batch_name.lower().replace(' ', '_')}",
            batch_name=batch_name,
            batch_image=batch_image,
            batch_caption=batch_caption,
            subjects=subjects or DEFAULT_SUBJECTS,
            teachers=teachers or DEFAULT_TEACHERS,
            created_by=created_by or 0
        )
        
        await batch_doc.commit()
        logger.info(f"Batch created: {batch_name}")
        return True
        
    except DuplicateKeyError:
        logger.warning(f"Batch already exists: {batch_name}")
        return False
    except Exception as e:
        logger.error(f"Error creating batch: {e}")
        return False

async def update_user_progress(user_id, batch_name, subject, chapter_no, 
                             content_type, duration=0):
    """Update user study progress"""
    try:
        user = await Users.find_one({"_id": user_id})
        if not user:
            return False
            
        # Update progress
        progress_key = f"{batch_name}.{subject}.{chapter_no}"
        if progress_key not in user.study_progress:
            user.study_progress[progress_key] = {}
            
        user.study_progress[progress_key][content_type] = user.study_progress[progress_key].get(content_type, 0) + 1
        user.total_time_spent += duration
        user.last_active = datetime.now(timezone.utc)
        
        await user.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error updating user progress: {e}")
        return False

async def ensure_indexes():
    """Ensure all database indexes are created"""
    try:
        await StudyFiles.ensure_indexes()
        await Batches.ensure_indexes()
        await Chapters.ensure_indexes()
        await Users.ensure_indexes()
        await StudySessions.ensure_indexes()
        await ContentAnalytics.ensure_indexes()
        await BotSettings.ensure_indexes()
        await JoinRequests.ensure_indexes()
        await Chats.ensure_indexes() # Added Chats index
        await GroupSettings.ensure_indexes() # Added GroupSettings index
        
        # Create text index for search
        await db[COLLECTION_NAME].create_index([("file_name", "text"), ("caption", "text")])
        
        logger.info("All database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

# Initialize database
async def init_db():
    """Initialize database connection and indexes"""
    try:
        await ensure_indexes()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

async def get_batch(batch_name):
    """Get batch information (alias for get_batch_info)"""
    return await get_batch_info(batch_name)

async def add_batch(batch_name, batch_data):
    """Add new batch with data dictionary"""
    try:
        batch_doc = Batches(
            batch_id=f"batch_{batch_name.lower().replace(' ', '_')}",
            batch_name=batch_name,
            batch_image=batch_data.get('batch_image'),
            batch_caption=batch_data.get('batch_caption'),
            subjects=batch_data.get('subjects', DEFAULT_SUBJECTS),
            teachers=batch_data.get('teachers', DEFAULT_TEACHERS),
            created_by=batch_data.get('created_by', 0)
        )
        
        await batch_doc.commit()
        logger.info(f"Batch added: {batch_name}")
        return True
        
    except DuplicateKeyError:
        logger.warning(f"Batch already exists: {batch_name}")
        return False
    except Exception as e:
        logger.error(f"Error adding batch: {e}")
        return False

async def get_user(user_id):
    """Get user by ID"""
    try:
        user = await Users.find_one({"_id": user_id})
        return user
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None

async def add_user(user_id, first_name, last_name=None, username=None):
    """Add new user"""
    try:
        user_doc = Users(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        
        await user_doc.commit()
        logger.info(f"User added: {user_id} ({first_name})")
        return True
        
    except DuplicateKeyError:
        logger.warning(f"User already exists: {user_id}")
        return False
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False

async def update_user(user_id, update_data):
    """Update user data"""
    try:
        user = await Users.find_one({"_id": user_id})
        if not user:
            return False
            
        # Update fields
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        await user.commit()
        logger.info(f"User updated: {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return False

async def total_users_count():
    """Get total users count"""
    try:
        count = await Users.count_documents({})
        return count
    except Exception as e:
        logger.error(f"Error getting total users count: {e}")
        return 0

async def total_chat_count():
    """Get total chat count"""
    try:
        # This would typically count groups/channels
        # For now, return 0 as we don't have a chats collection
        return 0
    except Exception as e:
        logger.error(f"Error getting total chat count: {e}")
        return 0

async def total_files_count():
    """Get total files count"""
    try:
        count = await StudyFiles.count_documents({"is_active": True})
        return count
    except Exception as e:
        logger.error(f"Error getting total files count: {e}")
        return 0

async def get_all_users():
    """Get all users"""
    try:
        cursor = Users.find({})
        users = await cursor.to_list(length=None)
        return [{"user_id": user.user_id, "id": user.user_id} for user in users]
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []

async def get_all_chats():
    """Get all chats"""
    try:
        # This would typically return groups/channels
        # For now, return empty list as we don't have a chats collection
        return []
    except Exception as e:
        logger.error(f"Error getting all chats: {e}")
        return []

async def get_banned_users():
    """Get all banned users"""
    try:
        cursor = Users.find({"banned": True})
        users = await cursor.to_list(length=None)
        return users
    except Exception as e:
        logger.error(f"Error getting banned users: {e}")
        return []

async def ban_user(user_id, reason, banned_by):
    """Ban a user"""
    try:
        user = await Users.find_one({"_id": user_id})
        if not user:
            return False
            
        user.banned = True
        user.ban_reason = reason
        user.banned_by = banned_by
        user.banned_at = datetime.now(timezone.utc)
        
        await user.commit()
        logger.info(f"User banned: {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error banning user {user_id}: {e}")
        return False

async def get_ban_status(user_id):
    """Get user ban status"""
    try:
        user = await Users.find_one({"_id": user_id})
        if not user:
            return {"is_banned": False}
            
        return {
            "is_banned": getattr(user, 'banned', False),
            "ban_reason": getattr(user, 'ban_reason', None),
            "banned_by": getattr(user, 'banned_by', None),
            "banned_at": getattr(user, 'banned_at', None)
        }
        
    except Exception as e:
        logger.error(f"Error getting ban status for user {user_id}: {e}")
        return {"is_banned": False}

async def remove_ban(user_id):
    """Remove ban from user"""
    try:
        user = await Users.find_one({"_id": user_id})
        if not user:
            return False
            
        user.banned = False
        user.ban_reason = None
        user.banned_by = None
        user.banned_at = None
        
        await user.commit()
        logger.info(f"User ban removed: {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error removing ban for user {user_id}: {e}")
        return False

async def add_join_request(user_id, chat_id, user_name, chat_title):
    """Add join request"""
    try:
        request_doc = JoinRequests(
            request_id=f"req_{user_id}_{chat_id}_{int(datetime.now(timezone.utc).timestamp())}",
            user_id=user_id,
            chat_id=chat_id,
            user_first_name=user_name.split(' ')[0], # Assuming user_name is "First Last"
            user_last_name=user_name.split(' ')[1] if len(user_name.split(' ')) > 1 else None,
            user_username=None, # Not available in this context
            chat_title=chat_title,
            chat_type="group" # Assuming it's a group for now
        )
        
        await request_doc.commit()
        logger.info(f"Join request added: {user_id} -> {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding join request: {e}")
        return False

async def update_join_request(user_id, chat_id, update_data):
    """Update join request"""
    try:
        request = await JoinRequests.find_one({"user_id": user_id, "chat_id": chat_id})
        if not request:
            return False
            
        # Update fields
        for key, value in update_data.items():
            if hasattr(request, key):
                setattr(request, key, value)
        
        await request.commit()
        logger.info(f"Join request updated: {user_id} -> {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating join request: {e}")
        return False

async def get_pending_join_requests():
    """Get pending join requests"""
    try:
        cursor = JoinRequests.find({"status": "pending"}).sort("requested_at", -1)
        requests = await cursor.to_list(length=None)
        return requests
    except Exception as e:
        logger.error(f"Error getting pending join requests: {e}")
        return []

async def get_all_join_requests():
    """Get all join requests"""
    try:
        cursor = JoinRequests.find({}).sort("requested_at", -1)
        requests = await cursor.to_list(length=None)
        return requests
    except Exception as e:
        logger.error(f"Error getting all join requests: {e}")
        return []

async def add_chat(chat_id, chat_title, chat_type="group"):
    """Add new chat"""
    try:
        chat_doc = Chats(
            chat_id=chat_id,
            chat_title=chat_title,
            chat_type=chat_type
        )
        
        await chat_doc.commit()
        logger.info(f"Chat added: {chat_id} ({chat_title})")
        return True
        
    except DuplicateKeyError:
        logger.warning(f"Chat already exists: {chat_id}")
        return False
    except Exception as e:
        logger.error(f"Error adding chat: {e}")
        return False

async def get_chat(chat_id):
    """Get chat by ID"""
    try:
        chat = await Chats.find_one({"_id": chat_id})
        return chat
    except Exception as e:
        logger.error(f"Error getting chat {chat_id}: {e}")
        return None

async def update_chat(chat_id, update_data):
    """Update chat data"""
    try:
        chat = await Chats.find_one({"_id": chat_id})
        if not chat:
            return False
            
        # Update fields
        for key, value in update_data.items():
            if hasattr(chat, key):
                setattr(chat, key, value)
        
        await chat.commit()
        logger.info(f"Chat updated: {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating chat {chat_id}: {e}")
        return False

async def get_settings(group_id):
    """Get group settings"""
    try:
        settings = await GroupSettings.find_one({"_id": group_id})
        if not settings:
            # Create default settings
            settings_doc = GroupSettings(
                group_id=group_id,
                welcome=True,
                auto_delete=False,
                auto_filter=True,
                pm_filter=True,
                auto_search=True,
                welcome_message=True
            )
            await settings_doc.commit()
            return settings_doc
        return settings
    except Exception as e:
        logger.error(f"Error getting settings for group {group_id}: {e}")
        return None

async def save_group_settings(group_id, **kwargs):
    """Save group settings"""
    try:
        settings = await GroupSettings.find_one({"_id": group_id})
        if not settings:
            # Create new settings
            settings_doc = GroupSettings(
                group_id=group_id,
                **kwargs
            )
            await settings_doc.commit()
            return True
        
        # Update existing settings
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.updated_at = datetime.now(timezone.utc)
        await settings.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error saving settings for group {group_id}: {e}")
        return False

async def save_file(media):
    """Save file to database (compatibility method)"""
    try:
        # This is a compatibility method for the index plugin
        # It should save the file to the study database
        file_id = str(media.file_id)
        file_name = media.file_name or "Unknown"
        file_size = media.file_size or 0
        
        # Create basic file document
        file_doc = StudyFiles(
            file_id=file_id,
            file_name=file_name,
            file_size=file_size,
            file_type="unknown",
            batch_name="default",
            subject="general",
            content_type="FILE",
            uploaded_by=0
        )
        
        await file_doc.commit()
        logger.info(f"File saved: {file_name}")
        return True
        
    except DuplicateKeyError:
        logger.warning(f"File already exists: {file_id}")
        return False
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return False

async def connect_group(group_id, user_id):
    """Connect user to group (compatibility method)"""
    try:
        # This is a compatibility method for the p_ttishow plugin
        # It should create a connection between user and group
        # For now, we'll just log the connection
        logger.info(f"User {user_id} connected to group {group_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error connecting user {user_id} to group {group_id}: {e}")
        return False

async def disable_chat(chat_id, reason="No Reason"):
    """Disable a chat"""
    try:
        chat = await Chats.find_one({"_id": chat_id})
        if not chat:
            return False
            
        chat.is_active = False
        await chat.commit()
        logger.info(f"Chat disabled: {chat_id} - {reason}")
        return True
        
    except Exception as e:
        logger.error(f"Error disabling chat {chat_id}: {e}")
        return False

async def enable_chat(chat_id):
    """Enable a chat"""
    try:
        chat = await Chats.find_one({"_id": chat_id})
        if not chat:
            return False
            
        chat.is_active = True
        await chat.commit()
        logger.info(f"Chat enabled: {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error enabling chat {chat_id}: {e}")
        return False

async def get_file_stats():
    """Get file statistics (compatibility method)"""
    try:
        # This is a compatibility method for the p_ttishow plugin
        total_files = await StudyFiles.count_documents({"is_active": True})
        
        return {
            "total": {
                "count": total_files
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting file stats: {e}")
        return {
            "total": {
                "count": 0
            }
        }
