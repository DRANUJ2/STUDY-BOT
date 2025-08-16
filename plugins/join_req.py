import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ChatJoinRequest
from config import *
from database.study_db import db
from utils import temp, get_readable_time

logger = logging.getLogger(__name__)

@Client.on_chat_join_request()
async def handle_join_request(client, chat_join_request):
    """Handle chat join requests"""
    try:
        chat = chat_join_request.chat
        user = chat_join_request.from_user
        
        # Log the join request
        logger.info(f"Join request from {user.id} ({user.first_name}) to {chat.id} ({chat.title})")
        
        # Store join request in database
        await db.add_join_request(
            user_id=user.id,
            chat_id=chat.id,
            user_name=user.first_name,
            chat_title=chat.title,
            timestamp=int(asyncio.get_event_loop().time())
        )
        
        # Send notification to admins if configured
        if LOG_CHANNEL:
            try:
                notification_text = (
                    f"🔔 **New Join Request**\n\n"
                    f"👤 **User:** {user.mention} (`{user.id}`)\n"
                    f"🏘️ **Chat:** {chat.title} (`{chat.id}`)\n"
                    f"📅 **Time:** {get_readable_time(int(asyncio.get_event_loop().time()))}\n"
                    f"🔗 **Chat Type:** {chat.type.value}"
                )
                
                buttons = [
                    [
                        InlineKeyboardButton("✅ Approve", callback_data=f"approve_join_{user.id}_{chat.id}"),
                        InlineKeyboardButton("❌ Decline", callback_data=f"decline_join_{user.id}_{chat.id}")
                    ],
                    [
                        InlineKeyboardButton("👤 User Info", callback_data=f"user_info_{user.id}"),
                        InlineKeyboardButton("🏘️ Chat Info", callback_data=f"chat_info_{chat.id}")
                    ]
                ]
                
                reply_markup = InlineKeyboardMarkup(buttons)
                
                await client.send_message(
                    LOG_CHANNEL,
                    notification_text,
                    reply_markup=reply_markup
                )
                
            except Exception as e:
                logger.error(f"Failed to send join request notification: {e}")
        
    except Exception as e:
        logger.error(f"Error handling join request: {e}")

@Client.on_callback_query(filters.regex(r"^approve_join_"))
async def approve_join_request(client, callback_query):
    """Approve join request"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    try:
        _, _, user_id, chat_id = callback_query.data.split("_")
        user_id = int(user_id)
        chat_id = int(chat_id)
        
        # Approve the join request
        await client.approve_chat_join_request(chat_id, user_id)
        
        # Update database
        await db.update_join_request(user_id, chat_id, {"status": "approved", "approved_by": callback_query.from_user.id})
        
        # Send success message
        await callback_query.answer("✅ Join request approved!")
        
        # Update the message
        await callback_query.message.edit_text(
            f"✅ **Join Request Approved**\n\n"
            f"👤 **User:** `{user_id}`\n"
            f"🏘️ **Chat:** `{chat_id}`\n"
            f"👮 **Approved by:** {callback_query.from_user.mention}\n"
            f"⏰ **Time:** {get_readable_time(int(asyncio.get_event_loop().time()))}"
        )
        
        # Notify the user
        try:
            await client.send_message(
                user_id,
                f"✅ **Your join request has been approved!**\n\n"
                f"🏘️ **Chat:** {callback_query.message.text.split('Chat:')[1].split('(')[0].strip()}\n"
                f"👮 **Approved by:** Admin\n"
                f"⏰ **Time:** {get_readable_time(int(asyncio.get_event_loop().time()))}"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
        
        logger.info(f"Join request approved: user {user_id} to chat {chat_id} by {callback_query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error approving join request: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^decline_join_"))
async def decline_join_request(client, callback_query):
    """Decline join request"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    try:
        _, _, user_id, chat_id = callback_query.data.split("_")
        user_id = int(user_id)
        chat_id = int(chat_id)
        
        # Decline the join request
        await client.decline_chat_join_request(chat_id, user_id)
        
        # Update database
        await db.update_join_request(user_id, chat_id, {"status": "declined", "declined_by": callback_query.from_user.id})
        
        # Send success message
        await callback_query.answer("❌ Join request declined!")
        
        # Update the message
        await callback_query.message.edit_text(
            f"❌ **Join Request Declined**\n\n"
            f"👤 **User:** `{user_id}`\n"
            f"🏘️ **Chat:** `{chat_id}`\n"
            f"👮 **Declined by:** {callback_query.from_user.mention}\n"
            f"⏰ **Time:** {get_readable_time(int(asyncio.get_event_loop().time()))}"
        )
        
        # Notify the user
        try:
            await client.send_message(
                user_id,
                f"❌ **Your join request has been declined**\n\n"
                f"🏘️ **Chat:** {callback_query.message.text.split('Chat:')[1].split('(')[0].strip()}\n"
                f"👮 **Declined by:** Admin\n"
                f"⏰ **Time:** {get_readable_time(int(asyncio.get_event_loop().time()))}\n\n"
                f"💡 You can try joining again later or contact support for more information."
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
        
        logger.info(f"Join request declined: user {user_id} to chat {chat_id} by {callback_query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error declining join request: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^user_info_"))
