import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from database.study_db import db as study_db
from config import *
from Script import script
from utils import temp, get_readable_time
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("channel") & filters.private)
async def channel_command(client, message):
    """Handle channel command"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is only for admins!")
        return
    
    buttons = [
        [InlineKeyboardButton("📢 Broadcast", callback_data="channel_broadcast")],
        [InlineKeyboardButton("📊 Channel Stats", callback_data="channel_stats")],
        [InlineKeyboardButton("🔗 Channel Links", callback_data="channel_links")],
        [InlineKeyboardButton("⚙️ Channel Settings", callback_data="channel_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        "📢 **Channel Management**\n\nChoose an option:",
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex(r"^channel_"))
async def channel_callback(client, callback_query):
    """Handle channel callback queries"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    if user_id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    if data == "channel_broadcast":
        await show_broadcast_options(client, callback_query)
    elif data == "channel_stats":
        await show_channel_stats(client, callback_query)
    elif data == "channel_links":
        await show_channel_links(client, callback_query)
    elif data == "channel_settings":
        await show_channel_settings(client, callback_query)
    
    await callback_query.answer()

async def show_broadcast_options(client, callback_query):
    """Show broadcast options"""
    buttons = [
        [InlineKeyboardButton("📢 Broadcast to All Users", callback_data="broadcast_all")],
        [InlineKeyboardButton("👥 Broadcast to Groups", callback_data="broadcast_groups")],
        [InlineKeyboardButton("📱 Broadcast to PM Users", callback_data="broadcast_pm")],
        [InlineKeyboardButton("🔙 Back", callback_data="channel_back")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(
        "📢 **Broadcast Options**\n\nChoose broadcast target:",
        reply_markup=reply_markup
    )

async def show_channel_stats(client, callback_query):
    """Show channel statistics"""
    try:
        # Get statistics from database
        total_users = await study_db.total_users_count()
        total_groups = await study_db.total_chat_count()
        total_files = await study_db.total_files_count()
        
        stats_text = f"📊 **Channel Statistics**\n\n"
        stats_text += f"👥 Total Users: {total_users}\n"
        stats_text += f"🏘️ Total Groups: {total_groups}\n"
        stats_text += f"📁 Total Files: {total_files}\n"
        stats_text += f"📅 Last Updated: {get_readable_time(int(asyncio.get_event_loop().time()))}"
        
        buttons = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="channel_stats")],
            [InlineKeyboardButton("🔙 Back", callback_data="channel_back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await callback_query.message.edit_text(stats_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting channel stats: {e}")
        await callback_query.message.edit_text(
            "❌ Error getting statistics. Please try again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="channel_back")
            ]])
        )

