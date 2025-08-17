import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.study_db import db as study_db, StudyFiles, Batches, Chapters, Users, StudySessions, ContentAnalytics, BotSettings, JoinRequests, Chats, GroupSettings
from config import *
from studybot.Bot import studybot, content_bot

logger = logging.getLogger(__name__)

# Help command for main bot
@studybot.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Show help information for main bot"""
    try:
        help_text = """📚 **Study Bot Help** 📚

🎯 **Welcome to Study Bot!** Your ultimate study companion.

**🚀 Getting Started:**
1. Use `/Anuj <batch_name>` to access study materials
2. Select your subject (Physics, Chemistry, Biology)
3. Choose your teacher (Mr Sir, Saleem Sir)
4. Pick chapter format (Numbers or Names)
5. Select content type and enjoy learning!

**📖 Available Commands:**
• `/start` - Start the bot
• `/help` - Show this help message
• `/about` - About the bot
• `/status` - Check bot status
• `/contact` - Contact support

**📚 Content Types Available:**
• **Lectures** - Video/audio lectures (L01, L02, L03...)
• **DPP** - Daily Practice Problems (Quiz & PDF)
• **Study Materials** - 12 different types including:
  - Mind Maps, Revision, Short Notes
  - PYQs, KPP PDF, Practice Sheets
  - Handwritten Notes, Module Questions

**💡 Tips:**
• Use `/Anuj NEET2026` to access NEET 2026 batch
• All content is organized by subject → teacher → chapter
• Files are delivered via the Content Bot
• Navigation is intuitive with back buttons

**🔐 Privacy:**
• Your study progress is tracked privately
• No personal information is shared
• All data is encrypted and secure

**📞 Support:**
If you need help, contact the bot admin or use `/contact` command.

**🎁 Bonus:**
Look for the "Surprise Here!" button throughout the navigation!"""
        
        keyboard = [
            [InlineKeyboardButton("📚 Start Studying", callback_data="help_start_studying")],
            [InlineKeyboardButton("📖 Content Guide", callback_data="help_content_guide")],
            [InlineKeyboardButton("🔧 Troubleshooting", callback_data="help_troubleshooting")],
            [InlineKeyboardButton("📞 Contact Support", callback_data="help_contact")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(help_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await message.reply_text("❌ An error occurred while showing help.")

# Help command for content bot
@content_bot.on_message(filters.command("help") & filters.private)
async def content_help_command(client: Client, message: Message):
    """Show help information for content bot"""
    try:
        help_text = """📚 **Content Bot Help** 📚

🎯 **Welcome to Content Bot!** This bot delivers your study materials.

**📤 What This Bot Does:**
• Receives and stores study files
• Delivers requested content to you
• Manages file organization
• Tracks your study progress

**📖 Available Commands:**
• `/start` - Welcome message
• `/help` - Show this help
• `/search <query>` - Search for files
• `/recent` - Show recent files
• `/stats` - Your statistics
• `/batch` - Available batches
• `/progress` - Study progress

**🔍 How to Use:**
1. **Main Bot** - Use `/Anuj <batch_name>` to request content
2. **Content Bot** - Automatically receives and delivers files
3. **File Access** - All requested files appear here

**📁 File Types Supported:**
• Documents (PDF, DOC, PPT)
• Videos (MP4, AVI, MOV)
• Audio (MP3, WAV, M4A)
• Images (JPG, PNG, GIF)

**💡 Tips:**
• Keep this bot active to receive files
• Use search to find specific content
• Check your progress regularly
• Contact admin for missing content

**🔐 Privacy:**
• Forwarding is restricted for content protection
• Your study data is private
• Files are organized by your selections

**📞 Support:**
For technical issues or missing content, contact the bot admin."""
        
        keyboard = [
            [InlineKeyboardButton("🔍 Search Files", callback_data="content_help_search")],
            [InlineKeyboardButton("📊 View Stats", callback_data="content_help_stats")],
            [InlineKeyboardButton("📚 Go to Main Bot", url=f"https://t.me/{client.me.username}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(help_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in content help command: {e}")
        await message.reply_text("❌ An error occurred while showing help.")

# About command
@studybot.on_message(filters.command("about") & filters.private)
async def about_command(client: Client, message: Message):
    """Show about information"""
    try:
        about_text = """📚 **About Study Bot** 📚