async def show_user_info(client, callback_query):
    """Show user information"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    try:
        user_id = int(callback_query.data.split("_")[2])
        
        # Get user from database
        user = await db.get_user(user_id)
        
        if user:
            user_info_text = f"👤 **User Information**\n\n"
            user_info_text += f"🆔 **User ID:** `{user_id}`\n"
            user_info_text += f"📝 **Name:** {user.get('name', 'Unknown')}\n"
            user_info_text += f"📅 **Joined:** {get_readable_time(user.get('joined_at', 0))}\n"
            user_info_text += f"🔒 **Banned:** {'Yes' if user.get('banned', False) else 'No'}\n"
            user_info_text += f"📊 **Study Sessions:** {len(user.get('study_sessions', []))}\n"
            user_info_text += f"⏱️ **Total Study Time:** {get_readable_time(sum(session.get('duration', 0) for session in user.get('study_sessions', [])))}"
        else:
            user_info_text = f"👤 **User Information**\n\n"
            user_info_text += f"🆔 **User ID:** `{user_id}`\n"
            user_info_text += f"❌ **User not found in database**"
        
        # Add buttons
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_join_request")],
            [InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_user_{user_id}")],
            [InlineKeyboardButton("📊 User Stats", callback_data=f"user_stats_{user_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        # Store original message for back button
        temp.ORIGINAL_JOIN_REQUEST_MESSAGE = callback_query.message
        
        await callback_query.message.edit_text(user_info_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error showing user info: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^chat_info_"))
async def show_chat_info(client, callback_query):
    """Show chat information"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    try:
        chat_id = int(callback_query.data.split("_")[2])
        
        # Get chat information
        chat = await client.get_chat(chat_id)
        
        chat_info_text = f"🏘️ **Chat Information**\n\n"
        chat_info_text += f"🆔 **Chat ID:** `{chat_id}`\n"
        chat_info_text += f"📝 **Title:** {chat.title}\n"
        chat_info_text += f"🔗 **Type:** {chat.type.value}\n"
        chat_info_text += f"👥 **Members:** {chat.members_count if hasattr(chat, 'members_count') else 'Unknown'}\n"
        chat_info_text += f"📅 **Created:** {get_readable_time(chat.date) if hasattr(chat, 'date') else 'Unknown'}"
        
        if chat.description:
            chat_info_text += f"\n📄 **Description:** {chat.description[:100]}{'...' if len(chat.description) > 100 else ''}"
        
        # Add buttons
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_join_request")],
            [InlineKeyboardButton("📊 Chat Stats", callback_data=f"chat_stats_{chat_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        # Store original message for back button
        temp.ORIGINAL_JOIN_REQUEST_MESSAGE = callback_query.message
        
        await callback_query.message.edit_text(chat_info_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error showing chat info: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^back_to_join_request$"))
async def back_to_join_request(client, callback_query):
    """Go back to join request message"""
    if hasattr(temp, 'ORIGINAL_JOIN_REQUEST_MESSAGE'):
        original_message = temp.ORIGINAL_JOIN_REQUEST_MESSAGE
        delattr(temp, 'ORIGINAL_JOIN_REQUEST_MESSAGE')
        
        # Restore original message
        await callback_query.message.edit_text(
            original_message.text,
            reply_markup=original_message.reply_markup
        )
    else:
        await callback_query.answer("❌ Original message not found!")

@Client.on_callback_query(filters.regex(r"^ban_user_"))
async def ban_user_from_join_request(client, callback_query):
    """Ban user from join request"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    try:
        user_id = int(callback_query.data.split("_")[2])
        
        # Ban the user
        await db.update_user(user_id, {
            'banned': True,
            'ban_reason': 'Join request abuse',
            'banned_by': callback_query.from_user.id,
            'banned_at': int(asyncio.get_event_loop().time())
        })
        
        await callback_query.answer("✅ User banned successfully!")
        
        # Update the message
        await callback_query.message.edit_text(
            f"🚫 **User Banned**\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"📝 **Reason:** Join request abuse\n"
            f"👮 **Banned by:** {callback_query.from_user.mention}\n"
            f"⏰ **Time:** {get_readable_time(int(asyncio.get_event_loop().time()))}"
        )
        
        logger.info(f"User {user_id} banned from join request by {callback_query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)

@Client.on_message(filters.command("joinrequests") & filters.private)
async def show_join_requests_command(client, message):
    """Show pending join requests"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is only for admins!")
        return
    
    await show_pending_join_requests(client, message)

async def show_pending_join_requests(client, message):
    """Show pending join requests"""
    try:
        # Get pending join requests from database
        pending_requests = await db.get_pending_join_requests()
        
        if not pending_requests:
            await message.reply_text("✅ **No pending join requests found.**")
            return
        
        requests_text = f"🔔 **Pending Join Requests**\n\n"
        requests_text += f"📊 **Total Pending:** {len(pending_requests)}\n\n"
        
        for i, request in enumerate(pending_requests[:10], 1):  # Show first 10
            user_id = request.get('user_id', 'Unknown')
            chat_id = request.get('chat_id', 'Unknown')
            user_name = request.get('user_name', 'Unknown')
            chat_title = request.get('chat_title', 'Unknown')
            timestamp = request.get('timestamp', 0)
            
            requests_text += f"{i}. **User:** {user_name} (`{user_id}`)\n"
            requests_text += f"   🏘️ **Chat:** {chat_title} (`{chat_id}`)\n"
            requests_text += f"   ⏰ **Time:** {get_readable_time(timestamp)}\n\n"
        
        if len(pending_requests) > 10:
            requests_text += f"... and {len(pending_requests) - 10} more requests."
        
        buttons = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_join_requests")],
            [InlineKeyboardButton("📊 View All", callback_data="view_all_join_requests")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(requests_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting join requests: {e}")
        await message.reply_text(f"❌ Error getting join requests: {e}")

@Client.on_callback_query(filters.regex(r"^refresh_join_requests$"))
async def refresh_join_requests_callback(client, callback_query):
    """Refresh join requests list"""
    await show_pending_join_requests(client, callback_query.message)
    await callback_query.answer("🔄 Join requests refreshed!")

@Client.on_callback_query(filters.regex(r"^view_all_join_requests$"))
async def view_all_join_requests_callback(client, callback_query):
    """View all join requests"""
    try:
        # Get all join requests from database
        all_requests = await db.get_all_join_requests()
        
        if not all_requests:
            await callback_query.answer("✅ No join requests found!", show_alert=True)
            return
        
        # Create detailed list
        detailed_text = f"📋 **All Join Requests**\n\n"
        detailed_text += f"📊 **Total Requests:** {len(all_requests)}\n\n"
        
        for request in all_requests:
            user_id = request.get('user_id', 'Unknown')
            chat_id = request.get('chat_id', 'Unknown')
            user_name = request.get('user_name', 'Unknown')
            chat_title = request.get('chat_title', 'Unknown')
            status = request.get('status', 'pending')
            timestamp = request.get('timestamp', 0)
            
            status_emoji = "⏳" if status == "pending" else "✅" if status == "approved" else "❌"
            
            detailed_text += f"{status_emoji} **{status.title()}**\n"
            detailed_text += f"👤 **User:** {user_name} (`{user_id}`)\n"
            detailed_text += f"🏘️ **Chat:** {chat_title} (`{chat_id}`)\n"
            detailed_text += f"⏰ **Time:** {get_readable_time(timestamp)}\n"
            detailed_text += "-" * 40 + "\n"
        
        # Send as file if too long
        if len(detailed_text) > 4000:
            await callback_query.message.reply_document(
                document=detailed_text.encode(),
                filename="join_requests.txt",
                caption="📋 All Join Requests"
            )
        else:
            await callback_query.message.reply_text(detailed_text)
        
        await callback_query.answer("📋 All join requests displayed!")
        
    except Exception as e:
        logger.error(f"Error viewing all join requests: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)
