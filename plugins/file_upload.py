import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.study_db import db, StudyFiles, Batches, Chapters, Users, StudySessions, ContentAnalytics, BotSettings, JoinRequests, Chats, GroupSettings, save_file
from config import *
from studybot.Bot import studybot, content_bot
import re
import os

logger = logging.getLogger(__name__)

# Handle file uploads in content bot
@content_bot.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file_upload(client: Client, message: Message):
    """Handle file uploads to content bot"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Only admins can upload files.")
            return
        
        # Extract file information
        if message.document:
            file = message.document
            file_type = "Document"
            file_name = file.file_name
            file_size = file.file_size
            mime_type = file.mime_type
        elif message.video:
            file = message.video
            file_type = "Video"
            file_name = file.file_name or f"video_{file.file_id}.mp4"
            file_size = file.file_size
            mime_type = "video/mp4"
        elif message.audio:
            file = message.audio
            file_type = "Audio"
            file_name = file.file_name or f"audio_{file.file_id}.mp3"
            file_size = file.file_size
            mime_type = "audio/mpeg"
        elif message.photo:
            file = message.photo[-1]  # Get the largest photo
            file_type = "Photo"
            file_name = f"photo_{file.file_id}.jpg"
            file_size = file.file_size
            mime_type = "image/jpeg"
        else:
            return
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            await message.reply_text(
                f"❌ **File Too Large!**\n\n"
                f"📁 **File:** {file_name}\n"
                f"📏 **Size:** {get_file_size(file_size)}\n"
                f"🚫 **Max Allowed:** {get_file_size(MAX_FILE_SIZE)}\n\n"
                f"💡 **Please compress the file or use a smaller one.**"
            )
            return
        
        # Send file info and request metadata
        await message.reply_text(
            f"📁 **File Received Successfully!**\n\n"
            f"📄 **File:** {file_name}\n"
            f"📏 **Size:** {get_file_size(file_size)}\n"
            f"📝 **Type:** {file_type}\n"
            f"🔗 **MIME:** {mime_type}\n\n"
            f"📝 **Please provide file metadata in this format:**\n"
            f"`/fileinfo <batch_name> <subject> <teacher> <chapter> <content_type>`\n\n"
            f"**Example:**\n"
            f"`/fileinfo NEET2026 Physics Mr_Sir CH01 Lectures`"
        )
        
        # Store file info temporarily
        temp.FILE_UPLOADS[user_id] = {
            "file_id": file.file_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
            "mime_type": mime_type,
            "message_id": message.message_id
        }
        
        logger.info(f"Admin {user_id} uploaded file: {file_name} ({file_type})")
        
    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        await message.reply_text("❌ An error occurred while processing the file.")

# Handle file info command
@content_bot.on_message(filters.command("fileinfo") & filters.private)
async def handle_file_info(client: Client, message: Message):
    """Handle file metadata information"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Only admins can upload files.")
            return
        
        # Check if user has uploaded a file
        if user_id not in temp.FILE_UPLOADS:
            await message.reply_text(
                "❌ **No File Found!**\n\n"
                f"📝 **Please upload a file first, then use this command.**\n\n"
                f"**Steps:**\n"
                f"1. Upload your file\n"
                f"2. Use `/fileinfo <batch_name> <subject> <teacher> <chapter> <content_type>`"
            )
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=5)
        if len(command_parts) < 6:
            await message.reply_text(
                "❌ **Invalid Format!**\n\n"
                f"📝 **Usage:** `/fileinfo <batch_name> <subject> <teacher> <chapter> <content_type>`\n\n"
                f"**Example:**\n"
                f"`/fileinfo NEET2026 Physics Mr_Sir CH01 Lectures`\n\n"
                f"**Available Content Types:**\n"
                f"• Lectures\n"
                f"• DPP Quiz\n"
                f"• DPP PDF\n"
                f"• Mind Maps\n"
                f"• Revision\n"
                f"• Short Notes\n"
                f"• PYQs\n"
                f"• KPP PDF\n"
                f"• KPP Solution\n"
                f"• Practice Sheet\n"
                f"• Kattar NEET 2026\n"
                f"• IMPORTANT\n"
                f"• Handwritten Notes\n"
                f"• Module Question"
            )
            return
        
        batch_name = command_parts[1].strip()
        subject = command_parts[2].strip()
        teacher = command_parts[3].strip()
        chapter = command_parts[4].strip()
        content_type = command_parts[5].strip()
        
        # Validate content type
        valid_content_types = [
            "Lectures", "DPP Quiz", "DPP PDF", "Mind Maps", "Revision", 
            "Short Notes", "PYQs", "KPP PDF", "KPP Solution", "Practice Sheet",
            "Kattar NEET 2026", "IMPORTANT", "Handwritten Notes", "Module Question"
        ]
        
        if content_type not in valid_content_types:
            await message.reply_text(
                f"❌ **Invalid Content Type!**\n\n"
                f"📝 **Received:** {content_type}\n\n"
                f"✅ **Valid Types:**\n"
                f"{chr(10).join([f'• {ct}' for ct in valid_content_types])}"
            )
            return
        
        # Check if batch exists
        existing_batch = await Batches.find_one({"batch_name": batch_name})
        if not existing_batch:
            await message.reply_text(
                f"❌ **Batch Not Found!**\n\n"
                f"📚 **Batch:** {batch_name}\n\n"
                f"💡 **Please create the batch first using:**\n"
                f"`/addbatch {batch_name}`"
            )
            return
        
        # Get file info
        file_info = temp.FILE_UPLOADS[user_id]
        
        # Create or update study file entry
        existing_file = await StudyFiles.find_one({
            "batch_name": batch_name,
            "subject": subject,
            "teacher": teacher,
            "chapter_no": chapter,
            "content_type": content_type
        })
        
        if existing_file:
            # Update existing file
            existing_file.file_id = file_info["file_id"]
            existing_file.file_name = file_info["file_name"]
            existing_file.file_size = file_info["file_size"]
            existing_file.file_type = file_info["file_type"]
            existing_file.mime_type = file_info["mime_type"]
            existing_file.uploaded_at = datetime.utcnow()
            existing_file.uploaded_by = user_id
            existing_file.is_active = True
            
            await existing_file.commit()
            
            await message.reply_text(
                f"✅ **File Updated Successfully!**\n\n"
                f"📚 **Batch:** {batch_name}\n"
                f"🧪 **Subject:** {subject}\n"
                f"👨‍🏫 **Teacher:** {teacher}\n"
                f"📖 **Chapter:** {chapter}\n"
                f"📝 **Content Type:** {content_type}\n"
                f"📄 **File:** {file_info['file_name']}\n"
                f"📏 **Size:** {get_file_size(file_info['file_size'])}\n"
                f"📅 **Updated:** {existing_file.uploaded_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"👤 **Updated By:** {user_id}"
            )
            
            logger.info(f"Admin {user_id} updated file: {batch_name} - {subject} - {teacher} - {chapter} - {content_type}")
            
        else:
            # Create new file entry
            study_file = StudyFiles(
                batch_name=batch_name,
                subject=subject,
                teacher=teacher,
                chapter_no=chapter,
                content_type=content_type,
                file_id=file_info["file_id"],
                file_name=file_info["file_name"],
                file_size=file_info["file_size"],
                file_type=file_info["file_type"],
                mime_type=file_info["mime_type"],
                uploaded_at=datetime.utcnow(),
                uploaded_by=user_id,
                is_active=True
            )
            
            await study_file.commit()
            
            await message.reply_text(
                f"✅ **File Added Successfully!**\n\n"
                f"📚 **Batch:** {batch_name}\n"
                f"🧪 **Subject:** {subject}\n"
                f"👨‍🏫 **Teacher:** {teacher}\n"
                f"📖 **Chapter:** {chapter}\n"
                f"📝 **Content Type:** {content_type}\n"
                f"📄 **File:** {file_info['file_name']}\n"
                f"📏 **Size:** {get_file_size(file_info['file_size'])}\n"
                f"📅 **Added:** {study_file.uploaded_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"👤 **Added By:** {user_id}"
            )
            
            logger.info(f"Admin {user_id} added new file: {batch_name} - {subject} - {teacher} - {chapter} - {content_type}")
        
        # Clear temporary file info
        del temp.FILE_UPLOADS[user_id]
        
    except Exception as e:
        logger.error(f"Error handling file info: {e}")
        await message.reply_text("❌ An error occurred while processing file information.")