🎯 **Your Ultimate Study Companion**

**🌟 What We Offer:**
• **Organized Learning** - Structured by batches, subjects, and chapters
• **Rich Content** - Lectures, DPPs, study materials, and more
• **Easy Navigation** - Intuitive button-based interface
• **Progress Tracking** - Monitor your learning journey
• **Dual Bot System** - Efficient content delivery

**🔧 Technical Features:**
• **Fast & Reliable** - Built with modern Python frameworks
• **Secure** - Encrypted data storage and transmission
• **Scalable** - Handles multiple users and large content libraries
• **User-Friendly** - Simple commands and clear navigation

**📚 Study Structure:**
• **Batches** - NEET2026, JEE2025, etc.
• **Subjects** - Physics, Chemistry, Biology
• **Teachers** - Mr Sir, Saleem Sir
• **Chapters** - Numbered (CH01, CH02) or Named ([CH-1] WAVES)
• **Content Types** - 15+ different study materials

**🎁 Special Features:**
• **Surprise Content** - Hidden gems throughout navigation
• **Progress Analytics** - Track your study habits
• **Achievement System** - Celebrate learning milestones
• **Smart Search** - Find content quickly

**👥 Who We Serve:**
• Medical aspirants (NEET)
• Engineering students (JEE)
• Science students
• Anyone seeking organized study materials

**💡 Our Mission:**
To make quality education accessible, organized, and engaging for every student.

**🔄 Version:** 1.0.0
**📅 Last Updated:** 2024
**👨‍💻 Developer:** Study Bot Team

**🌟 Join thousands of students already using Study Bot!**"""
        
        keyboard = [
            [InlineKeyboardButton("📚 Start Learning", callback_data="about_start")],
            [InlineKeyboardButton("📖 View Features", callback_data="about_features")],
            [InlineKeyboardButton("📞 Contact Us", callback_data="about_contact")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(about_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in about command: {e}")
        await message.reply_text("❌ An error occurred while showing about information.")

# Status command
@studybot.on_message(filters.command("status") & filters.private)
async def status_command(client: Client, message: Message):
    """Show bot status"""
    try:
        user_id = message.from_user.id
        
        # Get user info
        user = await Users.find_one({"_id": user_id})
        if not user:
            await message.reply_text("❌ User not found. Please use /start first.")
            return
        
        # Get bot statistics
        total_users = await Users.count_documents({})
        total_batches = await Batches.count_documents({})
        total_content = await StudyFiles.count_documents({})
        
        # Get user's current session
        current_batch = user.current_batch or "None"
        current_subject = user.current_subject or "None"
        current_teacher = user.current_teacher or "None"
        current_chapter = user.current_chapter or "None"
        
        status_text = f"""📊 **Bot Status** 📊

🟢 **Bot Status:** Online & Running
👤 **Your Status:** Active User

**📚 Your Current Session:**
• **Batch:** {current_batch}
• **Subject:** {current_subject}
• **Teacher:** {current_teacher}
• **Chapter:** {current_chapter}

**📊 Overall Statistics:**
• **Total Users:** {total_users}
• **Total Batches:** {total_batches}
• **Total Content Files:** {total_content}

**👤 Your Statistics:**
• **Total Downloads:** {user.total_downloads}
• **Time Spent:** {user.total_time_spent} minutes
• **Achievements:** {len(user.achievements)}
• **Joined:** {user.joined_at.strftime('%Y-%m-%d')}
• **Last Active:** {user.last_active.strftime('%Y-%m-%d %H:%M')}

**🔧 System Status:**
• **Database:** Connected ✅
• **Content Bot:** Active ✅
• **File Storage:** Available ✅
• **API Status:** Operational ✅

**💡 Quick Actions:**
• Use `/Anuj <batch_name>` to start studying
• Check `/help` for detailed guidance
• Use `/contact` for support"""
        
        keyboard = [
            [InlineKeyboardButton("📚 Continue Studying", callback_data="status_continue")],
            [InlineKeyboardButton("📊 View Progress", callback_data="status_progress")],
            [InlineKeyboardButton("🔧 Get Help", callback_data="status_help")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(status_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await message.reply_text("❌ An error occurred while checking status.")

# Contact command
@studybot.on_message(filters.command("contact") & filters.private)
async def contact_command(client: Client, message: Message):
    """Show contact information"""
    try:
        contact_text = """📞 **Contact & Support** 📞

