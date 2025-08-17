import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.study_db import db as study_db, StudyFiles, Batches, Chapters, Users, StudySessions, ContentAnalytics, BotSettings, JoinRequests, Chats, GroupSettings
from config import *
from studybot.Bot import studybot, content_bot
import re

logger = logging.getLogger(__name__)

# Admin commands - only for bot owner and admins
@studybot.on_message(filters.command("admin") & filters.private)
async def admin_panel(client: Client, message: Message):
    """Admin panel for bot management"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        admin_text = """🔐 **Admin Panel** 🔐

Welcome to the Study Bot Admin Panel!

**Available Commands:**
• /addbatch - Add new study batch
• /delbatch - Delete study batch
• /addcontent - Add study content
• /delcontent - Delete study content
• /users - View user statistics
• /stats - Bot statistics
• /broadcast - Send message to all users
• /settings - Bot settings
• /backup - Backup database
• /restore - Restore database

**Quick Actions:**"""
        
        keyboard = [
            [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
            [InlineKeyboardButton("📚 Batch Management", callback_data="admin_batches")],
            [InlineKeyboardButton("📁 Content Management", callback_data="admin_content")],
            [InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings")],
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(admin_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in admin panel: {e}")
        await message.reply_text("❌ An error occurred in admin panel.")

# Add batch command
@studybot.on_message(filters.command("addbatch") & filters.private)
async def add_batch_command(client: Client, message: Message):
    """Add new study batch"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("❌ Usage: /addbatch <batch_name>\n\nExample: /addbatch NEET2026")
            return
        
        batch_name = command_parts[1].strip()
        
        # Check if batch already exists
        existing_batch = await Batches.find_one({"batch_name": batch_name})
        if existing_batch:
            await message.reply_text(f"❌ Batch '{batch_name}' already exists!")
            return
        
        # Create new batch
        batch_doc = Batches(
            batch_name=batch_name,
            subjects=["Physics", "Chemistry", "Biology"],
            teachers=["Mr Sir", "Saleem Sir"],
            is_active=True,
            created_at=datetime.utcnow(),
            created_by=user_id
        )
        
        await batch_doc.commit()
        
        await message.reply_text(
            f"✅ **Batch Added Successfully!**\n\n"
            f"📚 **Batch Name:** {batch_name}\n"
            f"🧪 **Subjects:** Physics, Chemistry, Biology\n"
            f"👨‍🏫 **Teachers:** Mr Sir, Saleem Sir\n"
            f"📅 **Created:** {batch_doc.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"👤 **Created By:** {user_id}"
        )
        
        logger.info(f"Admin {user_id} added new batch: {batch_name}")
        
    except Exception as e:
        logger.error(f"Error adding batch: {e}")
        await message.reply_text("❌ An error occurred while adding batch.")

# Delete batch command
@studybot.on_message(filters.command("delbatch") & filters.private)
async def delete_batch_command(client: Client, message: Message):
    """Delete study batch"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("❌ Usage: /delbatch <batch_name>\n\nExample: /delbatch NEET2026")
            return
        
        batch_name = command_parts[1].strip()
        
        # Check if batch exists
        existing_batch = await Batches.find_one({"batch_name": batch_name})
        if not existing_batch:
            await message.reply_text(f"❌ Batch '{batch_name}' not found!")
            return
        
        # Delete batch
        await Batches.delete_one({"batch_name": batch_name})
        
        # Also delete related content
        await StudyFiles.delete_many({"batch_name": batch_name})
        
        await message.reply_text(
            f"✅ **Batch Deleted Successfully!**\n\n"
            f"📚 **Batch Name:** {batch_name}\n"
            f"🗑️ **Status:** Deleted\n"
            f"📁 **Related Content:** Also deleted\n"
            f"👤 **Deleted By:** {user_id}"
        )
        
        logger.info(f"Admin {user_id} deleted batch: {batch_name}")
        
    except Exception as e:
        logger.error(f"Error deleting batch: {e}")
        await message.reply_text("❌ An error occurred while deleting batch.")

# Add content command
@studybot.on_message(filters.command("addcontent") & filters.private)
async def add_content_command(client: Client, message: Message):
    """Add study content"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=5)
        if len(command_parts) < 6:
            await message.reply_text(
                "❌ Usage: /addcontent <batch_name> <subject> <teacher> <chapter> <content_type>\n\n"
                "Example: /addcontent NEET2026 Physics Mr_Sir CH01 Lectures"
            )
            return
        
        batch_name = command_parts[1].strip()
        subject = command_parts[2].strip()
        teacher = command_parts[3].strip()
        chapter = command_parts[4].strip()
        content_type = command_parts[5].strip()
        
        # Check if batch exists
        existing_batch = await Batches.find_one({"batch_name": batch_name})
        if not existing_batch:
            await message.reply_text(f"❌ Batch '{batch_name}' not found! Use /addbatch first.")
            return
        
        # Create content entry
        content_doc = StudyFiles(
            batch_name=batch_name,
            subject=subject,
            teacher=teacher,
            chapter_no=chapter,
            content_type=content_type,
            file_name=f"{batch_name}_{subject}_{teacher}_{chapter}_{content_type}",
            file_size=0,  # Will be updated when file is uploaded
            uploaded_at=datetime.utcnow(),
            uploaded_by=user_id,
            is_active=True
        )
        
        await content_doc.commit()
        
        await message.reply_text(
            f"✅ **Content Added Successfully!**\n\n"
            f"📚 **Batch:** {batch_name}\n"
            f"🧪 **Subject:** {subject}\n"
            f"👨‍🏫 **Teacher:** {teacher}\n"
            f"📖 **Chapter:** {chapter}\n"
            f"📝 **Content Type:** {content_type}\n"
            f"📅 **Added:** {content_doc.uploaded_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"👤 **Added By:** {user_id}\n\n"
            f"💡 **Next Step:** Upload the actual file using the Content Bot."
        )
        
        logger.info(f"Admin {user_id} added content: {batch_name} - {subject} - {teacher} - {chapter} - {content_type}")
        
    except Exception as e:
        logger.error(f"Error adding content: {e}")
        await message.reply_text("❌ An error occurred while adding content.")

