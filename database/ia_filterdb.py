import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from typing import Dict, List
from collections import defaultdict
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from marshmallow import ValidationError
from datetime import datetime, timedelta
import logging

# Try to import motor with error handling
try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError as e:
    print(f"Warning: Could not import motor in ia_filterdb.py: {e}")
    AsyncIOMotorClient = None

# Try to import config with error handling
try:
    from config import *
except ImportError as e:
    print(f"Warning: Could not import config in ia_filterdb.py: {e}")
    # Fallback configuration values
    DATABASE_URI = ""
    DATABASE_URI2 = ""
    DATABASE_NAME = "StudyBotDB"
    COLLECTION_NAME = "media_files"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global cache for DB size
_db_stats_cache = {"timestamp": None, "primary_size": 0.0}

# Initialize variables to None first
client = None
db = None
instance = None
client2 = None
db2 = None
instance2 = None

# Primary DB - Initialize with error handling
try:
    if AsyncIOMotorClient and DATABASE_URI:
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
except Exception as e:
    print(f"Warning: Could not initialize primary database connection in ia_filterdb.py: {e}")
    client = None
    db = None
    instance = None

# Secondary DB - Initialize with error handling
try:
    if AsyncIOMotorClient and DATABASE_URI2:
        client2 = AsyncIOMotorClient(DATABASE_URI2)
        raw_db2 = client2[DATABASE_NAME]
        instance2 = Instance.from_db(raw_db2)
        
        # Create a custom wrapper that doesn't expose command method
        class DatabaseWrapper2:
            def __init__(self, database):
                self._db = database
                # Copy all attributes except command
                for attr in dir(database):
                    if not attr.startswith('_') and attr != 'command':
                        setattr(self, attr, getattr(database, attr))
            
            def __getattr__(self, name):
                if name == 'command':
                    raise AttributeError("'DatabaseWrapper2' object has no attribute 'command'")
                return getattr(self._db, name)
        
        db2 = DatabaseWrapper2(raw_db2)
except Exception as e:
    print(f"Warning: Could not initialize secondary database connection in ia_filterdb.py: {e}")
    client2 = None
    db2 = None
    instance2 = None

# Only register document classes if instances are available
if instance:
    @instance.register
    class Media(Document):
        """Media document for primary database"""
        file_id = fields.StringField(attribute="_id")
        file_ref = fields.StringField(allow_none=True)
        file_name = fields.StringField(required=True)
        file_size = fields.IntegerField(required=True)
        file_type = fields.StringField(allow_none=True)
        mime_type = fields.StringField(allow_none=True)
        caption = fields.StringField(allow_none=True)

        class Meta:
            indexes = ("$file_name",)
            collection_name = COLLECTION_NAME
else:
    class Media:
        pass

if instance2:
    @instance2.register
    class Media2(Document):
        """Media document for secondary database"""
        file_id = fields.StringField(attribute="_id")
        file_ref = fields.StringField(allow_none=True)
        file_name = fields.StringField(required=True)
        file_size = fields.IntegerField(required=True)
        file_type = fields.StringField(allow_none=True)
        mime_type = fields.StringField(allow_none=True)
        caption = fields.StringField(allow_none=True)

        class Meta:
            indexes = ("$file_name",)
            collection_name = COLLECTION_NAME
else:
    class Media2:
        pass

async def check_db_size(db):
    """Check database size and cache results"""
    try:
        now = datetime.utcnow()
        cache_stale_by_time = _db_stats_cache["timestamp"] is None or (
            now - _db_stats_cache["timestamp"] > timedelta(minutes=10)
        )
        refresh_if_size_threshold = _db_stats_cache["primary_size"] >= 10.0
        if not cache_stale_by_time and not refresh_if_size_threshold:
            return _db_stats_cache["primary_size"]
        stats = await db.command("dbstats")
        db_logical_size = stats["dataSize"]
        db_index_size = stats["indexSize"]
        db_logical_size_mb = db_logical_size / (1024 * 1024)
        db_index_size_mb = db_index_size / (1024 * 1024)
        db_size_mb = db_logical_size_mb + db_index_size_mb
        _db_stats_cache["primary_size"] = db_size_mb
        _db_stats_cache["timestamp"] = now
        return db_size_mb
    except Exception as e:
        logger.error(f"Error Checking Database Size: {e}")
        return 0

def unpack_new_file_id(file_id):
    """Unpack new file ID format"""
    decoded = FileId.decode(file_id)
    file_type = decoded.file_type
    media_id = decoded.media_id
    access_hash = decoded.access_hash
    file_reference = decoded.file_reference
    return media_id, file_reference