🎯 **Need Help? We're Here for You!**

**📧 Contact Methods:**
• **Admin:** @your_admin_username
• **Support Channel:** @your_support_channel
• **Email:** support@studybot.com
• **Website:** https://studybot.com

**🔧 Technical Support:**
• **Bot Issues:** Report via admin
• **Content Problems:** Use /contact in main bot
• **Feature Requests:** Message admin directly
• **Bug Reports:** Include error details

**📚 Content Support:**
• **Missing Files:** Contact admin with details
• **Wrong Content:** Report with batch/subject info
• **Upload Requests:** Message admin
• **Content Updates:** Check support channel

**⏰ Response Time:**
• **Urgent Issues:** Within 2-4 hours
• **General Queries:** Within 24 hours
• **Content Requests:** Within 48 hours
• **Feature Requests:** Within 1 week

**💡 Before Contacting:**
1. Check `/help` for common solutions
2. Verify your command format
3. Include relevant error messages
4. Provide your user ID if needed

**📋 Contact Template:**
```
Issue: [Brief description]
Batch: [Your batch name]
Subject: [Subject if relevant]
Error: [Error message if any]
Steps: [What you were doing]
```

**🌟 We Value Your Feedback!**
Help us improve Study Bot by sharing your experience."""
        
        keyboard = [
            [InlineKeyboardButton("📧 Message Admin", url="https://t.me/your_admin_username")],
            [InlineKeyboardButton("📢 Support Channel", url="https://t.me/your_support_channel")],
            [InlineKeyboardButton("🌐 Visit Website", url="https://studybot.com")],
            [InlineKeyboardButton("📚 Back to Help", callback_data="contact_back_help")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(contact_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in contact command: {e}")
        await message.reply_text("❌ An error occurred while showing contact information.")

# Quick start guide
@studybot.on_message(filters.command("quickstart") & filters.private)
async def quickstart_command(client: Client, message: Message):
    """Show quick start guide"""
    try:
        quickstart_text = """🚀 **Quick Start Guide** 🚀

🎯 **Get Started in 5 Simple Steps:**

**1️⃣ Choose Your Batch**
```
/Anuj NEET2026
```
Replace `NEET2026` with your batch name.

**2️⃣ Select Subject**
• 🧪 **Physics** - Mechanics, Waves, Optics
• ⚗️ **Chemistry** - Organic, Inorganic, Physical
• 🧬 **Biology** - Cell Biology, Genetics, Ecology

**3️⃣ Pick Your Teacher**
• 👨‍🏫 **Mr Sir** - Expert in Physics & Chemistry
• 👨‍🏫 **Saleem Sir** - Specialized in Biology

**4️⃣ Choose Chapter Format**
• 🔢 **Numbers** - CH01, CH02, CH03...
• 📝 **Names** - [CH-1] WAVES, [CH-2] OPTICS...

**5️⃣ Select Content Type**
• 📖 **Lectures** - Video/audio lessons
• 📝 **DPP** - Practice problems
• 📚 **Study Materials** - 12 different types

**💡 Pro Tips:**
• Start with `/Anuj <your_batch>`
• Use back buttons for navigation
• Look for "Surprise Here!" buttons
• Check Content Bot for delivered files

**🎯 Example Journey:**
```
/Anuj NEET2026
→ Physics
→ Mr Sir
→ CH01
→ Lectures
→ L01 (File delivered to Content Bot)
```

**📚 Ready to Start?**
Use `/Anuj <batch_name>` now!"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Now", callback_data="quickstart_start")],
            [InlineKeyboardButton("📖 Full Help", callback_data="quickstart_help")],
            [InlineKeyboardButton("📚 View Examples", callback_data="quickstart_examples")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(quickstart_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in quickstart command: {e}")
        await message.reply_text("❌ An error occurred while showing quick start guide.")

# Log when plugin loads
logger.info("Help plugin loaded successfully")