# Handle file deletion
@content_bot.on_message(filters.command("delfile") & filters.private)
async def handle_file_deletion(client: Client, message: Message):
    """Handle file deletion"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Only admins can delete files.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=5)
        if len(command_parts) < 6:
            await message.reply_text(
                "❌ **Invalid Format!**\n\n"
                f"📝 **Usage:** `/delfile <batch_name> <subject> <teacher> <chapter> <content_type>`\n\n"
                f"**Example:**\n"
                f"`/delfile NEET2026 Physics Mr_Sir CH01 Lectures`"
            )
            return
        
        batch_name = command_parts[1].strip()
        subject = command_parts[2].strip()
        teacher = command_parts[3].strip()
        chapter = command_parts[4].strip()
        content_type = command_parts[5].strip()
        
        # Delete file from database
        result = await StudyFiles.delete_one({
            "batch_name": batch_name,
            "subject": subject,
            "teacher": teacher,
            "chapter_no": chapter,
            "content_type": content_type
        })
        
        if result.deleted_count > 0:
            await message.reply_text(
                f"✅ **File Deleted Successfully!**\n\n"
                f"📚 **Batch:** {batch_name}\n"
                f"🧪 **Subject:** {subject}\n"
                f"👨‍🏫 **Teacher:** {teacher}\n"
                f"📖 **Chapter:** {chapter}\n"
                f"📝 **Content Type:** {content_type}\n"
                f"👤 **Deleted By:** {user_id}"
            )
            
            logger.info(f"Admin {user_id} deleted file: {batch_name} - {subject} - {teacher} - {chapter} - {content_type}")
        else:
            await message.reply_text(f"❌ File not found!")
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        await message.reply_text("❌ An error occurred while deleting the file.")

# Handle file list command
@content_bot.on_message(filters.command("listfiles") & filters.private)
async def handle_file_list(client: Client, message: Message):
    """List files for a specific batch/subject/chapter"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Only admins can list files.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=3)
        if len(command_parts) < 2:
            await message.reply_text(
                "❌ **Invalid Format!**\n\n"
                f"📝 **Usage:** `/listfiles <batch_name> [subject] [chapter]`\n\n"
                f"**Examples:**\n"
                f"• `/listfiles NEET2026` - List all files for batch\n"
                f"• `/listfiles NEET2026 Physics` - List files for subject\n"
                f"• `/listfiles NEET2026 Physics CH01` - List files for chapter"
            )
            return
        
        batch_name = command_parts[1].strip()
        subject = command_parts[2].strip() if len(command_parts) > 2 else None
        chapter = command_parts[3].strip() if len(command_parts) > 3 else None
        
        # Build query
        query = {"batch_name": batch_name}
        if subject:
            query["subject"] = subject
        if chapter:
            query["chapter_no"] = chapter
        
        # Get files
        files = await StudyFiles.find(query).sort("uploaded_at", -1).to_list(length=50)
        
        if not files:
            await message.reply_text(
                f"❌ **No Files Found!**\n\n"
                f"📚 **Batch:** {batch_name}\n"
                f"🧪 **Subject:** {subject or 'All'}\n"
                f"📖 **Chapter:** {chapter or 'All'}"
            )
            return
        
        # Create file list
        files_text = f"📁 **Files Found:** {len(files)}\n\n"
        files_text += f"📚 **Batch:** {batch_name}\n"
        if subject:
            files_text += f"🧪 **Subject:** {subject}\n"
        if chapter:
            files_text += f"📖 **Chapter:** {chapter}\n"
        files_text += "\n"
        
        for i, file in enumerate(files, 1):
            files_text += f"{i}. 📄 **{file.file_name}**\n"
            files_text += f"   🧪 {file.subject} - {file.teacher}\n"
            files_text += f"   📖 {file.chapter_no} - {file.content_type}\n"
            files_text += f"   📏 {get_file_size(file.file_size)}\n"
            files_text += f"   📅 {file.uploaded_at.strftime('%Y-%m-%d')}\n\n"
        
        # Add pagination if needed
        if len(files) == 50:
            files_text += "💡 **Note:** Showing first 50 files. Use more specific filters to see more."
        
        await message.reply_text(files_text)
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        await message.reply_text("❌ An error occurred while listing files.")

