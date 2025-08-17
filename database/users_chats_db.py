import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields

# Try to import motor with error handling
try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError as e:
    print(f"Warning: Could not import motor in users_chats_db.py: {e}")
    AsyncIOMotorClient = None

from config import *

logger = logging.getLogger(__name__)

class Database:    
    def __init__(self, uri, database_name):
        if AsyncIOMotorClient is None:
            raise ImportError("Motor is not available")
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        
        # Remove the command method to prevent conflicts with filters.command
        if hasattr(self.db, 'command'):
            delattr(self.db, 'command')
            
        # Collections
        self.col = self.db.users
        self.grp = self.db.groups
        self.act = self.db.activities
        self.ban = self.db.bans
        self.conn = self.db.connections
        self.media = self.db.media
        self.file = self.db.file
        self.ia = self.db.ia
        self.ia2 = self.db.ia2
        self.ia3 = self.db.ia3
        self.ia4 = self.db.ia4
        self.ia5 = self.db.ia5
        self.ia6 = self.db.ia6
        self.ia7 = self.db.ia7
        self.ia8 = self.db.ia8
        self.ia9 = self.db.ia9
        self.ia10 = self.db.ia10
        self.ia11 = self.db.ia11
        self.ia12 = self.db.ia12
        self.ia13 = self.db.ia13
        self.ia14 = self.db.ia14
        self.ia15 = self.db.ia15
        self.ia16 = self.db.ia16
        self.ia17 = self.db.ia17
        self.ia18 = self.db.ia18
        self.ia19 = self.db.ia19
        self.ia20 = self.db.ia20
        self.ia21 = self.db.ia21
        self.ia22 = self.db.ia22
        self.ia23 = self.db.ia23
        self.ia24 = self.db.ia24
        self.ia25 = self.db.ia25
        self.ia26 = self.db.ia26
        self.ia27 = self.db.ia27
        self.ia28 = self.db.ia28
        self.ia29 = self.db.ia29
        self.ia30 = self.db.ia30
        self.ia31 = self.db.ia31
        self.ia32 = self.db.ia32
        self.ia33 = self.db.ia33
        self.ia34 = self.db.ia34
        self.ia35 = self.db.ia35
        self.ia36 = self.db.ia36
        self.ia37 = self.db.ia37
        self.ia38 = self.db.ia38
        self.ia39 = self.db.ia39
        self.ia40 = self.db.ia40
        self.ia41 = self.db.ia41
        self.ia42 = self.db.ia42
        self.ia43 = self.db.ia43
        self.ia44 = self.db.ia44
        self.ia45 = self.db.ia45
        self.ia46 = self.db.ia46
        self.ia47 = self.db.ia47
        self.ia48 = self.db.ia48
        self.ia49 = self.db.ia49
        self.ia50 = self.db.ia50
        self.ia51 = self.db.ia51
        self.ia52 = self.db.ia52
        self.ia53 = self.db.ia53
        self.ia54 = self.db.ia54
        self.ia55 = self.db.ia55
        self.ia56 = self.db.ia56
        self.ia57 = self.db.ia57
        self.ia58 = self.db.ia58
        self.ia59 = self.db.ia59
        self.ia60 = self.db.ia60
        self.ia61 = self.db.ia61
        self.ia62 = self.db.ia62
        self.ia63 = self.db.ia63
        self.ia64 = self.db.ia64
        self.ia65 = self.db.ia65
        self.ia66 = self.db.ia66
        self.ia67 = self.db.ia67
        self.ia68 = self.db.ia68
        self.ia69 = self.db.ia69
        self.ia70 = self.db.ia70
        self.ia71 = self.db.ia71
        self.ia72 = self.db.ia72
        self.ia73 = self.db.ia73
        self.ia74 = self.db.ia74
        self.ia75 = self.db.ia75
        self.ia76 = self.db.ia76
        self.ia77 = self.db.ia77
        self.ia78 = self.db.ia78
        self.ia79 = self.db.ia79
        self.ia80 = self.db.ia80
        self.ia81 = self.db.ia81
        self.ia82 = self.db.ia82
        self.ia83 = self.db.ia83
        self.ia84 = self.db.ia84
        self.ia85 = self.db.ia85
        self.ia86 = self.db.ia86
        self.ia87 = self.db.ia87
        self.ia88 = self.db.ia88
        self.ia89 = self.db.ia89
        self.ia90 = self.db.ia90
        self.ia91 = self.db.ia91
        self.ia92 = self.db.ia92
        self.ia93 = self.db.ia93
        self.ia94 = self.db.ia94
        self.ia95 = self.db.ia95
        self.ia96 = self.db.ia96
        self.ia97 = self.db.ia97
        self.ia98 = self.db.ia98
        self.ia99 = self.db.ia99
        self.ia100 = self.db.ia100
        self.users = self.db.uersz
        self.req = self.db.requests
        self.botcol = self.db.bot_settings
        self.misc = self.db.misc
        self.verify_id = self.db.verify_id 
        self.codes = self.db.codes
        self.filename_col = self.db.filename
        self.movie_updates = self.db.movie_updates
        self.connection = self.db.connections
        self.join_requests = self.db.join_requests

    async def add_name(self, filename):
        """Add filename to movie updates collection"""
        if await self.movie_updates.find_one({'_id': filename}):
            return False
        await self.movie_updates.insert_one({'_id': filename})
        return True

    async def delete_all_msg(self):
        """Delete all movie update notifications"""
        await self.movie_updates.delete_many({})
        logger.info("All filenames notification have been deleted.")
        return True
 
    async def add_join_req(self, user_id: int, channel_id: int):
        """Add join request for user and channel"""
        await self.req.update_one(
            {'user_id': user_id},
            {
                '$addToSet': {'channels': channel_id},
                '$setOnInsert': {'created_at': datetime.now(timezone.utc)}
            },
            upsert=True
        )
        
    async def has_joined_channel(self, user_id: int, channel_id: int):
        """Check if user has joined a specific channel"""
        doc = await self.req.find_one({'user_id': user_id})
        return doc and 'channels' in doc and channel_id in doc['channels']

    async def del_join_req(self):
        """Delete all join requests"""
        await self.req.drop()

    def new_user(self, id, name):
        """Create new user document structure"""
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title):
        """Create new group document structure"""
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )
    
    async def add_user(self, id, name):
        """Add new user to database"""
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        """Check if user exists in database"""
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        """Get total count of users"""
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        """Remove ban from user"""
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        """Ban user with reason"""
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        """Get ban status of user"""
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        """Get all users from database"""
        return self.col.find({})

    async def get_all_chats(self):
        """Get all groups from database"""
        return self.grp.find({})

    async def delete_user(self, user_id):
        """Delete user from database"""
        await self.col.delete_many({'id': int(user_id)})

    async def get_banned_users(self):
        """Get all banned users"""
        return self.col.find({'ban_status.is_banned': True})

    async def get_ban_info(self, user_id):
        """Get ban information for specific user"""
        user = await self.col.find_one({'id': int(user_id)})
        if user and user.get('ban_status', {}).get('is_banned'):
            return user['ban_status']
        return None

    async def total_chat_count(self):
        """Get total count of groups"""
        count = await self.grp.count_documents({})
        return count

    async def get_all_chat_members(self, chat_id):
        """Get all members of a specific chat"""
        group = await self.grp.find_one({'id': int(chat_id)})
        if group:
            return group.get('members', [])
        return []

    async def add_chat_member(self, chat_id, user_id, username=None):
        """Add member to chat"""
        await self.grp.update_one(
            {'id': int(chat_id)},
            {
                '$addToSet': {
                    'members': {
                        'user_id': user_id,
                        'username': username,
                        'joined_at': datetime.now(timezone.utc)
                    }
                }
            },
            upsert=True
        )

    async def remove_chat_member(self, chat_id, user_id):
        """Remove member from chat"""
        await self.grp.update_one(
            {'id': int(chat_id)},
            {'$pull': {'members': {'user_id': user_id}}}
        )

    async def set_grp_title(self, chat_id, title):
        """Set group title"""
        await self.grp.update_one(
            {'id': int(chat_id)},
            {'$set': {'title': title}},
            upsert=True
        )

    async def get_grp_title(self, chat_id):
        """Get group title"""
        group = await self.grp.find_one({'id': int(chat_id)})
        return group.get('title') if group else None

    async def disable_chat(self, chat_id, reason="No Reason"):
        """Disable chat"""
        chat_status = dict(
            is_disabled=True,
            reason=reason
        )
        await self.grp.update_one(
            {'id': int(chat_id)},
            {'$set': {'chat_status': chat_status}}
        )

    async def enable_chat(self, chat_id):
        """Enable chat"""
        chat_status = dict(
            is_disabled=False,
            reason=""
        )
        await self.grp.update_one(
            {'id': int(chat_id)},
            {'$set': {'chat_status': chat_status}}
        )

    async def get_chat_status(self, chat_id):
        """Get chat status"""
        default = dict(
            is_disabled=False,
            reason=''
        )
        group = await self.grp.find_one({'id': int(chat_id)})
        if not group:
            return default
        return group.get('chat_status', default)

    async def add_join_request(self, user_id, chat_id, user_name, chat_title):
        """Add join request to database"""
        join_request = {
            'user_id': user_id,
            'chat_id': chat_id,
            'user_name': user_name,
            'chat_title': chat_title,
            'status': 'pending',
            'timestamp': datetime.now(timezone.utc)
        }
        await self.join_requests.insert_one(join_request)

    async def update_join_request(self, user_id, chat_id, update_data):
        """Update join request status"""
        await self.join_requests.update_one(
            {'user_id': user_id, 'chat_id': chat_id},
            {'$set': update_data}
        )

    async def get_pending_join_requests(self):
        """Get all pending join requests"""
        return self.join_requests.find({'status': 'pending'}).sort('timestamp', -1)

    async def get_all_join_requests(self):
        """Get all join requests"""
        return self.join_requests.find({}).sort('timestamp', -1)

    async def get_join_request(self, user_id, chat_id):
        """Get specific join request"""
        return await self.join_requests.find_one({'user_id': user_id, 'chat_id': chat_id})

    async def delete_join_request(self, user_id, chat_id):
        """Delete join request"""
        await self.join_requests.delete_one({'user_id': user_id, 'chat_id': chat_id})

    async def get_user_stats(self, user_id):
        """Get user statistics"""
        user = await self.col.find_one({'id': int(user_id)})
        if user:
            return {
                'id': user['id'],
                'name': user['name'],
                'ban_status': user.get('ban_status', {}),
                'joined_at': user.get('joined_at'),
                'last_seen': user.get('last_seen'),
                'total_requests': user.get('total_requests', 0)
            }
        return None

    async def update_user_stats(self, user_id, update_data):
        """Update user statistics"""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': update_data}
        )

    async def get_chat_stats(self, chat_id):
        """Get chat statistics"""
        group = await self.grp.find_one({'id': int(chat_id)})
        if group:
            return {
                'id': group['id'],
                'title': group['title'],
                'chat_status': group.get('chat_status', {}),
                'members_count': len(group.get('members', [])),
                'created_at': group.get('created_at'),
                'last_activity': group.get('last_activity')
            }
        return None

    async def update_chat_stats(self, chat_id, update_data):
        """Update chat statistics"""
        await self.grp.update_one(
            {'id': int(chat_id)},
            {'$set': update_data}
        )

    async def get_connection(self, user_id):
        """Get user connection status"""
        return await self.connection.find_one({'id': user_id})

    async def add_connection(self, user_id, chat_id):
        """Add user connection"""
        await self.connection.update_one(
            {'id': user_id},
            {'$set': {'chat_id': chat_id}},
            upsert=True
        )

    async def remove_connection(self, user_id):
        """Remove user connection"""
        await self.connection.delete_one({'id': user_id})

    async def get_connections(self):
        """Get all connections"""
        return self.connection.find({})

    async def get_bot_settings(self):
        """Get bot settings"""
        return await self.botcol.find_one({})

    async def update_bot_settings(self, settings):
        """Update bot settings"""
        await self.botcol.update_one(
            {},
            {'$set': settings},
            upsert=True
        )

    async def get_misc_data(self, key):
        """Get miscellaneous data"""
        data = await self.misc.find_one({'key': key})
        return data.get('value') if data else None

    async def set_misc_data(self, key, value):
        """Set miscellaneous data"""
        await self.misc.update_one(
            {'key': key},
            {'$set': {'value': value}},
            upsert=True
        )

    async def delete_misc_data(self, key):
        """Delete miscellaneous data"""
        await self.misc.delete_one({'key': key})

    async def get_verify_id(self, user_id):
        """Get verification ID for user"""
        return await self.verify_id.find_one({'user_id': user_id})

    async def set_verify_id(self, user_id, verify_id):
        """Set verification ID for user"""
        await self.verify_id.update_one(
            {'user_id': user_id},
            {'$set': {'verify_id': verify_id}},
            upsert=True
        )

    async def delete_verify_id(self, user_id):
        """Delete verification ID for user"""
        await self.verify_id.delete_one({'user_id': user_id})

    async def get_codes(self):
        """Get all codes"""
        return self.codes.find({})

    async def add_code(self, code_data):
        """Add new code"""
        await self.codes.insert_one(code_data)

    async def get_code(self, code):
        """Get specific code"""
        return await self.codes.find_one({'code': code})

    async def delete_code(self, code):
        """Delete code"""
        await self.codes.delete_one({'code': code})

    async def get_filename(self, file_id):
        """Get filename by file ID"""
        return await self.filename_col.find_one({'file_id': file_id})

    async def add_filename(self, file_id, filename):
        """Add filename mapping"""
        await self.filename_col.update_one(
            {'file_id': file_id},
            {'$set': {'filename': filename}},
            upsert=True
        )

    async def delete_filename(self, file_id):
        """Delete filename mapping"""
        await self.filename_col.delete_one({'file_id': file_id})

    async def get_all_filenames(self):
        """Get all filename mappings"""
        return self.filename_col.find({})

    async def search_users(self, query):
        """Search users by name"""
        return self.col.find({'name': {'$regex': query, '$options': 'i'}})

    async def search_groups(self, query):
        """Search groups by title"""
        return self.grp.find({'title': {'$regex': query, '$options': 'i'}})

    async def get_recent_users(self, limit=10):
        """Get recent users"""
        return self.col.find({}).sort('joined_at', -1).limit(limit)

    async def get_recent_groups(self, limit=10):
        """Get recent groups"""
        return self.grp.find({}).sort('created_at', -1).limit(limit)

    async def get_user_activity(self, user_id, days=7):
        """Get user activity for specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        user = await self.col.find_one({'id': int(user_id)})
        if user and 'activity' in user:
            return [act for act in user['activity'] if act.get('timestamp', datetime.min) > cutoff_date]
        return []

    async def add_user_activity(self, user_id, activity_type, details=None):
        """Add user activity"""
        activity = {
            'type': activity_type,
            'timestamp': datetime.now(timezone.utc),
            'details': details or {}
        }
        await self.col.update_one(
            {'id': int(user_id)},
            {'$push': {'activity': activity}}
        )

    async def get_chat_activity(self, chat_id, days=7):
        """Get chat activity for specified days"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        group = await self.grp.find_one({'id': int(chat_id)})
        if group and 'activity' in group:
            return [act for act in group['activity'] if act.get('timestamp', datetime.min) > cutoff_date]
        return []

    async def add_chat_activity(self, chat_id, activity_type, details=None):
        """Add chat activity"""
        activity = {
            'type': activity_type,
            'timestamp': datetime.now(timezone.utc),
            'details': details or {}
        }
        await self.grp.update_one(
            {'id': int(chat_id)},
            {'$push': {'activity': activity}}
        )

    async def get_database_stats(self):
        """Get comprehensive database statistics"""
        try:
            stats = {}
            
            # User stats
            stats['total_users'] = await self.total_users_count()
            stats['banned_users'] = await self.col.count_documents({'ban_status.is_banned': True})
            
            # Group stats
            stats['total_groups'] = await self.total_chat_count()
            stats['disabled_groups'] = await self.grp.count_documents({'chat_status.is_disabled': True})
            
            # Join request stats
            stats['pending_requests'] = await self.join_requests.count_documents({'status': 'pending'})
            stats['total_requests'] = await self.join_requests.count_documents({})
            
            # Connection stats
            stats['active_connections'] = await self.connection.count_documents({})
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    async def cleanup_old_data(self, days_old=30):
        """Clean up old data from database"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            # Clean old join requests
            old_requests = await self.join_requests.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            # Clean old activity logs
            old_user_activity = await self.col.update_many(
                {},
                {'$pull': {'activity': {'timestamp': {'$lt': cutoff_date}}}}
            )
            
            old_group_activity = await self.grp.update_many(
                {},
                {'$pull': {'activity': {'timestamp': {'$lt': cutoff_date}}}}
            )
            
            logger.info(f"Cleaned up {old_requests.deleted_count} old join requests")
            return old_requests.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0

    async def backup_database(self):
        """Create database backup (basic implementation)"""
        try:
            # This is a basic backup implementation
            # In production, you might want to use MongoDB's built-in backup tools
            backup_data = {
                'timestamp': datetime.now(timezone.utc),
                'users_count': await self.total_users_count(),
                'groups_count': await self.total_chat_count(),
                'backup_type': 'manual'
            }
            
            # Store backup info in misc collection
            await self.set_misc_data('last_backup', backup_data)
            
            logger.info("Database backup info recorded")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False

    async def close(self):
        """Close database connection"""
        try:
            self._client.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

# Create global database instance with error handling
try:
    from config import *
    db = Database(DATABASE_URI, DATABASE_NAME)
except Exception as e:
    print(f"Warning: Could not initialize database connection in users_chats_db.py: {e}")
    db = None
