import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

# Try to import motor with error handling
try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError as e:
    print(f"Warning: Could not import motor in topdb.py: {e}")
    AsyncIOMotorClient = None

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, uri, database_name):
        if AsyncIOMotorClient is None:
            raise ImportError("Motor is not available")
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database_name]
        
        # Remove the command method to prevent conflicts with filters.command
        if hasattr(self.db, 'command'):
            delattr(self.db, 'command')
            
        # Collections
        self.col = self.db.top_messages
        self.stats = self.db.stats
        self.analytics = self.db.analytics
        self.leaderboard = self.db.leaderboard

    async def update_top_messages(self, user_id, message_text):
        """Update top messages for user"""
        try:
            user = await self.col.find_one({"user_id": user_id, "messages.text": message_text})
            
            if not user:
                await self.col.update_one(
                    {"user_id": user_id},
                    {"$push": {"messages": {"text": message_text, "count": 1}}},
                    upsert=True
                )
            else:
                await self.col.update_one(
                    {"user_id": user_id, "messages.text": message_text},
                    {"$inc": {"messages.$.count": 1}}
                )
            return True
        except Exception as e:
            logger.error(f"Error updating top messages: {e}")
            return False

    async def get_top_messages(self, limit=30):
        """Get top messages by count"""
        try:
            pipeline = [
                {"$unwind": "$messages"},
                {"$group": {"_id": "$messages.text", "count": {"$sum": "$messages.count"}}},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            results = await self.col.aggregate(pipeline).to_list(limit)
            return [result['_id'] for result in results]
        except Exception as e:
            logger.error(f"Error getting top messages: {e}")
            return []
    
    async def delete_all_messages(self):
        """Delete all messages"""
        try:
            await self.col.delete_many({})
            return True
        except Exception as e:
            logger.error(f"Error deleting all messages: {e}")
            return False

    async def update_study_stats(self, user_id, subject, chapter, duration, content_type):
        """Update study statistics for user"""
        try:
            stats_data = {
                "user_id": user_id,
                "subject": subject,
                "chapter": chapter,
                "content_type": content_type,
                "duration": duration,
                "timestamp": datetime.utcnow()
            }
            
            await self.stats.insert_one(stats_data)
            return True
        except Exception as e:
            logger.error(f"Error updating study stats: {e}")
            return False

    async def get_user_study_stats(self, user_id, days=30):
        """Get user study statistics for specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"user_id": user_id, "timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": {
                        "subject": "$subject",
                        "chapter": "$chapter",
                        "content_type": "$content_type"
                    },
                    "total_duration": {"$sum": "$duration"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"total_duration": -1}}
            ]
            
            results = await self.stats.aggregate(pipeline).to_list(length=None)
            return results
        except Exception as e:
            logger.error(f"Error getting user study stats: {e}")
            return []

    async def get_top_students(self, limit=10, days=30):
        """Get top students by study time"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": "$user_id",
                    "total_duration": {"$sum": "$duration"},
                    "total_sessions": {"$sum": 1}
                }},
                {"$sort": {"total_duration": -1}},
                {"$limit": limit}
            ]
            
            results = await self.stats.aggregate(pipeline).to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Error getting top students: {e}")
            return []

    async def get_subject_stats(self, subject, days=30):
        """Get statistics for specific subject"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"subject": subject, "timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": "$chapter",
                    "total_duration": {"$sum": "$duration"},
                    "total_sessions": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$sort": {"total_duration": -1}}
            ]
            
            results = await self.stats.aggregate(pipeline).to_list(length=None)
            
            # Calculate unique user count for each chapter
            for result in results:
                result["unique_users_count"] = len(result["unique_users"])
                del result["unique_users"]
            
            return results
        except Exception as e:
            logger.error(f"Error getting subject stats: {e}")
            return []

    async def get_content_type_stats(self, content_type, days=30):
        """Get statistics for specific content type"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"content_type": content_type, "timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": {
                        "subject": "$subject",
                        "chapter": "$chapter"
                    },
                    "total_duration": {"$sum": "$duration"},
                    "total_sessions": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$sort": {"total_duration": -1}}
            ]
            
            results = await self.stats.aggregate(pipeline).to_list(length=None)
            
            # Calculate unique user count for each subject-chapter combination
            for result in results:
                result["unique_users_count"] = len(result["unique_users"])
                del result["unique_users"]
            
            return results
        except Exception as e:
            logger.error(f"Error getting content type stats: {e}")
            return []

    async def update_user_activity(self, user_id, activity_type, details=None):
        """Update user activity log"""
        try:
            activity_data = {
                "user_id": user_id,
                "activity_type": activity_type,
                "details": details or {},
                "timestamp": datetime.utcnow()
            }
            
            await self.analytics.insert_one(activity_data)
            return True
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
            return False

    async def get_user_activity_log(self, user_id, days=7, limit=50):
        """Get user activity log for specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            activities = await self.analytics.find({
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_date}
            }).sort("timestamp", -1).limit(limit).to_list(length=limit)
            
            return activities
        except Exception as e:
            logger.error(f"Error getting user activity log: {e}")
            return []

    async def get_activity_summary(self, days=7):
        """Get activity summary for all users"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": "$activity_type",
                    "count": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            results = await self.analytics.aggregate(pipeline).to_list(length=None)
            
            # Calculate unique user count for each activity type
            for result in results:
                result["unique_users_count"] = len(result["unique_users"])
                del result["unique_users"]
            
            return results
        except Exception as e:
            logger.error(f"Error getting activity summary: {e}")
            return []

    async def get_daily_stats(self, days=30):
        """Get daily statistics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "subject": "$subject"
                    },
                    "total_duration": {"$sum": "$duration"},
                    "total_sessions": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$sort": {"_id.date": -1}}
            ]
            
            results = await self.stats.aggregate(pipeline).to_list(length=None)
            
            # Calculate unique user count for each date-subject combination
            for result in results:
                result["unique_users_count"] = len(result["unique_users"])
                del result["unique_users"]
            
            return results
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return []

    async def get_weekly_stats(self, weeks=12):
        """Get weekly statistics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$timestamp"},
                        "week": {"$week": "$timestamp"}
                    },
                    "total_duration": {"$sum": "$duration"},
                    "total_sessions": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$sort": {"_id.year": -1, "_id.week": -1}}
            ]
            
            results = await self.stats.aggregate(pipeline).to_list(length=None)
            
            # Calculate unique user count for each week
            for result in results:
                result["unique_users_count"] = len(result["unique_users"])
                del result["unique_users"]
            
            return results
        except Exception as e:
            logger.error(f"Error getting weekly stats: {e}")
            return []

    async def get_monthly_stats(self, months=12):
        """Get monthly statistics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=months*30)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$timestamp"},
                        "month": {"$month": "$timestamp"}
                    },
                    "total_duration": {"$sum": "$duration"},
                    "total_sessions": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$sort": {"_id.year": -1, "_id.month": -1}}
            ]
            
            results = await self.stats.aggregate(pipeline).to_list(length=None)
            
            # Calculate unique user count for each month
            for result in results:
                result["unique_users_count"] = len(result["unique_users"])
                del result["unique_users"]
            
            return results
        except Exception as e:
            logger.error(f"Error getting monthly stats: {e}")
            return []

    async def cleanup_old_data(self, days_old=90):
        """Clean up old data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Clean old study stats
            old_stats = await self.stats.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            # Clean old user activity
            old_activity = await self.analytics.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            # Clean old messages
            old_messages = await self.col.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleaned up {old_stats.deleted_count} old stats, {old_activity.deleted_count} old activities, {old_messages.deleted_count} old messages")
            
            return {
                "stats_deleted": old_stats.deleted_count,
                "activity_deleted": old_activity.deleted_count,
                "messages_deleted": old_messages.deleted_count
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return {}

    async def get_database_info(self):
        """Get database information and statistics"""
        try:
            info = {}
            
            # Collection counts
            info["total_users"] = await self.col.count_documents({})
            info["total_study_stats"] = await self.stats.count_documents({})
            info["total_user_activity"] = await self.analytics.count_documents({})
            
            # Database size info
            db_stats = await self.db.command("dbstats")
            info["database_size_mb"] = db_stats.get("dataSize", 0) / (1024 * 1024)
            info["index_size_mb"] = db_stats.get("indexSize", 0) / (1024 * 1024)
            info["storage_size_mb"] = db_stats.get("storageSize", 0) / (1024 * 1024)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {}

    async def close(self):
        """Close database connection"""
        try:
            self.client.close()
            logger.info("TopDB connection closed")
        except Exception as e:
            logger.error(f"Error closing TopDB connection: {e}")

# Create global database instance with error handling
try:
    from config import *
    topdb = Database(DATABASE_URI, "StudyBotTopDB")
except Exception as e:
    print(f"Warning: Could not initialize database connection in topdb.py: {e}")
    topdb = None