# Handle file search command
@content_bot.on_message(filters.command("searchfiles") & filters.private)
async def handle_file_search(client: Client, message: Message):
    """Search files by keyword"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin/owner
        if user_id not in OWNER_ID and not await is_admin(user_id):
            await message.reply_text("❌ Access denied. Only admins can search files.")
            return
        
        # Check command format
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text(
                "❌ **Invalid Format!**\n\n"
                f"📝 **Usage:** `/searchfiles <keyword>`\n\n"
                f"**Examples:**\n"
                f"• `/searchfiles Physics` - Search for Physics files\n"
                f"• `/searchfiles CH01` - Search for Chapter 1 files\n"
                f"• `/searchfiles Lectures` - Search for lecture files"
            )
            return
        
        keyword = command_parts[1].strip()
        
        # Search files
        files = await StudyFiles.find({
            "$or": [
                {"batch_name": {"$regex": keyword, "$options": "i"}},
                {"subject": {"$regex": keyword, "$options": "i"}},
                {"teacher": {"$regex": keyword, "$options": "i"}},
                {"chapter_no": {"$regex": keyword, "$options": "i"}},
                {"content_type": {"$regex": keyword, "$options": "i"}},
                {"file_name": {"$regex": keyword, "$options": "i"}}
            ]
        }).sort("uploaded_at", -1).to_list(length=20)
        
        if not files:
            await message.reply_text(
                f"❌ **No Files Found!**\n\n"
                f"🔍 **Search Term:** {keyword}\n\n"
                f"💡 **Try different keywords or check spelling.**"
            )
            return
        
        # Create search results
        results_text = f"🔍 **Search Results:** {len(files)} files\n\n"
        results_text += f"🔍 **Search Term:** {keyword}\n\n"
        
        for i, file in enumerate(files, 1):
            results_text += f"{i}. 📄 **{file.file_name}**\n"
            results_text += f"   📚 {file.batch_name} - {file.subject}\n"
            results_text += f"   👨‍🏫 {file.teacher} - {file.chapter_no}\n"
            results_text += f"   📝 {file.content_type}\n"
            results_text += f"   📏 {get_file_size(file.file_size)}\n\n"
        
        # Add pagination note
        if len(files) == 20:
            results_text += "💡 **Note:** Showing first 20 results. Use more specific search terms."
        
        await message.reply_text(results_text)
        
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        await message.reply_text("❌ An error occurred while searching files.")

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
logger.info("File Upload plugin loaded successfully")
