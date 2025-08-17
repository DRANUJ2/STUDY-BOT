from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, MULTIPLE_DB, LOG_CHANNEL, OWNER_LNK, MELCOW_PHOTO
from database.users_chats_db import db, db2
from database.ia_filterdb import Media, Media2, db as ia_db, db2 as ia_db2
from utils import get_size, temp, get_settings, get_readable_time
from Script import script
from pyrogram.errors import ChatAdminRequired
import asyncio
import psutil
import logging
from time import time
from bot import botStartTime

"""-----------------------------------------Study Bot - Group Management--------------------------------------"""

@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    """Handle new chat members and save group to database"""
    study_bot_check = [u.id for u in message.new_chat_members]
    if temp.ME in study_bot_check:
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            study_bot_user = message.from_user.mention if message.from_user else "Anonymous" 
            await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, study_bot_user))       
            await db.add_chat(message.chat.id, message.chat.title)
        
        if message.chat.id in temp.BANNED_CHATS:
            buttons = [[InlineKeyboardButton('📌 Contact Support 📌', url=OWNER_LNK)]]
            reply_markup = InlineKeyboardMarkup(buttons)
            k = await message.reply_text(
                '<b>Chat not allowed 🐞\n\nMy admins has restricted me from working here! If you want to know more about it contact support.</b>',
                reply_markup=reply_markup
            )
            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        
        buttons = [[
            InlineKeyboardButton("👩‍🌾 Bot Owner 👩‍🌾", url=OWNER_LNK)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>Thank you for adding me in {message.chat.title} ❣️\n\nIf you have any questions & doubts about using me contact support.</b>",
            reply_markup=reply_markup
        )
        try:
            await db.connect_group(message.chat.id, message.from_user.id)
        except Exception as e:
            logging.error(f"DB error connecting group: {e}")
    else:
        settings = await get_settings(message.chat.id)

        if settings.get("welcome"):
            for u in message.new_chat_members:
                if temp.MELCOW.get('welcome'):
                    try:
                        await temp.MELCOW['welcome'].delete()
                    except:
                        pass
                try:
                    temp.MELCOW['welcome'] = await message.reply_photo(
                        photo=MELCOW_PHOTO,
                        caption=script.MELCOW_ENG.format(u.mention, message.chat.title),
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("📌 Contact Support 📌", url=OWNER_LNK)
                            ]
                        ]),
                        parse_mode=enums.ParseMode.HTML
                    )
                except Exception as e:
                    print(f"Welcome photo send failed: {e}")
        
        if settings.get("auto_delete"):
            await asyncio.sleep(600)
            try:
                if temp.MELCOW.get('welcome'):
                    await temp.MELCOW['welcome'].delete()
                    temp.MELCOW['welcome'] = None 
            except:
                pass

