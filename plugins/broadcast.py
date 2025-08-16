import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import *
from database.study_db import db
from utils import temp, get_readable_time

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client, message):
    """Handle broadcast command"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is only for admins!")
        return
    
    # Check if there are command arguments
    if len(message.command) > 1:
        # Direct broadcast with message
        broadcast_message = " ".join(message.command[1:])
        await start_direct_broadcast(client, message, broadcast_message)
    else:
        # Interactive broadcast
        await show_broadcast_menu(client, message)

async def show_broadcast_menu(client, message):
    """Show broadcast menu"""
    buttons = [
        [InlineKeyboardButton("📢 Broadcast to All", callback_data="broadcast_all")],
        [InlineKeyboardButton("👥 Broadcast to Groups", callback_data="broadcast_groups")],
        [InlineKeyboardButton("📱 Broadcast to PM Users", callback_data="broadcast_pm")],
        [InlineKeyboardButton("🎯 Broadcast to Specific Users", callback_data="broadcast_specific")],
        [InlineKeyboardButton("📊 Broadcast Stats", callback_data="broadcast_stats")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        "📢 **Broadcast Menu**\n\nChoose broadcast target:",
        reply_markup=reply_markup
    )

async def start_direct_broadcast(client, message, broadcast_message):
    """Start direct broadcast with provided message"""
    await message.reply_text("📢 Starting direct broadcast...")
    
    try:
        success_count = 0
        failed_count = 0
        
        # Get all users
        users = await db.get_all_users()
        
        for user in users:
            try:
                await client.send_message(user['user_id'], broadcast_message)
                success_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send to user {user['user_id']}: {e}")
        
        # Send completion message
        completion_text = f"📢 **Direct Broadcast Completed!**\n\n"
        completion_text += f"✅ Successfully sent: {success_count}\n"
        completion_text += f"❌ Failed: {failed_count}\n"
        completion_text += f"📝 Message: {broadcast_message[:100]}{'...' if len(broadcast_message) > 100 else ''}"
        
        await message.reply_text(completion_text)
        
    except Exception as e:
        logger.error(f"Error in direct broadcast: {e}")
        await message.reply_text(f"❌ Error during broadcast: {e}")

@Client.on_callback_query(filters.regex(r"^broadcast_"))
async def broadcast_callback(client, callback_query):
    """Handle broadcast callback queries"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    if user_id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    if data == "broadcast_all":
        await start_broadcast_process(client, callback_query, "all")
    elif data == "broadcast_groups":
        await start_broadcast_process(client, callback_query, "groups")
    elif data == "broadcast_pm":
        await start_broadcast_process(client, callback_query, "pm")
    elif data == "broadcast_specific":
        await start_specific_broadcast(client, callback_query)
    elif data == "broadcast_stats":
        await show_broadcast_stats(client, callback_query)
    
    await callback_query.answer()

async def start_broadcast_process(client, callback_query, target):
    """Start broadcast process for specific target"""
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

async def start_specific_broadcast(client, callback_query):
    """Start broadcast to specific users"""
    await callback_query.message.edit_text(
        "🎯 **Specific User Broadcast**\n\n"
        "Send user IDs separated by commas, then send the message.\n"
        "Example: 123456789, 987654321\n\n"
        "Use /cancel to cancel.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")
        ]])
    )
    
    # Store broadcast state
    temp.BROADCAST_STATE = {
        'user_id': callback_query.from_user.id,
        'target': 'specific',
        'active': True,
        'waiting_for_users': True
    }

async def show_broadcast_stats(client, callback_query):
    """Show broadcast statistics"""
    try:
        # Get statistics from database
        total_users = await db.total_users_count()
        total_groups = await db.total_chat_count()
        
        stats_text = f"📊 **Broadcast Statistics**\n\n"
        stats_text += f"👥 Total Users: {total_users}\n"
        stats_text += f"🏘️ Total Groups: {total_groups}\n"
        stats_text += f"📅 Last Updated: {get_readable_time(int(asyncio.get_event_loop().time()))}"
        
        buttons = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="broadcast_stats")],
            [InlineKeyboardButton("🔙 Back", callback_data="broadcast_back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await callback_query.message.edit_text(stats_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting broadcast stats: {e}")
        await callback_query.message.edit_text(
            "❌ Error getting statistics. Please try again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="broadcast_back")
            ]])
        )

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

