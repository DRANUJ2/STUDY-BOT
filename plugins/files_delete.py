import re
import logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS
from database.ia_filterdb import Media, Media2, unpack_new_file_id

logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    """Delete Multiple files from database"""

    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)
    
    # Try to delete from primary database first
    if await Media.count_documents({'file_id': file_id}):
        result = await Media.collection.delete_one({
            '_id': file_id,
        })
        if result.deleted_count:
            logger.info('File is successfully deleted from primary database.')
            return
    else:
        # Try secondary database
        result = await Media2.collection.delete_one({
            '_id': file_id,
        })
        if result.deleted_count:
            logger.info('File is successfully deleted from secondary database.')
            return
    
    # If file_id deletion failed, try deleting by file properties
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    
    # Try primary database with file properties
    result = await Media.collection.delete_many({
        'file_name': file_name,
        'file_size': media.file_size,
        'mime_type': media.mime_type
    })
    if result.deleted_count:
        logger.info(f'File deleted from primary database by properties. Deleted: {result.deleted_count}')
        return
    
    # Try secondary database with file properties
    result = await Media2.collection.delete_many({
        'file_name': file_name,
        'file_size': media.file_size,
        'mime_type': media.mime_type
    })
    if result.deleted_count:
        logger.info(f'File deleted from secondary database by properties. Deleted: {result.deleted_count}')
        return
    
    # Try with original filename
    result = await Media.collection.delete_many({
        'file_name': media.file_name,
        'file_size': media.file_size,
        'mime_type': media.mime_type
    })
    if result.deleted_count:
        logger.info(f'File deleted from primary database by original filename. Deleted: {result.deleted_count}')
        return
    
    result = await Media2.collection.delete_many({
        'file_name': media.file_name,
        'file_size': media.file_size,
        'mime_type': media.mime_type
    })
    if result.deleted_count:
        logger.info(f'File deleted from secondary database by original filename. Deleted: {result.deleted_count}')
        return
    
    logger.info('File not found in database.')


@Client.on_message(filters.command("deletefile") & filters.user(ADMINS))
async def delete_file_command(bot, message):
    """Delete file by file_id (admin only)"""
    if len(message.command) < 2:
        await message.reply_text("❌ **Usage:** `/deletefile <file_id>`")
        return
    
    try:
        file_id = message.command[1]
        
        # Try to delete from primary database
        result = await Media.collection.delete_one({'_id': file_id})
        if result.deleted_count:
            await message.reply_text(f"✅ File `{file_id}` deleted from primary database.")
            return
        
        # Try secondary database
        result = await Media2.collection.delete_one({'_id': file_id})
        if result.deleted_count:
            await message.reply_text(f"✅ File `{file_id}` deleted from secondary database.")
            return
        
        await message.reply_text(f"❌ File `{file_id}` not found in database.")
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        await message.reply_text(f"❌ Error deleting file: {e}")


@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def delete_files_by_name(bot, message):
    """Delete files by filename pattern (admin only)"""
    if len(message.command) < 2:
        await message.reply_text("❌ **Usage:** `/deletefiles <filename_pattern>`")
        return
    
    try:
        filename_pattern = " ".join(message.command[1:])
        
        # Create regex pattern for partial matching
        regex_pattern = re.compile(filename_pattern, re.IGNORECASE)
        
        # Delete from primary database
        result = await Media.collection.delete_many({
            'file_name': {'$regex': regex_pattern}
        })
        primary_deleted = result.deleted_count
        
        # Delete from secondary database
        result = await Media2.collection.delete_many({
            'file_name': {'$regex': regex_pattern}
        })
        secondary_deleted = result.deleted_count
        
        total_deleted = primary_deleted + secondary_deleted
        
        if total_deleted > 0:
            await message.reply_text(
                f"✅ **Files Deleted Successfully!**\n\n"
                f"📁 **Primary DB:** {primary_deleted} files\n"
                f"📁 **Secondary DB:** {secondary_deleted} files\n"
                f"📊 **Total Deleted:** {total_deleted} files\n"
                f"🔍 **Pattern:** `{filename_pattern}`"
            )
        else:
            await message.reply_text(f"❌ No files found matching pattern `{filename_pattern}`")
        
    except Exception as e:
        logger.error(f"Error deleting files by name: {e}")
        await message.reply_text(f"❌ Error deleting files: {e}")


@Client.on_message(filters.command("cleardb") & filters.user(ADMINS))
async def clear_database(bot, message):
    """Clear entire database (admin only)"""
    try:
        # Get confirmation
        confirm_text = (
            "⚠️ **WARNING: This will delete ALL files from the database!**\n\n"
            "This action cannot be undone. Are you sure you want to continue?\n\n"
            "Reply with `YES` to confirm, or any other message to cancel."
        )
        
        confirm_msg = await message.reply_text(confirm_text)
        
        # Wait for confirmation
        try:
            response = await bot.wait_for_message(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                timeout=60
            )
            
            if response.text.upper() == "YES":
                # Clear primary database
                primary_result = await Media.collection.delete_many({})
                primary_deleted = primary_result.deleted_count
                
                # Clear secondary database
                secondary_result = await Media2.collection.delete_many({})
                secondary_deleted = secondary_result.deleted_count
                
                total_deleted = primary_deleted + secondary_deleted
                
                await message.reply_text(
                    f"🗑️ **Database Cleared Successfully!**\n\n"
                    f"📁 **Primary DB:** {primary_deleted} files deleted\n"
                    f"📁 **Secondary DB:** {secondary_deleted} files deleted\n"
                    f"📊 **Total Deleted:** {total_deleted} files"
                )
                
                logger.info(f"Database cleared by admin {message.from_user.id}. Deleted {total_deleted} files.")
                
            else:
                await message.reply_text("❌ Database clearing cancelled.")
                
        except TimeoutError:
            await message.reply_text("⏰ Confirmation timeout. Database clearing cancelled.")
            
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        await message.reply_text(f"❌ Error clearing database: {e}")


@Client.on_message(filters.command("dbstats") & filters.user(ADMINS))
async def database_stats(bot, message):
    """Show database statistics (admin only)"""
    try:
        # Get primary database stats
        primary_count = await Media.collection.count_documents({})
        
        # Get secondary database stats
        secondary_count = await Media2.collection.count_documents({})
        
        total_files = primary_count + secondary_count
        
        stats_text = f"📊 **Database Statistics**\n\n"
        stats_text += f"📁 **Primary DB:** {primary_count} files\n"
        stats_text += f"📁 **Secondary DB:** {secondary_count} files\n"
        stats_text += f"📊 **Total Files:** {total_files} files"
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        await message.reply_text(f"❌ Error getting database stats: {e}")


@Client.on_message(filters.command("cleanup") & filters.user(ADMINS))
async def cleanup_database(bot, message):
    """Clean up orphaned files (admin only)"""
    try:
        await message.reply_text("🧹 Starting database cleanup...")
        
        # This would typically involve more complex logic to identify orphaned files
        # For now, just show a message
        await message.reply_text(
            "🧹 **Database Cleanup**\n\n"
            "This feature is under development. It will help identify and remove:\n"
            "• Orphaned file references\n"
            "• Duplicate entries\n"
            "• Corrupted data\n\n"
            "Check back later for updates!"
        )
        
    except Exception as e:
        logger.error(f"Error in database cleanup: {e}")
        await message.reply_text(f"❌ Error during cleanup: {e}")