@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    """Leave a chat (admin only)"""
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton("📌 Contact Support 📌", url=OWNER_LNK)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='<b>Hello friends, \nMy admin has told me to leave from group, so I have to go! \nIf you want to add me again contact support.</b>',
            reply_markup=reply_markup,
        )

        await bot.leave_chat(chat)
        await message.reply(f"left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'Error - {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    """Disable a chat (admin only)"""
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = r[1]
    else:
        chat = r[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        k = await bot.get_chat(chat_)
    except:
        return await message.reply("This is an invalid chat, try one more time!")
    else:
        chat = k.id
    try:
        await db.disable_chat(chat_, reason)
        temp.BANNED_CHATS.add(chat_)
        await message.reply(f"Successfully disabled the chat `{chat_}`")
    except Exception as e:
        await message.reply(f"Error - {e}")

@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def enable_chat(bot, message):
    """Enable a chat (admin only)"""
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        k = await bot.get_chat(chat_)
    except:
        return await message.reply("This is an invalid chat, try one more time!")
    else:
        chat = k.id
    try:
        await db.enable_chat(chat_)
        temp.BANNED_CHATS.discard(chat_)
        await message.reply(f"Successfully enabled the chat `{chat_}`")
    except Exception as e:
        await message.reply(f"Error - {e}")

@Client.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot, message):
    """Show bot statistics (admin only)"""
    if message.from_user.id not in ADMINS:
        return await message.reply("❌ This command is only for admins!")
    
    try:
        # Get database statistics
        total_users = await db.total_users_count()
        total_chats = await db.total_chat_count()
        
        # Get file statistics
        file_stats = await get_file_stats()
        total_files = file_stats.get("total", {}).get("count", 0)
        
        # Calculate uptime
        uptime = get_readable_time(time() - botStartTime)
        
        # Get system info
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        stats_text = f"📊 **Study Bot Statistics**\n\n"
        stats_text += f"👥 **Total Users:** `{total_users}`\n"
        stats_text += f"🏘️ **Total Groups:** `{total_chats}`\n"
        stats_text += f"📁 **Total Files:** `{total_files}`\n"
        stats_text += f"⏱️ **Uptime:** `{uptime}`\n"
        stats_text += f"🖥️ **CPU Usage:** `{cpu_usage}%`\n"
        stats_text += f"💾 **Memory Usage:** `{memory_usage}%`"
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        logging.error(f"Error getting stats: {e}")
        await message.reply_text(f"❌ Error getting statistics: {e}")

@Client.on_message(filters.command('broadcast') & filters.user(ADMINS))
async def broadcast_handler(bot, message):
    """Broadcast message to all users (admin only)"""
    if message.from_user.id not in ADMINS:
        return await message.reply("❌ This command is only for admins!")
    
    if message.reply_to_message:
        broadcast_message = message.reply_to_message
    else:
        if len(message.command) < 2:
            return await message.reply("❌ Please provide a message to broadcast or reply to a message!")
        broadcast_message = " ".join(message.command[1:])
    
    try:
        users = await db.get_all_users()
        success_count = 0
        failed_count = 0
        
        await message.reply_text("📢 Starting broadcast...")
        
        for user in users:
            try:
                if isinstance(broadcast_message, str):
                    await bot.send_message(user['id'], broadcast_message)
                else:
                    await broadcast_message.copy(user['id'])
                success_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception as e:
                failed_count += 1
                logging.error(f"Failed to send to user {user['id']}: {e}")
        
        completion_text = f"📢 **Broadcast Completed!**\n\n"
        completion_text += f"✅ Successfully sent: {success_count}\n"
        completion_text += f"❌ Failed: {failed_count}\n"
        completion_text += f"📊 Total Users: {len(users)}"
        
        await message.reply_text(completion_text)
        
    except Exception as e:
        logging.error(f"Error in broadcast: {e}")
        await message.reply_text(f"❌ Error during broadcast: {e}")

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_user_handler(bot, message):
    """Ban a user (admin only)"""
    if message.from_user.id not in ADMINS:
        return await message.reply("❌ This command is only for admins!")
    
    if len(message.command) < 2:
        return await message.reply("❌ Please provide a user ID to ban!")
    
    try:
        user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
        
        # Check if user exists
        user = await db.get_user(user_id)
        if not user:
            return await message.reply("❌ User not found in database!")
        
        # Ban the user
        await db.ban_user(user_id, reason)
        
        await message.reply_text(
            f"✅ **User Banned Successfully!**\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"📝 **Reason:** {reason}\n"
            f"👮 **Banned by:** {message.from_user.mention}"
        )
        
        # Try to notify the banned user
        try:
            ban_notification = (
                f"🚫 **You have been banned from Study Bot**\n\n"
                f"📝 **Reason:** {reason}\n"
                f"👮 **Banned by:** Admin\n\n"
                f"❓ If you think this is a mistake, contact support."
            )
            await bot.send_message(user_id, ban_notification)
        except Exception as e:
            logging.error(f"Failed to notify banned user {user_id}: {e}")
        
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
    except Exception as e:
        logging.error(f"Error banning user: {e}")
        await message.reply_text(f"❌ Error banning user: {e}")

@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_user_handler(bot, message):
    """Unban a user (admin only)"""
    if message.from_user.id not in ADMINS:
        return await message.reply("❌ This command is only for admins!")
    
    if len(message.command) < 2:
        return await message.reply("❌ Please provide a user ID to unban!")
    
    try:
        user_id = int(message.command[1])
        
        # Check if user exists
        user = await db.get_user(user_id)
        if not user:
            return await message.reply("❌ User not found in database!")
        
        # Check if user is banned
        ban_status = await db.get_ban_status(user_id)
        if not ban_status.get('is_banned'):
            return await message.reply("❌ User is not banned!")
        
        # Unban the user
        await db.remove_ban(user_id)
        
        await message.reply_text(
            f"✅ **User Unbanned Successfully!**\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"👮 **Unbanned by:** {message.from_user.mention}"
        )
        
        # Try to notify the unbanned user
        try:
            unban_notification = (
                f"✅ **You have been unbanned from Study Bot**\n\n"
                f"👮 **Unbanned by:** Admin\n\n"
                f"🎉 Welcome back! You can now use the bot again."
            )
            await bot.send_message(user_id, unban_notification)
        except Exception as e:
            logging.error(f"Failed to notify unbanned user {user_id}: {e}")
        
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
    except Exception as e:
        logging.error(f"Error unbanning user: {e}")
        await message.reply_text(f"❌ Error unbanning user: {e}")

@Client.on_message(filters.command('banlist') & filters.user(ADMINS))
async def ban_list_handler(bot, message):
    """Show list of banned users (admin only)"""
    if message.from_user.id not in ADMINS:
        return await message.reply("❌ This command is only for admins!")
    
    try:
        banned_users = await db.get_banned_users()
        
        if not banned_users:
            await message.reply_text("✅ **No banned users found.**")
            return
        
        ban_list_text = f"🚫 **Banned Users List**\n\n"
        ban_list_text += f"📊 **Total Banned:** {len(banned_users)}\n\n"
        
        for i, user in enumerate(banned_users[:20], 1):  # Show first 20
            user_id = user.get('id', 'Unknown')
            ban_reason = user.get('ban_status', {}).get('ban_reason', 'No reason')
            
            ban_list_text += f"{i}. **User ID:** `{user_id}`\n"
            ban_list_text += f"   📝 **Reason:** {ban_reason}\n\n"
        
        if len(banned_users) > 20:
            ban_list_text += f"... and {len(banned_users) - 20} more users."
        
        await message.reply_text(ban_list_text)
        
    except Exception as e:
        logging.error(f"Error getting ban list: {e}")
        await message.reply_text(f"❌ Error getting ban list: {e}")

@Client.on_message(filters.command('settings') & filters.group)
async def settings_handler(bot, message):
    """Show group settings"""
    try:
        chat_id = message.chat.id
        settings = await get_settings(chat_id)
        
        settings_text = f"⚙️ **Group Settings for {message.chat.title}**\n\n"
        settings_text += f"🔍 **Auto Filter:** {'✅ Enabled' if settings.get('auto_filter', True) else '❌ Disabled'}\n"
        settings_text += f"💬 **Welcome:** {'✅ Enabled' if settings.get('welcome', True) else '❌ Disabled'}\n"
        settings_text += f"🗑️ **Auto Delete:** {'✅ Enabled' if settings.get('auto_delete', False) else '❌ Disabled'}\n"
        settings_text += f"🔒 **File Secure:** {'✅ Enabled' if settings.get('file_secure', True) else '❌ Disabled'}\n"
        settings_text += f"📝 **File Mode:** {settings.get('file_mode', 'document')}"
        
        buttons = [
            [
                InlineKeyboardButton("🔍 Toggle Auto Filter", callback_data=f"setting_auto_filter_{chat_id}"),
                InlineKeyboardButton("💬 Toggle Welcome", callback_data=f"setting_welcome_{chat_id}")
            ],
            [
                InlineKeyboardButton("🗑️ Toggle Auto Delete", callback_data=f"setting_auto_delete_{chat_id}"),
                InlineKeyboardButton("🔒 Toggle File Secure", callback_data=f"setting_file_secure_{chat_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(settings_text, reply_markup=reply_markup)
        
    except Exception as e:
        logging.error(f"Error showing settings: {e}")
        await message.reply_text(f"❌ Error showing settings: {e}")

@Client.on_message(filters.command('help') & filters.group)
async def help_handler(bot, message):
    """Show help for group users"""
    help_text = (
        "📚 **Study Bot Help**\n\n"
        "**Available Commands:**\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this help message\n"
        "• `/settings` - Show group settings\n"
        "• `/stats` - Show bot statistics (Admin only)\n"
        "• `/broadcast` - Broadcast message (Admin only)\n"
        "• `/ban` - Ban a user (Admin only)\n"
        "• `/unban` - Unban a user (Admin only)\n"
        "• `/banlist` - Show banned users (Admin only)\n\n"
        "**Features:**\n"
        "• Auto filter for study materials\n"
        "• Welcome messages for new members\n"
        "• File sharing and management\n"
        "• User management and moderation\n\n"
        "For more help, contact support!"
    )
    
    buttons = [[InlineKeyboardButton("📌 Contact Support 📌", url=OWNER_LNK)]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(help_text, reply_markup=reply_markup)

# Callback query handlers for settings
@Client.on_callback_query(filters.regex(r"^setting_"))
async def setting_callback(bot, callback_query):
    """Handle setting toggle callbacks"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    try:
        data = callback_query.data
        setting_type = data.split("_")[1]
        chat_id = int(data.split("_")[2])
        
        # Get current settings
        settings = await get_settings(chat_id)
        
        # Toggle the setting
        if setting_type == "auto_filter":
            new_value = not settings.get('auto_filter', True)
            await db.update_chat_settings(chat_id, {'auto_filter': new_value})
            status = "✅ Enabled" if new_value else "❌ Disabled"
            await callback_query.answer(f"Auto Filter: {status}")
            
        elif setting_type == "welcome":
            new_value = not settings.get('welcome', True)
            await db.update_chat_settings(chat_id, {'welcome': new_value})
            status = "✅ Enabled" if new_value else "❌ Disabled"
            await callback_query.answer(f"Welcome: {status}")
            
        elif setting_type == "auto_delete":
            new_value = not settings.get('auto_delete', False)
            await db.update_chat_settings(chat_id, {'auto_delete': new_value})
            status = "✅ Enabled" if new_value else "❌ Disabled"
            await callback_query.answer(f"Auto Delete: {status}")
            
        elif setting_type == "file_secure":
            new_value = not settings.get('file_secure', True)
            await db.update_chat_settings(chat_id, {'file_secure': new_value})
            status = "✅ Enabled" if new_value else "❌ Disabled"
            await callback_query.answer(f"File Secure: {status}")
        
        # Refresh the settings display
        await settings_handler(bot, callback_query.message)
        
    except Exception as e:
        logging.error(f"Error in setting callback: {e}")
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)