@Client.on_message(filters.private & filters.text & ~filters.command & ~filters.regex(r"^/"))
async def handle_broadcast_message(client, message):
    """Handle broadcast message"""
    if not hasattr(temp, 'BROADCAST_STATE') or not temp.BROADCAST_STATE.get('active'):
        return
    
    if message.from_user.id != temp.BROADCAST_STATE['user_id']:
        return
    
    target = temp.BROADCAST_STATE['target']
    message_text = message.text
    
    if target == 'specific' and temp.BROADCAST_STATE.get('waiting_for_users'):
        # Handle user IDs input
        await handle_user_ids_input(client, message, message_text)
    else:
        # Handle broadcast message
        await start_broadcast_process(client, message, target, message_text)

async def handle_user_ids_input(client, message, user_ids_text):
    """Handle user IDs input for specific broadcast"""
    try:
        # Parse user IDs
        user_ids = [int(uid.strip()) for uid in user_ids_text.split(',') if uid.strip().isdigit()]
        
        if not user_ids:
            await message.reply_text("❌ Invalid user IDs. Please provide valid numeric IDs separated by commas.")
            return
        
        # Store user IDs and wait for message
        temp.BROADCAST_STATE['specific_users'] = user_ids
        temp.BROADCAST_STATE['waiting_for_users'] = False
        
        await message.reply_text(
            f"✅ User IDs received: {len(user_ids)} users\n\n"
            "Now send the message you want to broadcast to these users.\n"
            "Use /cancel to cancel."
        )
        
    except Exception as e:
        logger.error(f"Error parsing user IDs: {e}")
        await message.reply_text("❌ Error parsing user IDs. Please check the format.")

async def start_broadcast_process(client, message, target, message_text):
    """Start the actual broadcast process"""
    try:
        await message.reply_text("📢 Starting broadcast...")
        
        success_count = 0
        failed_count = 0
        
        if target == "all" or target == "pm":
            # Broadcast to PM users
            users = await db.get_all_users()
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
            groups = await db.get_all_chats()
            for group in groups:
                try:
                    await client.send_message(group['chat_id'], message_text)
                    success_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send to group {group['chat_id']}: {e}")
        
        if target == "specific":
            # Broadcast to specific users
            specific_users = temp.BROADCAST_STATE.get('specific_users', [])
            for user_id in specific_users:
                try:
                    await client.send_message(user_id, message_text)
                    success_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send to user {user_id}: {e}")
        
        # Send completion message
        completion_text = f"📢 **Broadcast Completed!**\n\n"
        completion_text += f"✅ Successfully sent: {success_count}\n"
        completion_text += f"❌ Failed: {failed_count}\n"
        completion_text += f"🎯 Target: {target.title()}"
        
        if target == "specific":
            completion_text += f"\n👥 Users: {len(temp.BROADCAST_STATE.get('specific_users', []))}"
        
        await message.reply_text(completion_text)
        
        # Reset broadcast state
        temp.BROADCAST_STATE['active'] = False
        
    except Exception as e:
        logger.error(f"Error in broadcast process: {e}")
        await message.reply_text(f"❌ Error during broadcast: {e}")
        temp.BROADCAST_STATE['active'] = False

@Client.on_callback_query(filters.regex(r"^cancel_broadcast$"))
async def cancel_broadcast_callback(client, callback_query):
    """Cancel broadcast from callback"""
    if hasattr(temp, 'BROADCAST_STATE') and temp.BROADCAST_STATE.get('active'):
        temp.BROADCAST_STATE['active'] = False
        await callback_query.answer("❌ Broadcast cancelled!")
        await callback_query.message.edit_text("❌ Broadcast cancelled!")
    else:
        await callback_query.answer("❌ No active broadcast to cancel!")

@Client.on_callback_query(filters.regex(r"^broadcast_back$"))
async def broadcast_back(client, callback_query):
    """Go back to broadcast menu"""
    await show_broadcast_menu(client, callback_query.message)

@Client.on_message(filters.command("testbroadcast") & filters.private)
async def test_broadcast_command(client, message):
    """Test broadcast command - sends to admin only"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is only for admins!")
        return
    
    test_message = "🧪 **Test Broadcast**\n\nThis is a test broadcast message to verify the broadcast system is working correctly."
    
    try:
        await client.send_message(message.from_user.id, test_message)
        await message.reply_text("✅ Test broadcast sent successfully!")
    except Exception as e:
        logger.error(f"Error in test broadcast: {e}")
        await message.reply_text(f"❌ Error in test broadcast: {e}")