# Delete content command
@studybot.on_message(filters.command("delcontent") & filters.private)
async def delete_content_command(client: Client, message: Message):
    """Delete study content"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=5)
        if len(command_parts) < 6:
            await message.reply_text(
                "❌ Usage: /delcontent <batch_name> <subject> <teacher> <chapter> <content_type>\n\n"
                "Example: /delcontent NEET2026 Physics Mr_Sir CH01 Lectures"
            )
            return
        
        batch_name = command_parts[1].strip()
        subject = command_parts[2].strip()
        teacher = command_parts[3].strip()
        chapter = command_parts[4].strip()
        content_type = command_parts[5].strip()
        
        # Delete content
        result = await StudyFiles.delete_one({
            "batch_name": batch_name,
            "subject": subject,
            "teacher": teacher,
            "chapter_no": chapter,
            "content_type": content_type
        })
        
        if result.deleted_count > 0:
            await message.reply_text(
                f"✅ **Content Deleted Successfully!**\n\n"
                f"📚 **Batch:** {batch_name}\n"
                f"🧪 **Subject:** {subject}\n"
                f"👨‍🏫 **Teacher:** {teacher}\n"
                f"📖 **Chapter:** {chapter}\n"
                f"📝 **Content Type:** {content_type}\n"
                f"👤 **Deleted By:** {user_id}"
            )
            
            logger.info(f"Admin {user_id} deleted content: {batch_name} - {subject} - {teacher} - {chapter} - {content_type}")
        else:
            await message.reply_text(f"❌ Content not found!")
        
    except Exception as e:
        logger.error(f"Error deleting content: {e}")
        await message.reply_text("❌ An error occurred while deleting content.")

# Users command
@studybot.on_message(filters.command("users") & filters.private)
async def users_command(client: Client, message: Message):
    """View user statistics"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Get user statistics
        total_users = await Users.count_documents({})
        active_users = await Users.count_documents({"last_active": {"$gte": datetime.utcnow() - timedelta(days=7)}})
        premium_users = await Users.count_documents({"is_premium": True})
        
        # Get recent users
        recent_users = await Users.find().sort("joined_at", -1).limit(5).to_list(length=5)
        
        users_text = f"""👥 **User Statistics** 👥

📊 **Total Users:** {total_users}
🟢 **Active (7 days):** {active_users}
⭐ **Premium Users:** {premium_users}

👤 **Recent Users:**"""
        
        for user in recent_users:
            users_text += f"\n• {user.first_name} (@{user.username or 'No username'}) - {user.joined_at.strftime('%Y-%m-%d')}"
        
        await message.reply_text(users_text)
        
    except Exception as e:
        logger.error(f"Error in users command: {e}")
        await message.reply_text("❌ An error occurred while fetching user statistics.")

# Stats command
@studybot.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    """View bot statistics"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Get various statistics
        total_users = await Users.count_documents({})
        total_batches = await Batches.count_documents({})
        total_content = await StudyFiles.count_documents({})
        total_downloads = sum([user.total_downloads for user in await Users.find().to_list(length=1000)])
        
        # Get content by type
        content_by_type = await StudyFiles.aggregate([
            {"$group": {"_id": "$content_type", "count": {"$sum": 1}}}
        ]).to_list(length=100)
        
        stats_text = f"""📊 **Bot Statistics** 📊

👥 **Users:** {total_users}
📚 **Batches:** {total_batches}
📁 **Content Files:** {total_content}
📥 **Total Downloads:** {total_downloads}