async def save_file(media):
    """Save file in database, with detailed logging."""
    try:
        file_id, file_ref = unpack_new_file_id(media.file_id)
        file_name = re.sub(
            r"[_\-\.#+$%^&*()!~`,;:\"'?/<>\[\]{}=|\\]", " ", str(media.file_name)
        )
        file_name = re.sub(r"\s+", " ", file_name).strip()
        
        saveMedia = Media
        target_db = "Primary"
        
        if MULTIPLE_DB:
            try:
                exists = await Media.count_documents({"file_id": file_id}, limit=1)
                if exists:
                    saveMedia = Media2
                    target_db = "Secondary"
                else:
                    saveMedia = Media
                    target_db = "Primary"
            except Exception as e:
                logger.error(f"Error checking secondary DB: {e}")
                saveMedia = Media
                target_db = "Primary"
        
        file_data = {
            "file_id": file_id,
            "file_ref": file_ref,
            "file_name": file_name,
            "file_size": media.file_size,
            "file_type": media.file_type,
            "mime_type": media.mime_type,
            "caption": media.caption if hasattr(media, 'caption') else None
        }
        
        try:
            await saveMedia(**file_data).commit()
            logger.info(f"File saved successfully in {target_db} DB: {file_name}")
            return True
        except DuplicateKeyError:
            logger.info(f"File already exists in {target_db} DB: {file_name}")
            return False
        except Exception as e:
            logger.error(f"Error saving file in {target_db} DB: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error in save_file: {e}")
        return False

async def get_file_details(file_id):
    """Get file details from database"""
    try:
        # Try primary DB first
        file_data = await Media.find_one({"file_id": file_id})
        if file_data:
            return file_data, "Primary"
        
        # Try secondary DB if multiple DB is enabled
        if MULTIPLE_DB:
            file_data = await Media2.find_one({"file_id": file_id})
            if file_data:
                return file_data, "Secondary"
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error getting file details: {e}")
        return None, None

async def search_files(query, limit=50):
    """Search files by name or caption"""
    try:
        results = []
        
        # Search in primary DB
        primary_results = await Media.find({"$text": {"$search": query}}).limit(limit).to_list(length=limit)
        results.extend(primary_results)
        
        # Search in secondary DB if enabled
        if MULTIPLE_DB:
            secondary_results = await Media2.find({"$text": {"$search": query}}).limit(limit).to_list(length=limit)
            results.extend(secondary_results)
        
        # Remove duplicates based on file_id
        seen = set()
        unique_results = []
        for result in results:
            if result.file_id not in seen:
                seen.add(result.file_id)
                unique_results.append(result)
        
        return unique_results[:limit]
        
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        return []

async def delete_file(file_id):
    """Delete file from database"""
    try:
        deleted_count = 0
        
        # Delete from primary DB
        result = await Media.delete_one({"file_id": file_id})
        if result.deleted_count > 0:
            deleted_count += result.deleted_count
            logger.info(f"File deleted from Primary DB: {file_id}")
        
        # Delete from secondary DB if enabled
        if MULTIPLE_DB:
            result = await Media2.delete_one({"file_id": file_id})
            if result.deleted_count > 0:
                deleted_count += result.deleted_count
                logger.info(f"File deleted from Secondary DB: {file_id}")
        
        return deleted_count > 0
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False

async def get_file_stats():
    """Get file statistics from database"""
    try:
        stats = {}
        
        # Primary DB stats
        primary_count = await Media.count_documents({})
        primary_size = await check_db_size(db)
        stats["primary"] = {"count": primary_count, "size_mb": primary_size}
        
        # Secondary DB stats if enabled
        if MULTIPLE_DB:
            secondary_count = await Media2.count_documents({})
            secondary_size = await check_db_size(db2)
            stats["secondary"] = {"count": secondary_count, "size_mb": secondary_size}
        
        # Total stats
        total_count = primary_count
        if MULTIPLE_DB:
            total_count += secondary_count
        
        stats["total"] = {"count": total_count}
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting file stats: {e}")
        return {}

