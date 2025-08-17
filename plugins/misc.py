import logging
import asyncio
import random
import string
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import *
from database.study_db import db as study_db
from utils import temp, get_readable_time

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("id") & filters.private)
async def get_id_command(client, message):
    """Get user and chat ID"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    id_text = f"🆔 **ID Information**\n\n"
    id_text += f"👤 **Your ID:** `{user_id}`\n"
    id_text += f"💬 **Chat ID:** `{chat_id}`\n"
    id_text += f"📱 **Chat Type:** {message.chat.type.value}"
    
    if message.forward_from:
        id_text += f"\n🔄 **Forwarded from:** `{message.forward_from.id}`"
    
    if message.forward_from_chat:
        id_text += f"\n🏘️ **Forwarded from chat:** `{message.forward_from_chat.id}`"
    
    await message.reply_text(id_text)

@Client.on_message(filters.command("info") & filters.private)
async def get_info_command(client, message):
    """Get detailed user information"""
    user_id = message.from_user.id
    
    try:
        # Get user from database
        user = await study_db.get_user(user_id)
        
        if user:
            info_text = f"👤 **User Information**\n\n"
            info_text += f"🆔 **User ID:** `{user_id}`\n"
            info_text += f"📝 **Name:** {user.get('name', 'Unknown')}\n"
            info_text += f"📅 **Joined:** {get_readable_time(user.get('joined_at', 0))}\n"
            info_text += f"🔒 **Banned:** {'Yes' if user.get('banned', False) else 'No'}\n"
            info_text += f"📊 **Study Sessions:** {len(user.get('study_sessions', []))}\n"
            info_text += f"⏱️ **Total Study Time:** {get_readable_time(sum(session.get('duration', 0) for session in user.get('study_sessions', [])))}\n"
            info_text += f"🎯 **Current Streak:** {user.get('current_streak', 0)} days\n"
            info_text += f"🏆 **Achievements:** {len(user.get('achievements', []))}\n"
            info_text += f"💬 **PM Enabled:** {'Yes' if user.get('pm_enabled', True) else 'No'}"
            
            if user.get('banned', False):
                info_text += f"\n📝 **Ban Reason:** {user.get('ban_reason', 'No reason provided')}"
        else:
            info_text = f"👤 **User Information**\n\n"
            info_text += f"🆔 **User ID:** `{user_id}`\n"
            info_text += f"❌ **User not found in database**\n\n"
            info_text += f"💡 Use /start to register with the bot."
        
        await message.reply_text(info_text)
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        await message.reply_text(f"❌ Error getting user information: {e}")

@Client.on_message(filters.command("ping") & filters.private)
async def ping_command(client, message):
    """Check bot response time"""
    start_time = asyncio.get_event_loop().time()
    
    ping_msg = await message.reply_text("🏓 Pinging...")
    
    end_time = asyncio.get_event_loop().time()
    ping_time = (end_time - start_time) * 1000
    
    await ping_msg.edit_text(f"🏓 **Pong!**\n\n⏱️ **Response Time:** {ping_time:.2f}ms")

@Client.on_message(filters.command("random") & filters.private)
async def random_command(client, message):
    """Generate random number or string"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **Usage:** `/random <type> [range]`\n\n"
                "**Types:**\n"
                "• `number` - Random number\n"
                "• `string` - Random string\n"
                "• `choice` - Random choice from list\n\n"
                "**Examples:**\n"
                "• `/random number 1 100`\n"
                "• `/random string 10`\n"
                "• `/random choice apple,banana,orange`"
            )
            return
        
        random_type = message.command[1].lower()
        
        if random_type == "number":
            if len(message.command) < 4:
                await message.reply_text("❌ **Usage:** `/random number <min> <max>`")
                return
            
            try:
                min_val = int(message.command[2])
                max_val = int(message.command[3])
                
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                
                random_num = random.randint(min_val, max_val)
                await message.reply_text(f"🎲 **Random Number:** `{random_num}`\n\n📊 **Range:** {min_val} to {max_val}")
                
            except ValueError:
                await message.reply_text("❌ Invalid number range. Please provide valid integers.")
        
        elif random_type == "string":
            length = 10  # Default length
            if len(message.command) > 2:
                try:
                    length = int(message.command[2])
                    if length <= 0 or length > 100:
                        await message.reply_text("❌ String length must be between 1 and 100.")
                        return
                except ValueError:
                    await message.reply_text("❌ Invalid string length. Please provide a valid integer.")
                    return
            
            # Generate random string
            chars = string.ascii_letters + string.digits
            random_string = ''.join(random.choice(chars) for _ in range(length))
            
            await message.reply_text(f"🔤 **Random String:** `{random_string}`\n\n📏 **Length:** {length}")
        
        elif random_type == "choice":
            if len(message.command) < 3:
                await message.reply_text("❌ **Usage:** `/random choice <item1,item2,item3>`")
                return
            
            choices = message.command[2].split(',')
            if len(choices) < 2:
                await message.reply_text("❌ Please provide at least 2 choices separated by commas.")
                return
            
            # Clean choices
            choices = [choice.strip() for choice in choices if choice.strip()]
            
            if len(choices) < 2:
                await message.reply_text("❌ Please provide at least 2 valid choices.")
                return
            
            random_choice = random.choice(choices)
            await message.reply_text(f"🎯 **Random Choice:** `{random_choice}`\n\n📋 **Options:** {', '.join(choices)}")
        
        else:
            await message.reply_text("❌ Invalid random type. Use `number`, `string`, or `choice`.")
    
    except Exception as e:
        logger.error(f"Error in random command: {e}")
        await message.reply_text(f"❌ Error generating random value: {e}")

