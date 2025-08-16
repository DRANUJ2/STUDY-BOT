import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import *
from database.study_db import db
from utils import temp, get_readable_time

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("ban") & filters.private)
async def ban_user_command(client, message):
    """Handle ban user command"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is only for admins!")
        return
    
    # Check if user ID is provided
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/ban <user_id> [reason]`\n\n"
            "**Example:** `/ban 123456789 Spamming`"
        )
        return
    
    try:
        user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
        
        await ban_user(client, message, user_id, reason)
        
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")

async def ban_user(client, message, user_id, reason):
    """Ban a user"""
    try:
        # Check if user exists
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text(f"❌ User {user_id} not found in database.")
            return
        
        # Check if user is already banned
        if user.get('banned', False):
            await message.reply_text(f"❌ User {user_id} is already banned.")
            return
        
        # Ban the user
        await db.update_user(user_id, {
            'banned': True,
            'ban_reason': reason,
            'banned_by': message.from_user.id,
            'banned_at': int(asyncio.get_event_loop().time())
        })
        
        await message.reply_text(
            f"✅ **User Banned Successfully!**\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"📝 **Reason:** {reason}\n"
            f"👮 **Banned by:** {message.from_user.mention}\n"
            f"⏰ **Banned at:** {get_readable_time(int(asyncio.get_event_loop().time()))}"
        )
        
        # Try to notify the banned user
        try:
            ban_notification = (
                f"🚫 **You have been banned from Study Bot**\n\n"
                f"📝 **Reason:** {reason}\n"
                f"👮 **Banned by:** Admin\n"
                f"⏰ **Banned at:** {get_readable_time(int(asyncio.get_event_loop().time()))}\n\n"
                f"❓ If you think this is a mistake, contact support."
            )
            await client.send_message(user_id, ban_notification)
        except Exception as e:
            logger.error(f"Failed to notify banned user {user_id}: {e}")
        
        # Log the ban action
        logger.info(f"User {user_id} banned by {message.from_user.id} for reason: {reason}")
        
    except Exception as e:
        logger.error(f"Error banning user {user_id}: {e}")
        await message.reply_text(f"❌ Error banning user: {e}")

@Client.on_message(filters.command("unban") & filters.private)
async def unban_user_command(client, message):
    """Handle unban user command"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is only for admins!")
        return
    
    # Check if user ID is provided
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/unban <user_id>`\n\n"
            "**Example:** `/unban 123456789`"
        )
        return
    
    try:
        user_id = int(message.command[1])
        await unban_user(client, message, user_id)
        
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")

async def unban_user(client, message, user_id):
    """Unban a user"""
    try:
        # Check if user exists
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text(f"❌ User {user_id} not found in database.")
            return
        
        # Check if user is banned
        if not user.get('banned', False):
            await message.reply_text(f"❌ User {user_id} is not banned.")
            return
        
        # Unban the user
        await db.update_user(user_id, {
            'banned': False,
            'ban_reason': None,
            'banned_by': None,
            'banned_at': None
        })
        
        await message.reply_text(
            f"✅ **User Unbanned Successfully!**\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"👮 **Unbanned by:** {message.from_user.mention}\n"
            f"⏰ **Unbanned at:** {get_readable_time(int(asyncio.get_event_loop().time()))}"
        )
        
        # Try to notify the unbanned user
        try:
            unban_notification = (
                f"✅ **You have been unbanned from Study Bot**\n\n"
                f"👮 **Unbanned by:** Admin\n"
                f"⏰ **Unbanned at:** {get_readable_time(int(asyncio.get_event_loop().time()))}\n\n"
                f"🎉 Welcome back! You can now use the bot again."
            )
            await client.send_message(user_id, unban_notification)
        except Exception as e:
            logger.error(f"Failed to notify unbanned user {user_id}: {e}")
        
        # Log the unban action
        logger.info(f"User {user_id} unbanned by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error unbanning user {user_id}: {e}")
        await message.reply_text(f"❌ Error unbanning user: {e}")

@Client.on_message(filters.command("banlist") & filters.private)
async def ban_list_command(client, message):
    """Handle ban list command"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is only for admins!")
        return
    
    await show_ban_list(client, message)

async def show_ban_list(client, message):
    """Show list of banned users"""
    try:
        # Get banned users from database
        banned_users = await db.get_banned_users()
        
        if not banned_users:
            await message.reply_text("✅ **No banned users found.**")
            return
        
        ban_list_text = f"🚫 **Banned Users List**\n\n"
        ban_list_text += f"📊 **Total Banned:** {len(banned_users)}\n\n"
        
        for i, user in enumerate(banned_users[:20], 1):  # Show first 20
            user_id = user.get('user_id', 'Unknown')
            reason = user.get('ban_reason', 'No reason')
            banned_at = user.get('banned_at', 0)
            banned_by = user.get('banned_by', 'Unknown')
            
            ban_list_text += f"{i}. **User ID:** `{user_id}`\n"
            ban_list_text += f"   📝 **Reason:** {reason}\n"
            ban_list_text += f"   ⏰ **Banned:** {get_readable_time(banned_at) if banned_at else 'Unknown'}\n"
            ban_list_text += f"   👮 **By:** {banned_by}\n\n"
        
        if len(banned_users) > 20:
            ban_list_text += f"... and {len(banned_users) - 20} more users."
        
        buttons = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_banlist")],
            [InlineKeyboardButton("📊 Export", callback_data="export_banlist")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(ban_list_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting ban list: {e}")
        await message.reply_text(f"❌ Error getting ban list: {e}")

@Client.on_message(filters.command("baninfo") & filters.private)
async def ban_info_command(client, message):
    """Handle ban info command"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is only for admins!")
        return
    
    # Check if user ID is provided
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/baninfo <user_id>`\n\n"
            "**Example:** `/baninfo 123456789`"
        )
        return
    
    try:
        user_id = int(message.command[1])
        await show_ban_info(client, message, user_id)
        
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")

