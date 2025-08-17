import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.study_db import db as study_db, StudyFiles, Batches, Chapters, Users, StudySessions, ContentAnalytics, BotSettings, JoinRequests, Chats, GroupSettings, search_study_files, get_study_files
from config import *
from studybot.Bot import content_bot
import re

logger = logging.getLogger(__name__)

@content_bot.on_message(filters.command("start") & filters.private)
async def content_start_command(client: Client, message: Message):
    """Handle /start command for content bot"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    welcome_text = f"""Hello {first_name}! 👋

All your Files will be sent here.

Go back to bot & use.

⚠️ **Note:** Forwarding and saving content is restricted."""
    
    await message.reply_text(welcome_text)

@content_bot.on_message(filters.command("help") & filters.private)
async def content_help_command(client: Client, message: Message):
    """Handle /help command for content bot"""
    help_text = """📚 **Content Bot Help**

This bot is designed to deliver study materials to you.

**Features:**
• 📖 Receive study files
• 📝 Get notes and DPPs
• 🎯 Access lectures
• 📚 Download materials

**How to use:**
1. Go back to the main Study Bot
2. Use /Anuj <batch_name> command
3. Select your subject, teacher, and chapter
4. Choose content type
5. Files will be sent here automatically

**Note:** This bot is controlled by the main Study Bot."""
    
    await message.reply_text(help_text)

@content_bot.on_message(filters.command("search") & filters.private)
async def content_search_command(client: Client, message: Message):
    """Handle /search command for content bot"""
    try:
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("❌ Usage: /search <query>\n\nExample: /search Physics CH01")
            return
        
        query = command_parts[1].strip()
        
        # Search for files
        files = await search_study_files(query, limit=10)
        
        if not files:
            await message.reply_text(f"❌ No files found for: {query}")
            return
        
        # Send search results
        result_text = f"🔍 **Search Results for:** {query}\n\n"
        
        for i, file in enumerate(files, 1):
            result_text += f"{i}. 📄 **{file.file_name}**\n"
            result_text += f"   📚 Batch: {file.batch_name}\n"
            result_text += f"   🧪 Subject: {file.subject}\n"
            result_text += f"   📖 Chapter: {file.chapter_no or 'N/A'}\n"
            result_text += f"   📝 Type: {file.content_type}\n"
            result_text += f"   📏 Size: {file.file_size} bytes\n\n"
        
        # Add navigation buttons
        keyboard = []
        if len(files) > 5:
            keyboard.append([
                InlineKeyboardButton("⬅️ Previous", callback_data=f"search_prev_{query}_0"),
                InlineKeyboardButton("Next ➡️", callback_data=f"search_next_{query}_5")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await message.reply_text(result_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in content search: {e}")
        await message.reply_text("❌ An error occurred during search")

@content_bot.on_message(filters.command("recent") & filters.private)
async def content_recent_command(client: Client, message: Message):
    """Handle /recent command to show recent files"""
    try:
        # Get recent files
        files = await get_study_files(limit=10)
        
        if not files:
            await message.reply_text("❌ No recent files found")
            return
        
        # Send recent files list
        result_text = "📚 **Recent Study Files**\n\n"
        
        for i, file in enumerate(files, 1):
            result_text += f"{i}. 📄 **{file.file_name}**\n"
            result_text += f"   📚 {file.batch_name} - {file.subject}\n"
            result_text += f"   📖 Chapter: {file.chapter_no or 'N/A'}\n"
            result_text += f"   📝 Type: {file.content_type}\n\n"
        
        await message.reply_text(result_text)
        
    except Exception as e:
        logger.error(f"Error in content recent: {e}")
        await message.reply_text("❌ An error occurred")

@content_bot.on_message(filters.command("stats") & filters.private)
async def content_stats_command(client: Client, message: Message):
    """Handle /stats command for content bot"""
    try:
        # Get user stats
        user_id = message.from_user.id
        user = await Users.find_one({"_id": user_id})
        
        if not user:
            await message.reply_text("❌ User not found")
            return
        
        stats_text = f"📊 **Your Study Statistics**\n\n"
        stats_text += f"👤 **User:** {user.first_name}\n"
        stats_text += f"📚 **Current Batch:** {user.current_batch or 'None'}\n"
        stats_text += f"📥 **Total Downloads:** {user.total_downloads}\n"
        stats_text += f"⏱️ **Total Time Spent:** {user.total_time_spent} minutes\n"
        stats_text += f"🏆 **Achievements:** {len(user.achievements)}\n"
        stats_text += f"📅 **Joined:** {user.joined_at.strftime('%Y-%m-%d')}\n"
        stats_text += f"🕐 **Last Active:** {user.last_active.strftime('%Y-%m-%d %H:%M')}\n"
        
        if user.achievements:
            stats_text += f"\n🏅 **Achievements:**\n"
            for achievement in user.achievements[:5]:  # Show first 5
                stats_text += f"• {achievement}\n"
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        logger.error(f"Error in content stats: {e}")
        await message.reply_text("❌ An error occurred")

@content_bot.on_message(filters.command("batch") & filters.private)
async def content_batch_command(client: Client, message: Message):
    """Handle /batch command to show available batches"""
    try:
        # Get all active batches
        batches = await Batches.find({"is_active": True}).to_list(length=50)
        
        if not batches:
            await message.reply_text("❌ No batches available")
            return
        
        # Send batches list
        result_text = "📚 **Available Study Batches**\n\n"
        
        for i, batch in enumerate(batches, 1):
            result_text += f"{i}. 📚 **{batch.batch_name}**\n"
            result_text += f"   🧪 Subjects: {', '.join(batch.subjects)}\n"
            result_text += f"   👨‍🏫 Teachers: {', '.join(batch.teachers)}\n"
            result_text += f"   📅 Created: {batch.created_at.strftime('%Y-%m-%d')}\n\n"
        
        await message.reply_text(result_text)
        
    except Exception as e:
        logger.error(f"Error in content batch: {e}")
        await message.reply_text("❌ An error occurred")

@content_bot.on_message(filters.command("progress") & filters.private)
async def content_progress_command(client: Client, message: Message):
    """Handle /progress command to show study progress"""
    try:
        user_id = message.from_user.id
        user = await Users.find_one({"_id": user_id})
        
        if not user or not user.study_progress:
            await message.reply_text("❌ No study progress found")
            return
        
        # Show progress
        progress_text = "📈 **Your Study Progress**\n\n"
        
        for progress_key, progress_data in user.study_progress.items():
            batch_name, subject, chapter_no = progress_key.split('.')
            progress_text += f"📚 **{batch_name}** - {subject}\n"
            progress_text += f"   📖 Chapter: {chapter_no}\n"
            
            for content_type, count in progress_data.items():
                progress_text += f"   📝 {content_type}: {count} files\n"
            
            progress_text += "\n"
        
        await message.reply_text(progress_text)
        
    except Exception as e:
        logger.error(f"Error in content progress: {e}")
        await message.reply_text("❌ An error occurred")

# Handle file forwarding from main bot
@content_bot.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_content_files(client: Client, message: Message):
    """Handle content files sent to the content bot"""
    try:
        # Extract file information
        if message.document:
            file = message.document
            file_type = "Document"
        elif message.video:
            file = message.video
            file_type = "Video"
        elif message.audio:
            file = message.audio
            file_type = "Audio"
        elif message.photo:
            file = message.photo[-1]  # Get the largest photo
            file_type = "Photo"
        else:
            return
        
        # Log file received
        logger.info(f"Content file received: {file.file_name} ({file_type}) from {message.from_user.id}")
        
        # Send confirmation
        await message.reply_text(
            f"✅ **{file_type} Received**\n\n"
            f"📄 **File:** {file.file_name}\n"
            f"📏 **Size:** {file.file_size} bytes\n"
            f"📝 **Type:** {file_type}\n\n"
            f"File has been processed and is ready for delivery."
        )
        
    except Exception as e:
        logger.error(f"Error handling content file: {e}")
        await message.reply_text("❌ Error processing file")

# Handle text messages for content delivery
@content_bot.on_message(filters.text & filters.private & ~filters.command)
async def handle_content_text(client: Client, message: Message):
    """Handle text messages for content delivery"""
    try:
        # Check if this is a content delivery message
        if "Here's your requested content:" in message.text:
            # This is a content delivery message, no need to process further
            return
        
        # Check if this is a search result
        if "Search Results for:" in message.text:
            # This is a search result, no need to process further
            return
        
        # For other text messages, provide help
        await message.reply_text(
            "💡 **Need Help?**\n\n"
            "Use these commands:\n"
            "• /start - Welcome message\n"
            "• /help - Show help\n"
            "• /search <query> - Search files\n"
            "• /recent - Recent files\n"
            "• /stats - Your statistics\n"
            "• /batch - Available batches\n"
            "• /progress - Study progress\n\n"
            "Or go back to the main Study Bot to request content!"
        )
        
    except Exception as e:
        logger.error(f"Error handling content text: {e}")

# Handle callback queries for search navigation
@content_bot.on_callback_query(filters.regex(r"^search_(prev|next)_"))
async def handle_search_navigation(client: Client, callback_query):
    """Handle search navigation callbacks"""
    try:
        data = callback_query.data
        _, direction, query, offset = data.split("_", 3)
        offset = int(offset)
        
        # Get search results
        files = await search_study_files(query, limit=10, skip=offset)
        
        if not files:
            await callback_query.answer("❌ No more results", show_alert=True)
            return
        
        # Create result text
        result_text = f"🔍 **Search Results for:** {query}\n\n"
        
        for i, file in enumerate(files, 1):
            result_text += f"{offset + i}. 📄 **{file.file_name}**\n"
            result_text += f"   📚 Batch: {file.batch_name}\n"
            result_text += f"   🧪 Subject: {file.subject}\n"
            result_text += f"   📖 Chapter: {file.chapter_no or 'N/A'}\n"
            result_text += f"   📝 Type: {file.content_type}\n\n"
        
        # Create navigation buttons
        keyboard = []
        if offset > 0:
            keyboard.append([InlineKeyboardButton("⬅️ Previous", callback_data=f"search_prev_{query}_{offset-5}")])
        
        if len(files) == 10:  # If we got full page, there might be more
            keyboard.append([InlineKeyboardButton("Next ➡️", callback_data=f"search_next_{query}_{offset+5}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        # Edit the message
        await callback_query.edit_message_text(result_text, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in search navigation: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Error handler
@content_bot.on_message(filters.all)
async def handle_all_messages(client: Client, message: Message):
    """Handle all other message types"""
    try:
        # Log unexpected message types
        logger.info(f"Unexpected message type: {message.media} from {message.from_user.id}")
        
        # Send helpful response
        await message.reply_text(
            "❓ **Unsupported Message Type**\n\n"
            "This bot only handles text messages and files.\n"
            "Please use text commands or send files for processing.\n\n"
            "Use /help for available commands."
        )
        
    except Exception as e:
        logger.error(f"Error handling unexpected message: {e}")

# Log when content bot starts
@content_bot.on_start()
async def content_bot_start(client: Client):
    """Log when content bot starts"""
    logger.info("Content Bot started successfully")
    logger.info("Content Bot is ready to receive and deliver study materials")

# Log when content bot stops
@content_bot.on_stop()
async def content_bot_stop(client: Client):
    """Log when content bot stops"""
    logger.info("Content Bot stopped")