📝 **Content by Type:**"""
        
        for content_type in content_by_type:
            stats_text += f"\n• {content_type['_id']}: {content_type['count']}"
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply_text("❌ An error occurred while fetching bot statistics.")

# Broadcast command
@studybot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    """Send message to all users"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("❌ Usage: /broadcast <message>\n\nExample: /broadcast Hello everyone!")
            return
        
        broadcast_message = command_parts[1].strip()
        
        # Get all users
        users = await Users.find().to_list(length=1000)
        
        if not users:
            await message.reply_text("❌ No users found to broadcast to.")
            return
        
        # Send broadcast
        success_count = 0
        failed_count = 0
        
        for user in users:
            try:
                await client.send_message(
                    user.user_id,
                    f"📢 **Broadcast Message** 📢\n\n{broadcast_message}\n\n_From Study Bot Admin_"
                )
                success_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to {user.user_id}: {e}")
        
        await message.reply_text(
            f"✅ **Broadcast Completed!**\n\n"
            f"📢 **Message:** {broadcast_message}\n"
            f"✅ **Success:** {success_count} users\n"
            f"❌ **Failed:** {failed_count} users\n"
            f"👤 **Sent By:** {user_id}"
        )
        
        logger.info(f"Admin {user_id} sent broadcast to {success_count} users")
        
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await message.reply_text("❌ An error occurred while broadcasting.")

# Settings command
@studybot.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    """View and modify bot settings"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Get current settings
        settings = await BotSettings.find_one({"_id": "main"})
        if not settings:
            # Create default settings
            settings = BotSettings(
                _id="main",
                enable_pm=ENABLE_PM,
                enable_group=ENABLE_GROUP,
                max_file_size=MAX_FILE_SIZE,
                surprise_link="https://t.me/your_channel",
                maintenance_mode=False,
                created_at=datetime.utcnow()
            )
            await settings.commit()
        
        settings_text = f"""⚙️ **Bot Settings** ⚙️

🔐 **Private Messages:** {'✅ Enabled' if settings.enable_pm else '❌ Disabled'}
👥 **Group Messages:** {'✅ Enabled' if settings.enable_group else '❌ Disabled'}
📁 **Max File Size:** {get_file_size(settings.max_file_size)}
🎁 **Surprise Link:** {settings.surprise_link}
🔧 **Maintenance Mode:** {'✅ Enabled' if settings.maintenance_mode else '❌ Disabled'}

💡 **Use /setsetting to modify these settings**"""
        
        keyboard = [
            [InlineKeyboardButton("🔐 Toggle PM", callback_data="setting_toggle_pm")],
            [InlineKeyboardButton("👥 Toggle Group", callback_data="setting_toggle_group")],
            [InlineKeyboardButton("🎁 Update Surprise Link", callback_data="setting_surprise_link")],
            [InlineKeyboardButton("🔧 Toggle Maintenance", callback_data="setting_toggle_maintenance")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(settings_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in settings command: {e}")
        await message.reply_text("❌ An error occurred while fetching settings.")

# Set setting command
@studybot.on_message(filters.command("setsetting") & filters.private)
async def set_setting_command(client: Client, message: Message):
    """Set bot setting"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            await message.reply_text(
                "❌ Usage: /setsetting <setting> <value>\n\n"
                "Examples:\n"
                "• /setsetting enable_pm true\n"
                "• /setsetting surprise_link https://t.me/new_channel\n"
                "• /setsetting max_file_size 52428800"
            )
            return
        
        setting_name = command_parts[1].strip()
        setting_value = command_parts[2].strip()
        
        # Get current settings
        settings = await BotSettings.find_one({"_id": "main"})
        if not settings:
            await message.reply_text("❌ Bot settings not found. Use /settings first.")
            return
        
        # Update setting
        if setting_name == "enable_pm":
            settings.enable_pm = setting_value.lower() in ["true", "1", "yes", "on"]
            await settings.commit()
            await message.reply_text(f"✅ PM setting updated to: {'Enabled' if settings.enable_pm else 'Disabled'}")
            
        elif setting_name == "enable_group":
            settings.enable_group = setting_value.lower() in ["true", "1", "yes", "on"]
            await settings.commit()
            await message.reply_text(f"✅ Group setting updated to: {'Enabled' if settings.enable_group else 'Disabled'}")
            
        elif setting_name == "surprise_link":
            settings.surprise_link = setting_value
            await settings.commit()
            await message.reply_text(f"✅ Surprise link updated to: {settings.surprise_link}")
            
        elif setting_name == "max_file_size":
            try:
                file_size = int(setting_value)
                settings.max_file_size = file_size
                await settings.commit()
                await message.reply_text(f"✅ Max file size updated to: {get_file_size(file_size)}")
            except ValueError:
                await message.reply_text("❌ Invalid file size. Please provide a number in bytes.")
                
        elif setting_name == "maintenance_mode":
            settings.maintenance_mode = setting_value.lower() in ["true", "1", "yes", "on"]
            await settings.commit()
            await message.reply_text(f"✅ Maintenance mode updated to: {'Enabled' if settings.maintenance_mode else 'Disabled'}")
            
        else:
            await message.reply_text(f"❌ Unknown setting: {setting_name}")
            return
        
        logger.info(f"Admin {user_id} updated setting {setting_name} to {setting_value}")
        
    except Exception as e:
        logger.error(f"Error setting setting: {e}")
        await message.reply_text("❌ An error occurred while updating setting.")

# Utility functions
async def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    try:
        user = await Users.find_one({"_id": user_id})
        return user and user.is_admin
    except:
        return False

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

# Log when plugin loads
logger.info("Admin plugin loaded successfully")