async def show_channel_links(client, callback_query):
    """Show channel links"""
    links_text = "🔗 **Channel Links**\n\n"
    links_text += f"📢 Main Channel: {MAIN_CHANNEL}\n"
    links_text += f"🔗 Support Group: {SUPPORT_GROUP}\n"
    links_text += f"📱 Bot Username: @{BOT_USERNAME}\n"
    links_text += f"🎯 Content Bot: @{CONTENT_BOT_USERNAME}"
    
    buttons = [
        [InlineKeyboardButton("🔗 Copy Main Channel", callback_data="copy_main_channel")],
        [InlineKeyboardButton("🔗 Copy Support Group", callback_data="copy_support_group")],
        [InlineKeyboardButton("🔙 Back", callback_data="channel_back")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(links_text, reply_markup=reply_markup)

async def show_channel_settings(client, callback_query):
    """Show channel settings"""
    settings_text = "⚙️ **Channel Settings**\n\n"
    settings_text += f"🔒 Auto Filter: {'✅ Enabled' if AUTO_FILTER else '❌ Disabled'}\n"
    settings_text += f"💬 PM Filter: {'✅ Enabled' if PM_FILTER else '❌ Disabled'}\n"
    settings_text += f"🔍 Auto Search: {'✅ Enabled' if AUTO_SEARCH else '❌ Disabled'}\n"
    settings_text += f"📝 Welcome Message: {'✅ Enabled' if WELCOME_MESSAGE else '❌ Disabled'}"
    
    buttons = [
        [InlineKeyboardButton("🔒 Toggle Auto Filter", callback_data="toggle_auto_filter")],
        [InlineKeyboardButton("💬 Toggle PM Filter", callback_data="toggle_pm_filter")],
        [InlineKeyboardButton("🔍 Toggle Auto Search", callback_data="toggle_auto_search")],
        [InlineKeyboardButton("🔙 Back", callback_data="channel_back")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(settings_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^broadcast_"))
async def broadcast_callback(client, callback_query):
    """Handle broadcast callbacks"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    if user_id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    if data == "broadcast_all":
        await start_broadcast(client, callback_query, "all")
    elif data == "broadcast_groups":
        await start_broadcast(client, callback_query, "groups")
    elif data == "broadcast_pm":
        await start_broadcast(client, callback_query, "pm")
    
    await callback_query.answer()

async def start_broadcast(client, callback_query, target):
    """Start broadcast process"""
    await callback_query.message.edit_text(
        f"📢 **Broadcast to {target.title()}**\n\n"
        "Send the message you want to broadcast.\n"
        "Use /cancel to cancel the broadcast.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")
        ]])
    )
    
    # Store broadcast state
    temp.BROADCAST_STATE = {
        'user_id': callback_query.from_user.id,
        'target': target,
        'active': True
    }

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_broadcast_command(client, message):
    """Cancel broadcast command"""
    if message.from_user.id not in ADMINS:
        return
    
    if hasattr(temp, 'BROADCAST_STATE') and temp.BROADCAST_STATE.get('active'):
        temp.BROADCAST_STATE['active'] = False
        await message.reply_text("❌ Broadcast cancelled!")
    else:
        await message.reply_text("❌ No active broadcast to cancel!")

@Client.on_message(filters.private & filters.text & filters.create(lambda _, __, m: not m.command) & filters.create(lambda _, __, m: not m.text.startswith('/')))
async def handle_broadcast_message(client, message):
    """Handle broadcast message"""
    if not hasattr(temp, 'BROADCAST_STATE') or not temp.BROADCAST_STATE.get('active'):
        return
    
    if message.from_user.id != temp.BROADCAST_STATE['user_id']:
        return
    
    target = temp.BROADCAST_STATE['target']
    message_text = message.text
    
    # Start broadcast process
    await start_broadcast_process(client, message, target, message_text)

async def start_broadcast_process(client, message, target, message_text):
    """Start the actual broadcast process"""
    try:
        await message.reply_text("📢 Starting broadcast...")
        
        success_count = 0
        failed_count = 0
        
        if target == "all" or target == "pm":
            # Broadcast to PM users
            users = await study_db.get_all_users()
            for user in users:
                try:
                    await client.send_message(user['user_id'], message_text)
                    success_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send to user {user['user_id']}: {e}")
        
        if target == "all" or target == "groups":
            # Broadcast to groups
            groups = await study_db.get_all_chats()
            for group in groups:
                try:
                    await client.send_message(group['chat_id'], message_text)
                    success_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send to group {group['chat_id']}: {e}")
        
        # Send completion message
        completion_text = f"📢 **Broadcast Completed!**\n\n"
        completion_text += f"✅ Successfully sent: {success_count}\n"
        completion_text += f"❌ Failed: {failed_count}\n"
        completion_text += f"🎯 Target: {target.title()}"
        
        await message.reply_text(completion_text)
        
        # Reset broadcast state
        temp.BROADCAST_STATE['active'] = False
        
    except Exception as e:
        logger.error(f"Error in broadcast process: {e}")
        await message.reply_text(f"❌ Error during broadcast: {e}")
        temp.BROADCAST_STATE['active'] = False

@Client.on_callback_query(filters.regex(r"^toggle_"))
async def toggle_channel_settings(client, callback_query):
    """Toggle channel settings"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    if user_id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    # This would typically update bot settings in database
    # For now, just show a message
    setting_name = data.replace("toggle_", "").replace("_", " ").title()
    await callback_query.answer(f"⚙️ {setting_name} setting updated!")
    
    # Refresh settings display
    await show_channel_settings(client, callback_query)

@Client.on_callback_query(filters.regex(r"^copy_"))
async def copy_channel_links(client, callback_query):
    """Copy channel links to clipboard"""
    data = callback_query.data
    
    if data == "copy_main_channel":
        link = MAIN_CHANNEL
        name = "Main Channel"
    elif data == "copy_support_group":
        link = SUPPORT_GROUP
        name = "Support Group"
    else:
        return
    
    # In a real bot, you might want to send the link as a separate message
    await callback_query.answer(f"🔗 {name} link copied!")
    
    # Send the link
    await callback_query.message.reply_text(f"🔗 **{name}**\n{link}")

@Client.on_callback_query(filters.regex(r"^channel_back$"))
async def channel_back(client, callback_query):
    """Go back to channel main menu"""
    await channel_command(client, callback_query.message)