async def cleanup_old_files(days_old=30):
    """Clean up old files from database"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Clean primary DB
        primary_result = await Media.delete_many({"uploaded_at": {"$lt": cutoff_date}})
        primary_deleted = primary_result.deleted_count
        
        # Clean secondary DB if enabled
        secondary_deleted = 0
        if MULTIPLE_DB:
            secondary_result = await Media2.delete_many({"uploaded_at": {"$lt": cutoff_date}})
            secondary_deleted = secondary_result.deleted_count
        
        total_deleted = primary_deleted + secondary_deleted
        
        if total_deleted > 0:
            logger.info(f"Cleaned up {total_deleted} old files ({primary_deleted} primary, {secondary_deleted} secondary)")
        
        return total_deleted
        
    except Exception as e:
        logger.error(f"Error cleaning up old files: {e}")
        return 0

async def get_file_by_name(file_name):
    """Get file by exact name match"""
    try:
        # Try primary DB first
        file_data = await Media.find_one({"file_name": file_name})
        if file_data:
            return file_data, "Primary"
        
        # Try secondary DB if multiple DB is enabled
        if MULTIPLE_DB:
            file_data = await Media2.find_one({"file_name": file_name})
            if file_data:
                return file_data, "Secondary"
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error getting file by name: {e}")
        return None, None

async def update_file_caption(file_id, new_caption):
    """Update file caption in database"""
    try:
        updated_count = 0
        
        # Update in primary DB
        result = await Media.update_one(
            {"file_id": file_id},
            {"$set": {"caption": new_caption}}
        )
        if result.modified_count > 0:
            updated_count += result.modified_count
        
        # Update in secondary DB if enabled
        if MULTIPLE_DB:
            result = await Media2.update_one(
                {"file_id": file_id},
                {"$set": {"caption": new_caption}}
            )
            if result.modified_count > 0:
                updated_count += result.modified_count
        
        return updated_count > 0
        
    except Exception as e:
        logger.error(f"Error updating file caption: {e}")
        return False

async def get_files_by_type(file_type, limit=50):
    """Get files by specific type"""
    try:
        results = []
        
        # Get from primary DB
        primary_results = await Media.find({"file_type": file_type}).limit(limit).to_list(length=limit)
        results.extend(primary_results)
        
        # Get from secondary DB if enabled
        if MULTIPLE_DB:
            secondary_results = await Media2.find({"file_type": file_type}).limit(limit).to_list(length=limit)
            results.extend(secondary_results)
        
        # Remove duplicates and limit results
        seen = set()
        unique_results = []
        for result in results:
            if result.file_id not in seen:
                seen.add(result.file_id)
                unique_results.append(result)
        
        return unique_results[:limit]
        
    except Exception as e:
        logger.error(f"Error getting files by type: {e}")
        return []

async def get_files_by_size_range(min_size, max_size, limit=50):
    """Get files within a size range"""
    try:
        results = []
        
        # Get from primary DB
        primary_results = await Media.find({
            "file_size": {"$gte": min_size, "$lte": max_size}
        }).limit(limit).to_list(length=limit)
        results.extend(primary_results)
        
        # Get from secondary DB if enabled
        if MULTIPLE_DB:
            secondary_results = await Media2.find({
                "file_size": {"$gte": min_size, "$lte": max_size}
            }).limit(limit).to_list(length=limit)
            results.extend(secondary_results)
        
        # Remove duplicates and limit results
        seen = set()
        unique_results = []
        for result in results:
            if result.file_id not in seen:
                seen.add(result.file_id)
                unique_results.append(result)
        
        return unique_results[:limit]
        
    except Exception as e:
        logger.error(f"Error getting files by size range: {e}")
        return []

async def create_text_indexes():
    """Create text indexes for search functionality"""
    try:
        # Create text index on primary DB
        await db[COLLECTION_NAME].create_index([("file_name", "text"), ("caption", "text")])
        logger.info("Text indexes created on primary DB")
        
        # Create text index on secondary DB if enabled
        if MULTIPLE_DB:
            await db2[COLLECTION_NAME].create_index([("file_name", "text"), ("caption", "text")])
            logger.info("Text indexes created on secondary DB")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating text indexes: {e}")
        return False

async def get_database_info():
    """Get comprehensive database information"""
    try:
        info = {}
        
        # Primary DB info
        primary_stats = await db.command("dbstats")
        primary_collections = await db.list_collection_names()
        info["primary"] = {
            "name": db.name,
            "collections": primary_collections,
            "data_size_mb": primary_stats.get("dataSize", 0) / (1024 * 1024),
            "index_size_mb": primary_stats.get("indexSize", 0) / (1024 * 1024),
            "storage_size_mb": primary_stats.get("storageSize", 0) / (1024 * 1024)
        }
        
        # Secondary DB info if enabled
        if MULTIPLE_DB:
            secondary_stats = await db2.command("dbstats")
            secondary_collections = await db2.list_collection_names()
            info["secondary"] = {
                "name": db2.name,
                "collections": secondary_collections,
                "data_size_mb": secondary_stats.get("dataSize", 0) / (1024 * 1024),
                "index_size_mb": secondary_stats.get("indexSize", 0) / (1024 * 1024),
                "storage_size_mb": secondary_stats.get("storageSize", 0) / (1024 * 1024)
            }
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {}
