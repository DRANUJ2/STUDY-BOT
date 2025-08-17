import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

# Try to import motor with error handling
try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError as e:
    print(f"Warning: Could not import motor in config_db.py: {e}")
    AsyncIOMotorClient = None

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, uri, database_name):
        if AsyncIOMotorClient is None:
            raise ImportError("Motor is not available")
        self.client = AsyncIOMotorClient(uri)
        raw_db = self.client[database_name]
        
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
        
        self.db = DatabaseWrapper(raw_db)
            
        # Collections
        self.col = self.db.config
        self.misc = self.db.misc
        self.settings = self.db.settings
        self.backups = self.db.backups
        self.logs = self.db.logs

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

    async def get_config(self, key: str, default: Any = None):
        """Get configuration value by key"""
        try:
            config = await self.col.find_one({"key": key})
            return config.get("value") if config else default
        except Exception as e:
            logger.error(f"Error getting config {key}: {e}")
            return default

    async def set_config(self, key: str, value: Any):
        """Set configuration value by key"""
        try:
            await self.col.update_one(
                {"key": key},
                {"$set": {"value": value, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            return False

    async def delete_config(self, key: str):
        """Delete configuration by key"""
        try:
            await self.col.delete_one({"key": key})
            return True
        except Exception as e:
            logger.error(f"Error deleting config {key}: {e}")
            return False

    async def get_all_configs(self):
        """Get all configuration values"""
        try:
            configs = await self.col.find({}).to_list(length=None)
            return {config["key"]: config["value"] for config in configs}
        except Exception as e:
            logger.error(f"Error getting all configs: {e}")
            return {}

    async def get_setting(self, key: str, default: Any = None):
        """Get setting value by key"""
        try:
            setting = await self.settings.find_one({"key": key})
            return setting.get("value") if setting else default
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default

    async def set_setting(self, key: str, value: Any):
        """Set setting value by key"""
        try:
            await self.settings.update_one(
                {"key": key},
                {"$set": {"value": value, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting setting {key}: {e}")
            return False

    async def delete_setting(self, key: str):
        """Delete setting by key"""
        try:
            await self.settings.delete_one({"key": key})
            return True
        except Exception as e:
            logger.error(f"Error deleting setting {key}: {e}")
            return False

    async def get_all_settings(self):
        """Get all setting values"""
        try:
            settings = await self.settings.find({}).to_list(length=None)
            return {setting["key"]: setting["value"] for setting in settings}
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return {}

    async def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        try:
            feature = await self.misc.find_one({"name": feature_name})
            if feature:
                return feature.get("enabled", False)
            return False
        except Exception as e:
            logger.error(f"Error checking feature {feature_name}: {e}")
            return False

    async def enable_feature(self, feature_name: str, description: str = ""):
        """Enable a feature"""
        try:
            await self.misc.update_one(
                {"name": feature_name},
                {
                    "$set": {
                        "enabled": True,
                        "description": description,
                        "enabled_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error enabling feature {feature_name}: {e}")
            return False

    async def disable_feature(self, feature_name: str, reason: str = ""):
        """Disable a feature"""
        try:
            await self.misc.update_one(
                {"name": feature_name},
                {
                    "$set": {
                        "enabled": False,
                        "disabled_reason": reason,
                        "disabled_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error disabling feature {feature_name}: {e}")
            return False

    async def get_feature_info(self, feature_name: str):
        """Get feature information"""
        try:
            feature = await self.misc.find_one({"name": feature_name})
            return feature
        except Exception as e:
            logger.error(f"Error getting feature info {feature_name}: {e}")
            return None

    async def get_all_features(self):
        """Get all features"""
        try:
            features = await self.misc.find({}).to_list(length=None)
            return features
        except Exception as e:
            logger.error(f"Error getting all features: {e}")
            return []

    async def add_feature(self, feature_name: str, description: str = "", enabled: bool = True):
        """Add a new feature"""
        try:
            feature_data = {
                "name": feature_name,
                "description": description,
                "enabled": enabled,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if enabled:
                feature_data["enabled_at"] = datetime.utcnow()
            else:
                feature_data["disabled_at"] = datetime.utcnow()
            
            await self.misc.insert_one(feature_data)
            return True
        except Exception as e:
            logger.error(f"Error adding feature {feature_name}: {e}")
            return False

    async def delete_feature(self, feature_name: str):
        """Delete a feature"""
        try:
            await self.misc.delete_one({"name": feature_name})
            return True
        except Exception as e:
            logger.error(f"Error deleting feature {feature_name}: {e}")
            return False

    async def get_bot_config(self):
        """Get bot configuration"""
        try:
            config = await self.col.find_one({"key": "bot_config"})
            return config.get("value") if config else {}
        except Exception as e:
            logger.error(f"Error getting bot config: {e}")
            return {}

    async def set_bot_config(self, config_data: Dict):
        """Set bot configuration"""
        try:
            await self.col.update_one(
                {"key": "bot_config"},
                {"$set": {"value": config_data, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting bot config: {e}")
            return False

    async def get_user_config(self, user_id: int):
        """Get user configuration"""
        try:
            config = await self.col.find_one({"key": f"user_config_{user_id}"})
            return config.get("value") if config else {}
        except Exception as e:
            logger.error(f"Error getting user config {user_id}: {e}")
            return {}

    async def set_user_config(self, user_id: int, config_data: Dict):
        """Set user configuration"""
        try:
            await self.col.update_one(
                {"key": f"user_config_{user_id}"},
                {"$set": {"value": config_data, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting user config {user_id}: {e}")
            return False

    async def get_chat_config(self, chat_id: int):
        """Get chat configuration"""
        try:
            config = await self.col.find_one({"key": f"chat_config_{chat_id}"})
            return config.get("value") if config else {}
        except Exception as e:
            logger.error(f"Error getting chat config {chat_id}: {e}")
            return {}

    async def set_chat_config(self, chat_id: int, config_data: Dict):
        """Set chat configuration"""
        try:
            await self.col.update_one(
                {"key": f"chat_config_{chat_id}"},
                {"$set": {"value": config_data, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting chat config {chat_id}: {e}")
            return False

    async def get_global_config(self):
        """Get global configuration"""
        try:
            config = await self.col.find_one({"key": "global_config"})
            return config.get("value") if config else {}
        except Exception as e:
            logger.error(f"Error getting global config: {e}")
            return {}

    async def set_global_config(self, config_data: Dict):
        """Set global configuration"""
        try:
            await self.col.update_one(
                {"key": "global_config"},
                {"$set": {"value": config_data, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting global config: {e}")
            return False

    async def backup_configs(self):
        """Backup all configurations"""
        try:
            backup_data = {
                "timestamp": datetime.utcnow(),
                "configs": await self.get_all_configs(),
                "settings": await self.get_all_settings(),
                "features": await self.get_all_features()
            }
            
            # Store backup in config collection
            await self.col.update_one(
                {"key": "config_backup"},
                {"$set": {"value": backup_data}},
                upsert=True
            )
            
            logger.info("Configuration backup created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating config backup: {e}")
            return False

    async def restore_configs(self, backup_key: str = "config_backup"):
        """Restore configurations from backup"""
        try:
            backup = await self.col.find_one({"key": backup_key})
            if not backup:
                logger.error("Backup not found")
                return False
            
            backup_data = backup.get("value", {})
            
            # Restore configs
            for key, value in backup_data.get("configs", {}).items():
                await self.set_config(key, value)
            
            # Restore settings
            for key, value in backup_data.get("settings", {}).items():
                await self.set_setting(key, value)
            
            # Restore features
            for feature in backup_data.get("features", []):
                await self.misc.update_one(
                    {"name": feature["name"]},
                    {"$set": feature},
                    upsert=True
                )
            
            logger.info("Configuration restore completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error restoring configs: {e}")
            return False

    async def get_config_stats(self):
        """Get configuration statistics"""
        try:
            stats = {}
            
            # Count configs
            stats["total_configs"] = await self.col.count_documents({})
            stats["total_settings"] = await self.settings.count_documents({})
            stats["total_features"] = await self.misc.count_documents({})
            
            # Count enabled features
            stats["enabled_features"] = await self.misc.count_documents({"enabled": True})
            stats["disabled_features"] = await self.misc.count_documents({"enabled": False})
            
            # Get recent updates
            recent_configs = await self.col.find({}).sort("updated_at", -1).limit(5).to_list(length=5)
            stats["recent_configs"] = recent_configs
            
            return stats
        except Exception as e:
            logger.error(f"Error getting config stats: {e}")
            return {}

    async def cleanup_old_configs(self, days_old=90):
        """Clean up old configuration data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Clean old backups
            old_backups = await self.col.delete_many({
                "key": {"$regex": "^config_backup_"},
                "value.timestamp": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleaned up {old_backups.deleted_count} old config backups")
            return old_backups.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old configs: {e}")
            return 0

    async def close(self):
        """Close database connection"""
        try:
            self.client.close()
            logger.info("ConfigDB connection closed")
        except Exception as e:
            logger.error(f"Error closing ConfigDB connection: {e}")

# Create global database instance with error handling
try:
    from config import *
    mdb = Database(DATABASE_URI, "StudyBotConfigDB")
except Exception as e:
    print(f"Warning: Could not initialize database connection in config_db.py: {e}")
    mdb = None