async def show_ban_info(client, message, user_id):
    """Show ban information for a specific user"""
    try:
        # Get user from database
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text(f"❌ User {user_id} not found in database.")
            return
        
        if not user.get('banned', False):
            await message.reply_text(f"✅ User {user_id} is not banned.")
            return
        
        # Get ban information
        ban_reason = user.get('ban_reason', 'No reason provided')
        banned_at = user.get('banned_at', 0)
        banned_by = user.get('banned_by', 'Unknown')
        
        ban_info_text = f"🚫 **Ban Information**\n\n"
        ban_info_text += f"👤 **User ID:** `{user_id}`\n"
        ban_info_text += f"📝 **Ban Reason:** {ban_reason}\n"
        ban_info_text += f"⏰ **Banned At:** {get_readable_time(banned_at) if banned_at else 'Unknown'}\n"
        ban_info_text += f"👮 **Banned By:** {banned_by}\n"
        ban_info_text += f"📅 **Ban Duration:** {get_readable_time(int(asyncio.get_event_loop().time()) - banned_at) if banned_at else 'Unknown'}"
        
        buttons = [
            [InlineKeyboardButton("✅ Unban User", callback_data=f"unban_user_{user_id}")],
            [InlineKeyboardButton("📝 Edit Reason", callback_data=f"edit_ban_reason_{user_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(ban_info_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting ban info for user {user_id}: {e}")
        await message.reply_text(f"❌ Error getting ban info: {e}")

@Client.on_callback_query(filters.regex(r"^unban_user_"))
async def unban_user_callback(client, callback_query):
    """Handle unban user callback"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    user_id = int(callback_query.data.split("_")[2])
    
    try:
        await unban_user(client, callback_query.message, user_id)
        await callback_query.answer("✅ User unbanned successfully!")
        
    except Exception as e:
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^edit_ban_reason_"))
async def edit_ban_reason_callback(client, callback_query):
    """Handle edit ban reason callback"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    user_id = int(callback_query.data.split("_")[3])
    
    await callback_query.message.edit_text(
        f"📝 **Edit Ban Reason**\n\n"
        f"User ID: `{user_id}`\n\n"
        "Send the new ban reason:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit_reason")
        ]])
    )
    
    # Store edit state
    temp.EDIT_BAN_REASON = {
        'user_id': user_id,
        'admin_id': callback_query.from_user.id,
        'active': True
    }