@Client.on_message(filters.command("quote") & filters.private)
async def quote_command(client, message):
    """Get random motivational quote"""
    quotes = [
        "🎯 **Success is not final, failure is not fatal: it is the courage to continue that counts.** - Winston Churchill",
        "🚀 **The only way to do great work is to love what you do.** - Steve Jobs",
        "💪 **Believe you can and you're halfway there.** - Theodore Roosevelt",
        "🌟 **The future belongs to those who believe in the beauty of their dreams.** - Eleanor Roosevelt",
        "📚 **Education is the most powerful weapon which you can use to change the world.** - Nelson Mandela",
        "🎓 **Learning is a treasure that will follow its owner everywhere.** - Chinese Proverb",
        "🔥 **The only limit to our realization of tomorrow is our doubts of today.** - Franklin D. Roosevelt",
        "🌈 **Don't watch the clock; do what it does. Keep going.** - Sam Levenson",
        "⚡ **The harder you work for something, the greater you'll feel when you achieve it.** - Unknown",
        "🎉 **Every expert was once a beginner.** - Robert T. Kiyosaki"
    ]
    
    random_quote = random.choice(quotes)
    await message.reply_text(f"💭 **Daily Motivation**\n\n{random_quote}")

@Client.on_message(filters.command("timer") & filters.private)
async def timer_command(client, message):
    """Set a timer"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "⏰ **Timer Command**\n\n"
                "**Usage:** `/timer <seconds>`\n\n"
                "**Examples:**\n"
                "• `/timer 60` - 1 minute timer\n"
                "• `/timer 300` - 5 minutes timer\n"
                "• `/timer 3600` - 1 hour timer"
            )
            return
        
        seconds = int(message.command[1])
        
        if seconds <= 0:
            await message.reply_text("❌ Timer duration must be positive.")
            return
        
        if seconds > 86400:  # 24 hours
            await message.reply_text("❌ Timer duration cannot exceed 24 hours.")
            return
        
        # Send timer start message
        timer_msg = await message.reply_text(f"⏰ **Timer Started!**\n\n⏱️ **Duration:** {get_readable_time(seconds)}")
        
        # Wait for timer
        await asyncio.sleep(seconds)
        
        # Send timer completion message
        await timer_msg.edit_text(f"🔔 **Timer Complete!**\n\n⏰ **Duration:** {get_readable_time(seconds)}\n\n🎉 Time's up!")
        
        # Send notification
        await message.reply_text("🔔 **Timer Complete!** ⏰")
        
    except ValueError:
        await message.reply_text("❌ Invalid timer duration. Please provide a valid number of seconds.")
    except Exception as e:
        logger.error(f"Error in timer command: {e}")
        await message.reply_text(f"❌ Error setting timer: {e}")

@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client, message):
    """Show user statistics"""
    user_id = message.from_user.id
    
    try:
        # Get user from database
        user = await study_db.get_user(user_id)
        
        if user:
            # Calculate statistics
            total_sessions = len(user.get('study_sessions', []))
            total_time = sum(session.get('duration', 0) for session in user.get('study_sessions', []))
            current_streak = user.get('current_streak', 0)
            achievements = len(user.get('achievements', []))
            
            # Calculate average session time
            avg_session_time = total_time / total_sessions if total_sessions > 0 else 0
            
            # Get recent activity
            recent_sessions = sorted(user.get('study_sessions', []), key=lambda x: x.get('timestamp', 0), reverse=True)[:5]
            
            stats_text = f"📊 **Your Study Statistics**\n\n"
            stats_text += f"📚 **Total Study Sessions:** {total_sessions}\n"
            stats_text += f"⏱️ **Total Study Time:** {get_readable_time(total_time)}\n"
            stats_text += f"📈 **Average Session:** {get_readable_time(avg_session_time)}\n"
            stats_text += f"🎯 **Current Streak:** {current_streak} days\n"
            stats_text += f"🏆 **Achievements:** {achievements}\n"
            stats_text += f"📅 **Member Since:** {get_readable_time(user.get('joined_at', 0))}"
            
            if recent_sessions:
                stats_text += f"\n\n📝 **Recent Activity:**\n"
                for i, session in enumerate(recent_sessions, 1):
                    session_time = get_readable_time(session.get('duration', 0))
                    session_date = get_readable_time(session.get('timestamp', 0))
                    stats_text += f"{i}. {session_time} - {session_date}\n"
            
            buttons = [
                [InlineKeyboardButton("📈 Detailed Stats", callback_data="detailed_stats")],
                [InlineKeyboardButton("🏆 Achievements", callback_data="achievements")],
                [InlineKeyboardButton("📊 Progress Chart", callback_data="progress_chart")]
            ]
            
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_text(stats_text, reply_markup=reply_markup)
            
        else:
            await message.reply_text(
                "📊 **Statistics**\n\n"
                "❌ No statistics available.\n\n"
                "💡 Use /start to begin your study journey!"
            )
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        await message.reply_text(f"❌ Error getting statistics: {e}")

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    """Show help information"""
    help_text = (
        "🤖 **Study Bot Help**\n\n"
        "**Basic Commands:**\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this help message\n"
        "• `/id` - Get your user ID\n"
        "• `/info` - Get your information\n"
        "• `/stats` - Show your statistics\n\n"
        "**Utility Commands:**\n"
        "• `/ping` - Check bot response time\n"
        "• `/random` - Generate random values\n"
        "• `/quote` - Get motivational quote\n"
        "• `/timer <seconds>` - Set a timer\n\n"
        "**Study Commands:**\n"
        "• `/Anuj <batch>` - Access study materials\n"
        "• `/search` - Search for content\n"
        "• `/progress` - Track your progress\n\n"
        "**Admin Commands:**\n"
        "• `/admin` - Admin panel\n"
        "• `/broadcast` - Send messages to users\n"
        "• `/ban` - Ban users\n"
        "• `/stats` - Bot statistics\n\n"
        "💡 **Need more help?** Contact support!"
    )
    
    buttons = [
        [InlineKeyboardButton("📚 Study Guide", callback_data="study_guide")],
        [InlineKeyboardButton("🔧 Admin Guide", callback_data="admin_guide")],
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(help_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^study_guide$"))
async def study_guide_callback(client, callback_query):
    """Show study guide"""
    guide_text = (
        "📚 **Study Bot Guide**\n\n"
        "**Getting Started:**\n"
        "1. Use `/Anuj <batch_name>` to access study materials\n"
        "2. Select your subject (Physics, Chemistry, Biology)\n"
        "3. Choose your teacher\n"
        "4. Select chapter format (Number or Name)\n"
        "5. Choose content type (Lectures, DPP, All Materials)\n\n"
        "**Content Types:**\n"
        "• **Lectures:** Video/audio lessons\n"
        "• **DPP:** Daily Practice Problems\n"
        "• **All Materials:** Complete study resources\n\n"
        "**Navigation:**\n"
        "• Use buttons to navigate through content\n"
        "• All content is delivered via the content bot\n"
        "• Track your progress with `/progress`\n\n"
        "💡 **Tip:** Use `/search` to quickly find specific content!"
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Back to Help", callback_data="back_to_help")],
        [InlineKeyboardButton("📖 Quick Start", callback_data="quick_start")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(guide_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^admin_guide$"))
async def admin_guide_callback(client, callback_query):
    """Show admin guide"""
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    guide_text = (
        "🔧 **Admin Guide**\n\n"
        "**User Management:**\n"
        "• `/ban <user_id> [reason]` - Ban a user\n"
        "• `/unban <user_id>` - Unban a user\n"
        "• `/banlist` - List banned users\n"
        "• `/baninfo <user_id>` - Get ban information\n\n"
        "**Content Management:**\n"
        "• `/addbatch <name>` - Add new batch\n"
        "• `/delbatch <name>` - Delete batch\n"
        "• `/addcontent <type> <content>` - Add content\n"
        "• `/delcontent <id>` - Delete content\n\n"
        "**Broadcasting:**\n"
        "• `/broadcast` - Send messages to users\n"
        "• `/testbroadcast` - Test broadcast system\n\n"
        "**Statistics:**\n"
        "• `/users` - User statistics\n"
        "• `/stats` - Bot statistics\n"
        "• `/joinrequests` - Join request management\n\n"
        "💡 **Tip:** Use `/admin` for the full admin panel!"
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Back to Help", callback_data="back_to_help")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(guide_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^back_to_help$"))
async def back_to_help_callback(client, callback_query):
    """Go back to help menu"""
    await help_command(client, callback_query.message)

@Client.on_callback_query(filters.regex(r"^contact_support$"))
async def contact_support_callback(client, callback_query):
    """Show contact support information"""
    support_text = (
        "📞 **Contact Support**\n\n"
        "**Need Help?**\n"
        "• Technical issues\n"
        "• Feature requests\n"
        "• Bug reports\n"
        "• General questions\n\n"
        "**Contact Methods:**\n"
        "• **Support Group:** @support_group\n"
        "• **Main Channel:** @main_channel\n"
        "• **Email:** support@studybot.com\n\n"
        "**Response Time:**\n"
        "• Usually within 24 hours\n"
        "• Emergency issues: ASAP\n\n"
        "💡 **Before contacting:** Check /help and /guide first!"
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Back to Help", callback_data="back_to_help")],
        [InlineKeyboardButton("📋 Report Issue", callback_data="report_issue")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(support_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"^report_issue$"))
async def report_issue_callback(client, callback_query):
    """Start issue reporting process"""
    await callback_query.message.edit_text(
        "🐛 **Report Issue**\n\n"
        "Please describe the issue you're experiencing:\n\n"
        "**Include:**\n"
        "• What you were trying to do\n"
        "• What happened instead\n"
        "• Steps to reproduce\n"
        "• Screenshots if possible\n\n"
        "Send your report now:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancel", callback_data="back_to_help")
        ]])
    )
    
    # Store report state
    temp.REPORT_ISSUE = {
        'user_id': callback_query.from_user.id,
        'active': True
    }

@Client.on_message(filters.private & filters.text & filters.create(lambda _, __, m: not m.command) & filters.create(lambda _, __, m: not m.text.startswith('/')))
async def handle_issue_report(client, message):
    """Handle issue report message"""
    if not hasattr(temp, 'REPORT_ISSUE') or not temp.REPORT_ISSUE.get('active'):
        return
    
    if message.from_user.id != temp.REPORT_ISSUE['user_id']:
        return
    
    issue_text = message.text
    
    try:
        # Send issue report to admins
        if LOG_CHANNEL:
            report_text = (
                f"🐛 **Issue Report**\n\n"
                f"👤 **User:** {message.from_user.mention} (`{message.from_user.id}`)\n"
                f"📝 **Issue:** {issue_text}\n"
                f"⏰ **Time:** {get_readable_time(int(asyncio.get_event_loop().time()))}"
            )
            
            await client.send_message(LOG_CHANNEL, report_text)
        
        # Confirm to user
        await message.reply_text(
            "✅ **Issue Report Submitted!**\n\n"
            "📝 **Your Report:**\n"
            f"{issue_text}\n\n"
            "🔍 Our team will review this and get back to you soon.\n"
            "📞 For urgent issues, contact support directly."
        )
        
        # Reset report state
        temp.REPORT_ISSUE['active'] = False
        
        logger.info(f"Issue report submitted by user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error submitting issue report: {e}")
        await message.reply_text(f"❌ Error submitting report: {e}")
        temp.REPORT_ISSUE['active'] = False
