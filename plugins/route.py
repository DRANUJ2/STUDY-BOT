import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import *
from database.study_db import db
from utils import temp, get_readable_time

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("route") & filters.private)
async def route_command(client, message):
    """Handle route command for navigation"""
    user_id = message.from_user.id
    
    # Check if user exists in database
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
    
    # Show route options
    buttons = [
        [InlineKeyboardButton("🏠 Home", callback_data="route_home")],
        [InlineKeyboardButton("📚 Study Materials", callback_data="route_study")],
        [InlineKeyboardButton("🔍 Search", callback_data="route_search")],
        [InlineKeyboardButton("📊 Progress", callback_data="route_progress")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="route_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        "🚀 **Study Bot Navigation**\n\nChoose your destination:",
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex(r"^route_"))
async def route_callback(client, callback_query):
    """Handle route callback queries"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    if data == "route_home":
        await show_home(client, callback_query)
    elif data == "route_study":
        await show_study_materials(client, callback_query)
    elif data == "route_search":
        await show_search(client, callback_query)
    elif data == "route_progress":
        await show_progress(client, callback_query)
    elif data == "route_settings":
        await show_settings(client, callback_query)
    
    await callback_query.answer()

async def show_home(client, callback_query):
    """Show home page"""
    buttons = [
        [InlineKeyboardButton("📚 Start Learning", callback_data="start_learning")],
        [InlineKeyboardButton("🔍 Search Content", callback_data="search_content")],
        [InlineKeyboardButton("📊 My Progress", callback_data="my_progress")],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(
        "🏠 **Welcome to Study Bot!**\n\n"
        "Your personal learning companion. Choose an option to get started:",
        reply_markup=reply_markup
    )

async def show_study_materials(client, callback_query):
    """Show study materials options"""
    buttons = [
        [InlineKeyboardButton("📖 Lectures", callback_data="materials_lectures")],
        [InlineKeyboardButton("📝 DPP", callback_data="materials_dpp")],
        [InlineKeyboardButton("📚 All Materials", callback_data="materials_all")],
        [InlineKeyboardButton("🔙 Back", callback_data="route_home")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(
        "📚 **Study Materials**\n\n"
        "Choose the type of study material you need:",
        reply_markup=reply_markup
    )

async def show_search(client, callback_query):
    """Show search options"""
    buttons = [
        [InlineKeyboardButton("🔍 Search by Topic", callback_data="search_topic")],
        [InlineKeyboardButton("📖 Search by Chapter", callback_data="search_chapter")],
        [InlineKeyboardButton("👨‍🏫 Search by Teacher", callback_data="search_teacher")],
        [InlineKeyboardButton("🔙 Back", callback_data="route_home")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(
        "🔍 **Search Options**\n\n"
        "How would you like to search for content?",
        reply_markup=reply_markup
    )

async def show_progress(client, callback_query):
    """Show user progress"""
    user_id = callback_query.from_user.id
    
    # Get user progress from database
    user = await db.get_user(user_id)
    if user:
        total_sessions = len(user.get('study_sessions', []))
        total_time = sum(session.get('duration', 0) for session in user.get('study_sessions', []))
        
        progress_text = f"📊 **Your Progress**\n\n"
        progress_text += f"📚 Total Study Sessions: {total_sessions}\n"
        progress_text += f"⏱️ Total Study Time: {get_readable_time(total_time)}\n"
        progress_text += f"🎯 Current Streak: {user.get('current_streak', 0)} days\n"
        progress_text += f"🏆 Achievements: {len(user.get('achievements', []))}"
    else:
        progress_text = "📊 **Your Progress**\n\nNo progress data available yet."
    
    buttons = [
        [InlineKeyboardButton("📈 Detailed Stats", callback_data="detailed_stats")],
        [InlineKeyboardButton("🏆 Achievements", callback_data="achievements")],
        [InlineKeyboardButton("🔙 Back", callback_data="route_home")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(progress_text, reply_markup=reply_markup)

async def show_settings(client, callback_query):
    """Show user settings"""
    user_id = callback_query.from_user.id
    
    # Get user settings
    user = await db.get_user(user_id)
    if user:
        pm_enabled = user.get('pm_enabled', True)
        notifications = user.get('notifications', True)
        auto_save = user.get('auto_save', False)
        
        settings_text = f"⚙️ **Your Settings**\n\n"
        settings_text += f"💬 PM Mode: {'✅ Enabled' if pm_enabled else '❌ Disabled'}\n"
        settings_text += f"🔔 Notifications: {'✅ Enabled' if notifications else '❌ Disabled'}\n"
        settings_text += f"💾 Auto Save: {'✅ Enabled' if auto_save else '❌ Disabled'}"
    else:
        settings_text = "⚙️ **Your Settings**\n\nDefault settings applied."
    
    buttons = [
        [InlineKeyboardButton("💬 Toggle PM", callback_data="toggle_pm")],
        [InlineKeyboardButton("🔔 Toggle Notifications", callback_data="toggle_notifications")],
        [InlineKeyboardButton("💾 Toggle Auto Save", callback_data="toggle_auto_save")],
        [InlineKeyboardButton("🔙 Back", callback_data="route_home")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(settings_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^toggle_"))
async def toggle_settings(client, callback_query):
    """Handle setting toggles"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    if data == "toggle_pm":
        await toggle_pm_setting(client, callback_query, user_id)
    elif data == "toggle_notifications":
        await toggle_notification_setting(client, callback_query, user_id)
    elif data == "toggle_auto_save":
        await toggle_auto_save_setting(client, callback_query, user_id)
    
    await callback_query.answer()

async def toggle_pm_setting(client, callback_query, user_id):
    """Toggle PM setting"""
    user = await db.get_user(user_id)
    current_pm = user.get('pm_enabled', True) if user else True
    
    new_pm = not current_pm
    await db.update_user(user_id, {'pm_enabled': new_pm})
    
    status = "✅ Enabled" if new_pm else "❌ Disabled"
    await callback_query.answer(f"PM Mode: {status}")
    
    # Refresh settings display
    await show_settings(client, callback_query)

async def toggle_notification_setting(client, callback_query, user_id):
    """Toggle notification setting"""
    user = await db.get_user(user_id)
    current_notif = user.get('notifications', True) if user else True
    
    new_notif = not current_notif
    await db.update_user(user_id, {'notifications': new_notif})
    
    status = "✅ Enabled" if new_notif else "❌ Disabled"
    await callback_query.answer(f"Notifications: {status}")
    
    # Refresh settings display
    await show_settings(client, callback_query)

async def toggle_auto_save_setting(client, callback_query, user_id):
    """Toggle auto save setting"""
    user = await db.get_user(user_id)
    current_auto = user.get('auto_save', False) if user else False
    
    new_auto = not current_auto
    await db.update_user(user_id, {'auto_save': new_auto})
    
    status = "✅ Enabled" if new_auto else "❌ Disabled"
    await callback_query.answer(f"Auto Save: {status}")
    
    # Refresh settings display
    await show_settings(client, callback_query)