@Client.on_message(filters.private & filters.text & ~filters.command & ~filters.regex(r"^/"))
async def handle_ban_reason_edit(client, message):
    """Handle ban reason edit message"""
    if not hasattr(temp, 'EDIT_BAN_REASON') or not temp.EDIT_BAN_REASON.get('active'):
        return
    
    if message.from_user.id != temp.EDIT_BAN_REASON['admin_id']:
        return
    
    user_id = temp.EDIT_BAN_REASON['user_id']
    new_reason = message.text
    
    try:
        # Update ban reason
        await db.update_user(user_id, {'ban_reason': new_reason})
        
        await message.reply_text(
            f"✅ **Ban Reason Updated!**\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"📝 **New Reason:** {new_reason}"
        )
        
        # Reset edit state
        temp.EDIT_BAN_REASON['active'] = False
        
    except Exception as e:
        logger.error(f"Error updating ban reason for user {user_id}: {e}")
        await message.reply_text(f"❌ Error updating ban reason: {e}")
        temp.EDIT_BAN_REASON['active'] = False

@Client.on_callback_query(filters.regex(r"^cancel_edit_reason$"))
async def cancel_edit_reason_callback(client, callback_query):
    """Cancel ban reason edit"""
    if hasattr(temp, 'EDIT_BAN_REASON'):
        temp.EDIT_BAN_REASON['active'] = False
    
    await callback_query.answer("❌ Edit cancelled!")
    await callback_query.message.edit_text("❌ Ban reason edit cancelled.")

@Client.on_callback_query(filters.regex(r"^refresh_banlist$"))
async def refresh_banlist_callback(client, callback_query):
    """Refresh ban list"""
    await show_ban_list(client, callback_query.message)
    await callback_query.answer("🔄 Ban list refreshed!")

@Client.on_callback_query(filters.regex(r"^export_banlist$"))
async def export_banlist_callback(client, callback_query):
    """Export ban list"""
    try:
        banned_users = await db.get_banned_users()
        
        if not banned_users:
            await callback_query.answer("✅ No banned users to export!", show_alert=True)
            return
        
        # Create export text
        export_text = "🚫 Banned Users Export\n"
        export_text += f"📅 Generated: {get_readable_time(int(asyncio.get_event_loop().time()))}\n"
        export_text += f"📊 Total: {len(banned_users)}\n\n"
        
        for user in banned_users:
            user_id = user.get('user_id', 'Unknown')
            reason = user.get('ban_reason', 'No reason')
            banned_at = user.get('banned_at', 0)
            
            export_text += f"User ID: {user_id}\n"
            export_text += f"Reason: {reason}\n"
            export_text += f"Banned At: {get_readable_time(banned_at) if banned_at else 'Unknown'}\n"
            export_text += "-" * 30 + "\n"
        
        # Send as file if too long
        if len(export_text) > 4000:
            await callback_query.message.reply_document(
                document=export_text.encode(),
                filename="banned_users.txt",
                caption="📁 Banned Users Export"
            )
        else:
            await callback_query.message.reply_text(export_text)
        
        await callback_query.answer("📁 Ban list exported!")
        
    except Exception as e:
        logger.error(f"Error exporting ban list: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)

# Middleware to check if user is banned
async def check_banned_user(client, message):
    """Check if user is banned before processing any message"""
    user_id = message.from_user.id
    
    try:
        user = await db.get_user(user_id)
        if user and user.get('banned', False):
            ban_reason = user.get('ban_reason', 'No reason provided')
            await message.reply_text(
                f"🚫 **You are banned from using this bot**\n\n"
                f"📝 **Reason:** {ban_reason}\n\n"
                f"❓ If you think this is a mistake, contact support."
            )
            return True  # User is banned
        return False  # User is not banned
        
    except Exception as e:
        logger.error(f"Error checking ban status for user {user_id}: {e}")
        return False  # Allow user if error occurs
