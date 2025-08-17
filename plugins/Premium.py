import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from database.study_db import db as study_db
from config import *
from Script import script
from utils import temp, get_readable_time
from datetime import datetime, timedelta
import pytz

@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium(client, message):
    """Remove premium access from a user"""
    if len(message.command) == 2:
        try:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            
            if await study_db.remove_premium_access(user_id):
                await message.reply_text("✅ **Premium access removed successfully!**")
                
                # Notify the user
                try:
                    await client.send_message(
                        chat_id=user_id,
                        text=script.PREMIUM_END_TEXT.format(user.mention)
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user {user_id}: {e}")
                
                logger.info(f"Premium access removed from user {user_id} by {message.from_user.id}")
            else:
                await message.reply_text("❌ **Unable to remove premium access!**\n\nAre you sure it was a premium user ID?")
        except ValueError:
            await message.reply_text("❌ **Invalid user ID!** Please provide a valid numeric user ID.")
        except Exception as e:
            logger.error(f"Error removing premium access: {e}")
            await message.reply_text(f"❌ **Error:** {e}")
    else:
        await message.reply_text("❌ **Usage:** `/remove_premium <user_id>`")

@Client.on_message(filters.command("myplan"))
async def myplan(client, message):
    """Show user's premium plan information"""
    try:
        user = message.from_user.mention
        user_id = message.from_user.id
        
        # Get user data from database
        user_data = await study_db.get_user(user_id)
        
        if user_data and user_data.get("premium_expiry"):
            expiry = user_data.get("premium_expiry")
            current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
            
            # Calculate time left
            if isinstance(expiry, str):
                # Parse string date
                expiry_dt = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                expiry_dt = expiry_dt.astimezone(pytz.timezone("Asia/Kolkata"))
            else:
                expiry_dt = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            
            time_left = expiry_dt - current_time
            
            if time_left.total_seconds() > 0:
                days = time_left.days
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
                
                expiry_str = expiry_dt.strftime("%d-%m-%Y\n⏱️ Expiry time: %I:%M:%S %p")
                
                caption = (
                    f"⚜️ **Premium User Data**\n\n"
                    f"👤 **User:** {user}\n"
                    f"⚡ **User ID:** `{user_id}`\n"
                    f"⏰ **Time Left:** {time_left_str}\n"
                    f"⌛️ **Expiry Date:** {expiry_str}\n\n"
                    f"🎯 **Premium Benefits:**\n"
                    f"• Unlimited study materials\n"
                    f"• Priority support\n"
                    f"• Advanced features\n"
                    f"• No ads"
                )
                
                buttons = [
                    [InlineKeyboardButton("🔥 Extend Plan", callback_data="premium_info")],
                    [InlineKeyboardButton("📊 Usage Stats", callback_data="premium_stats")]
                ]
                
                reply_markup = InlineKeyboardMarkup(buttons)
                
                await message.reply_photo(
                    photo=PREMIUM_IMG if 'PREMIUM_IMG' in globals() else "https://i.ibb.co/gMrpRQWP/photo-2025-07-09-05-21-32-7524948058832896004.jpg",
                    caption=caption,
                    reply_markup=reply_markup
                )
            else:
                # Premium expired
                await show_expired_premium(client, message, user)
        else:
            # No premium plan
            await show_no_premium(client, message, user)
            
    except Exception as e:
        logger.error(f"Error in myplan command: {e}")
        await message.reply_text("❌ **Error getting plan information.** Please try again later.")

async def show_expired_premium(client, message, user):
    """Show expired premium message"""
    caption = (
        f"💔 **Hey {user}**\n\n"
        f"❌ **Your premium plan has expired!**\n\n"
        f"🔒 **Current Status:** Free User\n"
        f"📚 **Access:** Limited study materials\n\n"
        f"💎 **Renew your premium plan to enjoy:**\n"
        f"• Unlimited access to all content\n"
        f"• Priority support\n"
        f"• Advanced features\n"
        f"• Ad-free experience"
    )
    
    buttons = [
        [InlineKeyboardButton("💎 Checkout Premium Plans", callback_data='premium_info')],
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_photo(
        photo="https://i.ibb.co/gMrpRQWP/photo-2025-07-09-05-21-32-7524948058832896004.jpg",
        caption=caption,
        reply_markup=reply_markup
    )

async def show_no_premium(client, message, user):
    """Show no premium plan message"""
    caption = (
        f"💎 **Hey {user}**\n\n"
        f"❌ **You don't have an active premium plan.**\n\n"
        f"🔒 **Current Status:** Free User\n"
        f"📚 **Access:** Limited study materials\n\n"
        f"💎 **Upgrade to premium to enjoy:**\n"
        f"• Unlimited access to all content\n"
        f"• Priority support\n"
        f"• Advanced features\n"
        f"• Ad-free experience\n"
        f"• Study progress tracking\n"
        f"• Personalized recommendations"
    )
    
    buttons = [
        [InlineKeyboardButton("💎 Checkout Premium Plans", callback_data='premium_info')],
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_photo(
        photo="https://i.ibb.co/gMrpRQWP/photo-2025-07-09-05-21-32-7524948058832896004.jpg",
        caption=caption,
        reply_markup=reply_markup
    )

@Client.on_message(filters.command("get_premium") & filters.user(ADMINS))
async def get_premium(client, message):
    """Get premium user information (admin only)"""
    if len(message.command) == 2:
        try:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            user_data = await study_db.get_user(user_id)
            
            if user_data and user_data.get("premium_expiry"):
                expiry = user_data.get("premium_expiry")
                current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
                
                # Parse expiry date
                if isinstance(expiry, str):
                    expiry_dt = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                    expiry_dt = expiry_dt.astimezone(pytz.timezone("Asia/Kolkata"))
                else:
                    expiry_dt = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
                
                time_left = expiry_dt - current_time
                
                if time_left.total_seconds() > 0:
                    days = time_left.days
                    hours, remainder = divmod(time_left.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
                    
                    expiry_str = expiry_dt.strftime("%d-%m-%Y\n⏱️ Expiry time: %I:%M:%S %p")
                    
                    premium_info = (
                        f"⚜️ **Premium User Data**\n\n"
                        f"👤 **User:** {user.mention}\n"
                        f"⚡ **User ID:** `{user_id}`\n"
                        f"⏰ **Time Left:** {time_left_str}\n"
                        f"⌛️ **Expiry Date:** {expiry_str}\n"
                        f"💎 **Status:** Active Premium"
                    )
                    
                    await message.reply_text(premium_info)
                else:
                    await message.reply_text(f"❌ **Premium Expired**\n\nUser {user.mention} had premium access but it has expired.")
            else:
                await message.reply_text("❌ **No premium data found!**\n\nThis user doesn't have an active premium plan.")
                
        except ValueError:
            await message.reply_text("❌ **Invalid user ID!** Please provide a valid numeric user ID.")
        except Exception as e:
            logger.error(f"Error getting premium info: {e}")
            await message.reply_text(f"❌ **Error:** {e}")
    else:
        await message.reply_text("❌ **Usage:** `/get_premium <user_id>`")

@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def add_premium(client, message):
    """Add premium access to a user (admin only)"""
    if len(message.command) < 3:
        await message.reply_text(
            "❌ **Usage:** `/add_premium <user_id> <days>`\n\n"
            "**Example:** `/add_premium 123456789 30` - Add 30 days premium"
        )
        return
    
    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
        
        if days <= 0:
            await message.reply_text("❌ **Invalid duration!** Please provide a positive number of days.")
            return
        
        if days > 365:
            await message.reply_text("❌ **Invalid duration!** Maximum premium duration is 365 days.")
            return
        
        # Get user
        user = await client.get_users(user_id)
        
        # Calculate expiry date
        current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        expiry_time = current_time + timedelta(days=days)
        
        # Update user in database
        await study_db.update_user(user_id, {
            'premium_expiry': expiry_time.isoformat(),
            'premium_plan': 'standard',
            'premium_added_by': message.from_user.id,
            'premium_added_at': current_time.isoformat()
        })
        
        # Send confirmation
        await message.reply_text(
            f"✅ **Premium Access Added Successfully!**\n\n"
            f"👤 **User:** {user.mention}\n"
            f"⚡ **User ID:** `{user_id}`\n"
            f"⏰ **Duration:** {days} days\n"
            f"📅 **Expires:** {expiry_time.strftime('%d-%m-%Y %I:%M:%S %p')}\n"
            f"👮 **Added by:** {message.from_user.mention}"
        )
        
        # Notify the user
        try:
            notification = (
                f"🎉 **Congratulations!**\n\n"
                f"💎 **Premium Access Activated!**\n\n"
                f"⏰ **Duration:** {days} days\n"
                f"📅 **Expires:** {expiry_time.strftime('%d-%m-%Y %I:%M:%S %p')}\n\n"
                f"🎯 **Premium Benefits:**\n"
                f"• Unlimited study materials\n"
                f"• Priority support\n"
                f"• Advanced features\n"
                f"• Ad-free experience\n\n"
                f"🚀 **Start exploring premium features now!**"
            )
            
            await client.send_message(user_id, notification)
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
        
        logger.info(f"Premium access added to user {user_id} for {days} days by {message.from_user.id}")
        
    except ValueError:
        await message.reply_text("❌ **Invalid input!** Please provide valid user ID and number of days.")
    except Exception as e:
        logger.error(f"Error adding premium access: {e}")
        await message.reply_text(f"❌ **Error:** {e}")

@Client.on_message(filters.command("premium_users"))
async def premium_users(client, message):
    """List all premium users (admin only)"""
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ **Access denied!** This command is only for admins.")
        return
    
    try:
        # Get premium users from database
        premium_users = await study_db.get_premium_users()
        
        if not premium_users:
            await message.reply_text("✅ **No premium users found.**")
            return
        
        users_text = f"💎 **Premium Users List**\n\n"
        users_text += f"📊 **Total Premium Users:** {len(premium_users)}\n\n"
        
        for i, user in enumerate(premium_users[:20], 1):  # Show first 20
            user_id = user.get('user_id', 'Unknown')
            expiry = user.get('premium_expiry', 'Unknown')
            plan = user.get('premium_plan', 'standard')
            
            # Calculate time left
            try:
                if isinstance(expiry, str):
                    expiry_dt = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                    current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
                    time_left = expiry_dt - current_time
                    
                    if time_left.total_seconds() > 0:
                        days = time_left.days
                        hours, remainder = divmod(time_left.seconds, 3600)
                        time_left_str = f"{days}d {hours}h"
                    else:
                        time_left_str = "Expired"
                else:
                    time_left_str = "Unknown"
            except:
                time_left_str = "Unknown"
            
            users_text += f"{i}. **User ID:** `{user_id}`\n"
            users_text += f"   💎 **Plan:** {plan.title()}\n"
            users_text += f"   ⏰ **Time Left:** {time_left_str}\n\n"
        
        if len(premium_users) > 20:
            users_text += f"... and {len(premium_users) - 20} more users."
        
        buttons = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_premium_users")],
            [InlineKeyboardButton("📊 Export", callback_data="export_premium_users")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(users_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting premium users: {e}")
        await message.reply_text(f"❌ **Error getting premium users:** {e}")

@Client.on_callback_query(filters.regex(r"^premium_info$"))
async def premium_info_callback(client, callback_query):
    """Handle premium info callback"""
    await callback_query.answer("💎 Premium plans coming soon!")
    
    info_text = (
        "💎 **Premium Plans**\n\n"
        "🚀 **Coming Soon!**\n\n"
        "We're working on amazing premium features:\n"
        "• Unlimited study materials\n"
        "• Priority support\n"
        "• Advanced progress tracking\n"
        "• Personalized recommendations\n"
        "• Ad-free experience\n"
        "• Early access to new features\n\n"
        "📞 **Contact support for early access!**"
    )
    
    buttons = [
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_plan")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(info_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^premium_stats$"))
async def premium_stats_callback(client, callback_query):
    """Handle premium stats callback"""
    user_id = callback_query.from_user.id
    
    try:
        user_data = await study_db.get_user(user_id)
        
        if user_data and user_data.get("premium_expiry"):
            expiry = user_data.get("premium_expiry")
            
            if isinstance(expiry, str):
                expiry_dt = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
                time_left = expiry_dt - current_time
                
                if time_left.total_seconds() > 0:
                    days = time_left.days
                    hours, remainder = divmod(time_left.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
                    
                    stats_text = (
                        f"📊 **Premium Usage Statistics**\n\n"
                        f"⏰ **Time Remaining:** {time_left_str}\n"
                        f"📅 **Expires:** {expiry_dt.strftime('%d-%m-%Y %I:%M:%S %p')}\n"
                        f"💎 **Plan:** {user_data.get('premium_plan', 'Standard').title()}\n\n"
                        f"🎯 **Usage Benefits:**\n"
                        f"• Unlimited content access\n"
                        f"• Priority support\n"
                        f"• Advanced features\n"
                        f"• Ad-free experience"
                    )
                else:
                    stats_text = "❌ **Premium has expired!** Renew to continue enjoying premium benefits."
            else:
                stats_text = "❌ **Invalid premium data.** Please contact support."
        else:
            stats_text = "❌ **No premium plan found.** Upgrade to premium to see usage statistics."
        
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_plan")],
            [InlineKeyboardButton("💎 Upgrade", callback_data="premium_info")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await callback_query.message.edit_text(stats_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting premium stats: {e}")
        await callback_query.answer("❌ Error getting statistics!", show_alert=True)

@Client.on_callback_query(filters.regex(r"^back_to_plan$"))
async def back_to_plan_callback(client, callback_query):
    """Go back to plan information"""
    await myplan(client, callback_query.message)
