# -*- coding: utf-8 -*-

class script(object):
    LOGO = """
╔══════════════════════════════════════╗
║             📚 STUDY BOT 📚           ║
║                                      ║
║  🎯 Your Personal Learning Companion  ║
║  🚀 Advanced Dual Bot System         ║
║  💡 Smart Content Management         ║
║  🔍 Intelligent Search & Filter      ║
║  📊 Progress Tracking & Analytics     ║
║  🏆 Gamification & Achievements      ║
║                                      ║
║  ⚡ Powered by Pyrogram & MongoDB    ║
║  🌟 Built for Educational Excellence ║
╚══════════════════════════════════════╝
"""

    RESTART_TXT = """**Study Bot Restarted!**

🔄 **Bot:** {}
📅 **Date:** {}
⏰ **Time:** {}

✅ Bot is now online and ready to help with your studies!"""

    START_TXT = """👋 **Hello {}!**

🎯 **Welcome to Study Bot - Your Personal Learning Companion!**

🚀 **What I can do for you:**
• 📚 Access study materials by batch
• 🔍 Search for specific content
• 📖 Get lectures, DPP, and study materials
• 📊 Track your learning progress
• 🏆 Earn achievements and badges
• 💡 Get personalized study recommendations

📚 **Available Subjects:**
• 🧪 Physics
• ⚗️ Chemistry  
• 🧬 Biology

💡 **Start Learning:**
Use `/Anuj <batch_name>` to access your study materials!

🔗 **Bot:** @{}
📢 **Channel:** @{}

🎯 **Ready to start your learning journey?**"""

    HELP_TXT = """📚 **Study Bot Help**

🎯 **Main Commands:**
• `/start` - Start the bot
• `/help` - Show this help message
• `/Anuj <batch_name>` - Access study materials
• `/search <query>` - Search for content
• `/stats` - Show your progress
• `/route` - Navigation menu

📖 **Study Commands:**
• `/lectures` - Access video lectures
• `/dpp` - Get practice materials
• `/notes` - Download study notes
• `/materials` - All study materials

🔍 **Search Commands:**
• `/search <topic>` - Search by topic
• `/search <chapter>` - Search by chapter
• `/search <teacher>` - Search by teacher

⚙️ **Settings Commands:**
• `/settings` - Configure bot settings
• `/profile` - View your profile
• `/achievements` - View achievements

💡 **Need More Help?**
Contact admin: @your_admin_username

🎯 **Start Learning Now:**
Use `/Anuj NEET2026` to begin!"""

    ABOUT_TXT = """📚 **About Study Bot**

🎯 **Your Personal Learning Companion**

🚀 **Features:**
• 📚 Dual Bot System (Main + Content)
• 🔍 Smart Content Management
• 📊 Progress Tracking & Analytics
• 🏆 Gamification & Achievements
• 💡 Personalized Study Plans
• 🔐 Secure Content Access

📖 **Study Materials:**
• 🧪 Physics, Chemistry, Biology
• 📹 Video Lectures & DPPs
• 📝 Notes, Mind Maps, PYQs
• 🎯 NEET, JEE, CBSE Content

⚡ **Technology:**
• Built with Pyrogram
• MongoDB Database
• Asynchronous Architecture
• Mobile Optimized

👨‍💻 **Developer:** {}
🤖 **Bot:** {}
🔗 **Contact:** {}

🌟 **Empowering students to learn smarter!**"""

    STATS_TXT = """
📊 <b>Study Bot Statistics</b>

📈 <b>Overall Stats:</b>
• 📁 Total Files: {total_files}
• 👥 Total Users: {total_users}
• 📚 Total Batches: {total_batches}
• 🧪 Total Subjects: {total_subjects}

🎯 <b>Content Distribution:</b>
• 📹 Lectures: {lectures_count}
• 📝 DPPs: {dpp_count}
• 📚 Notes: {notes_count}
• 🧩 Quizzes: {quiz_count}

📊 <b>User Activity:</b>
• 🚀 Active Users (24h): {active_users_24h}
• 📱 Active Users (7d): {active_users_7d}
• ⏱️ Total Study Time: {total_study_time}
• 📥 Total Downloads: {total_downloads}

🏆 <b>Achievements:</b>
• 🎓 Study Masters: {study_masters}
• 📚 Subject Explorers: {subject_explorers}
• 🏅 Content Collectors: {content_collectors}

🕐 <b>System Info:</b>
• 🚀 Uptime: {uptime}
• 💾 Database Size: {db_size}
• 🔄 Last Update: {last_update}

🌟 <b>Study Bot is growing stronger every day!</b>
"""

    BATCH_INFO_TXT = """
📚 <b>Batch Information</b>

🎯 <b>Batch:</b> {batch_name}
📅 <b>Created:</b> {created_date}
👨‍🏫 <b>Teachers:</b> {teachers}
🧪 <b>Subjects:</b> {subjects}

📊 <b>Content Summary:</b>
• 📹 Total Lectures: {total_lectures}
• 📝 Total DPPs: {total_dpp}
• 📚 Total Notes: {total_notes}
• 🧩 Total Quizzes: {total_quizzes}

📈 <b>Student Progress:</b>
• 👥 Active Students: {active_students}
• 📖 Chapters Completed: {chapters_completed}
• ⏱️ Average Study Time: {avg_study_time}
• 🏆 Top Achievers: {top_achievers}

🎁 <b>Special Features:</b>
• 🎁 Surprise content available
• 📱 Mobile optimized interface
• 🔍 Smart search capabilities
• 📊 Progress tracking

💡 <b>Get Started:</b>
Use <code>/Anuj {batch_name}</code> to begin studying!

🌟 <b>Join this batch and start your learning journey!</b>
"""

    CONTENT_DELIVERY_TXT = """
📚 <b>Content Delivery</b>

🎯 <b>Request Details:</b>
• 📚 Batch: {batch_name}
• 🧪 Subject: {subject}
• 👨‍🏫 Teacher: {teacher}
• 📖 Chapter: {chapter_no}
• 📝 Content Type: {content_type}

📦 <b>Content Package:</b>
• 📄 Files Found: {files_count}
• 📏 Total Size: {total_size}
• 🕐 Delivery Time: {delivery_time}

📋 <b>Files Included:</b>
{file_list}

💡 <b>Next Steps:</b>
• 📖 Review the materials
• 📝 Take notes
• 🧩 Practice with DPPs
• 📊 Track your progress

🎁 <b>Bonus:</b>
• 🎁 Surprise content included
• 📱 Mobile optimized files
• 🔍 Search within content
• 📊 Progress tracking

🌟 <b>Happy Studying!</b>
"""

    ERROR_TXT = """
❌ <b>Error Occurred</b>

🔍 <b>Error Details:</b>
• Type: {error_type}
• Message: {error_message}
• Time: {error_time}

💡 <b>Possible Solutions:</b>
• 🔄 Try again in a few moments
• 📱 Check your internet connection
• 🆘 Contact support if problem persists
• 📖 Use /help for command guidance

🆘 <b>Need Help?</b>
• Use <code>/help</code> command
• Contact bot admins
• Check bot status

🌟 <b>We're here to help you learn!</b>
"""

    SEARCH_RESULTS_TXT = """
🔍 <b>Search Results</b>

📝 <b>Query:</b> {query}
📊 <b>Results Found:</b> {results_count}

📋 <b>Results:</b>
{results_list}

💡 <b>Search Tips:</b>
• 🔍 Use specific keywords
• 📚 Include batch names
• 🧪 Specify subjects
• 📖 Add chapter numbers

🎯 <b>Refine Search:</b>
• Use <code>/search &lt;query&gt;</code> again
• Add more specific terms
• Check spelling

🌟 <b>Found what you're looking for?</b>
"""

    PROGRESS_TXT = """
📈 <b>Your Study Progress</b>

👤 <b>Student:</b> {user_name}
📚 <b>Current Batch:</b> {current_batch}
🏆 <b>Level:</b> {study_level}
⭐ <b>Score:</b> {study_score} points

📊 <b>Overall Statistics:</b>
• ⏱️ Total Study Time: {total_time}
• 📥 Total Downloads: {total_downloads}
• 🧪 Subjects Studied: {subjects_count}
• 📖 Chapters Completed: {chapters_count}

📈 <b>Subject Progress:</b>
{subject_progress}

🏅 <b>Achievements:</b>
{achievements_list}

🎯 <b>Next Goals:</b>
• 📚 Complete current chapter
• 🧪 Study new subjects
• 📝 Download more materials
• 🏆 Earn new achievements

🌟 <b>Keep up the great work!</b>
"""

    ACHIEVEMENT_TXT = """
🏆 <b>New Achievement Unlocked!</b>

🎉 <b>Congratulations!</b>
You've earned: <b>{achievement_name}</b>

📝 <b>Description:</b>
{achievement_description}

🎯 <b>Requirements Met:</b>
{requirements_met}

🏅 <b>Your Achievements:</b>
{total_achievements} total

💡 <b>Keep Learning:</b>
• 📚 Study more subjects
• 📝 Download materials
• ⏱️ Spend time learning
• 🎯 Complete chapters

🌟 <b>You're doing amazing!</b>
"""

    SURPRISE_TXT = """
🎁 <b>Surprise Content!</b>

🎉 <b>You've found a surprise!</b>

🎯 <b>Special Content:</b>
{surprise_content}

🎁 <b>Surprise Features:</b>
• 🎯 Exclusive materials
• 📚 Bonus content
• 🏆 Special achievements
• 💎 Premium features

💡 <b>How to Find More:</b>
• 🔍 Explore all menus
• 📱 Check every button
• 🎁 Look for surprise icons
• 🚀 Complete more content

🌟 <b>Keep exploring for more surprises!</b>
"""

    # Admin messages
    ADMIN_STATS_TXT = """
👑 <b>Admin Statistics</b>

📊 <b>System Overview:</b>
• 📁 Total Files: {total_files}
• 👥 Total Users: {total_users}
• 📚 Total Batches: {total_batches}
• 🧪 Total Subjects: {total_subjects}

📈 <b>Performance Metrics:</b>
• 🚀 Bot Uptime: {uptime}
• 💾 Database Size: {db_size}
• 📱 Active Sessions: {active_sessions}
• 🔄 Last Backup: {last_backup}

👥 <b>User Activity:</b>
• 🚀 New Users (24h): {new_users_24h}
• 📱 Active Users (7d): {active_users_7d}
• ⏱️ Total Study Time: {total_study_time}
• 📥 Total Downloads: {total_downloads}

🏆 <b>Content Analytics:</b>
• 📹 Most Popular: {most_popular}
• 📝 Most Downloaded: {most_downloaded}
• 🧪 Subject Distribution: {subject_distribution}
• 📊 Chapter Coverage: {chapter_coverage}

🛠️ <b>System Health:</b>
• ✅ Database: {db_status}
• ✅ File Storage: {storage_status}
• ✅ Bot API: {api_status}
• ✅ Content Delivery: {delivery_status}

🌟 <b>Study Bot is running smoothly!</b>
"""

    # Error messages
    ERRORS = {
        "no_batch": "❌ No batch name provided. Use: /Anuj &lt;batch_name&gt;",
        "batch_not_found": "❌ Batch '{batch_name}' not found. Use /addbatch to create it.",
        "no_content": "❌ No content found for this selection.",
        "invalid_input": "❌ Invalid input. Please check your request.",
        "rate_limit": "⏰ Rate limit exceeded. Please wait before trying again.",
        "permission_denied": "🚫 Permission denied. Admin access required.",
        "file_too_large": "📁 File too large. Maximum size: 2GB",
        "database_error": "💾 Database error. Please try again later.",
        "network_error": "🌐 Network error. Check your connection.",
        "bot_error": "🤖 Bot error. Please try again later."
    }

    # Success messages
    SUCCESS = {
        "batch_created": "✅ Batch '{batch_name}' created successfully!",
        "file_uploaded": "✅ File uploaded successfully!",
        "content_sent": "✅ Content sent to your PM!",
        "progress_updated": "✅ Progress updated successfully!",
        "achievement_unlocked": "🏆 Achievement unlocked: {achievement_name}!",
        "search_completed": "🔍 Search completed successfully!",
        "settings_updated": "⚙️ Settings updated successfully!",
        "backup_created": "💾 Backup created successfully!"
    }

    # Info messages
    INFO = {
        "processing": "⏳ Processing your request...",
        "searching": "🔍 Searching for content...",
        "uploading": "📤 Uploading file...",
        "downloading": "📥 Downloading content...",
        "analyzing": "📊 Analyzing data...",
        "connecting": "🔗 Connecting to database...",
        "validating": "✅ Validating input...",
        "preparing": "📋 Preparing content..."
    }

    # Warning messages
    WARNINGS = {
        "cache_expired": "⚠️ Cache expired, refreshing data...",
        "rate_limit_warning": "⚠️ Approaching rate limit. Slow down.",
        "storage_warning": "⚠️ Storage space running low.",
        "backup_warning": "⚠️ Backup overdue. Please create backup.",
        "update_available": "⚠️ Bot update available.",
        "maintenance_mode": "⚠️ Bot in maintenance mode."
    }

    # Welcome message template
    MELCOW_ENG = """<b>👋 Hey {},

🍁 Welcome to
🌟 {} 

🔍 Here you can search for your study materials by just typing the subject or chapter name 🔎

⚠️ If you're having any problem regarding accessing content or need help, feel free to contact support.

🎯 Start your learning journey now!</b>"""

    # Status message template
    STATUS_TXT = """�� **Study Bot Status**

👥 **Users:** {}
🏘️ **Groups:** {}
⭐ **Premium:** {}
📁 **Files:** {}
💾 **Database:** {}
💿 **Free Space:** {}
⏱️ **Uptime:** {}
🖥️ **RAM:** {}
⚡ **CPU:** {}"""

    # Multi-database status message template
    MULTI_STATUS_TXT = """📊 **Study Bot Status (Multi-DB)**

👥 **Users:** {}
🏘️ **Groups:** {}
⭐ **Premium:** {}
📁 **Files:** {}
💾 **Database:** {}
💿 **Free Space:** {}
⏱️ **Uptime:** {}
🖥️ **RAM:** {}
⚡ **CPU:** {}

📊 **Secondary Database:**
📁 **Files:** {}
💾 **Database:** {}
💿 **Free Space:** {}

📈 **Total Files:** {}"""

    # Group commands help
    GROUP_CMD = """📚 **Study Bot Group Commands**

👥 **For Group Members:**
• `/Anuj <batch_name>` - Access study materials
• `/search <query>` - Search for content
• `/help` - Show help menu
• `/stats` - Show your progress

👮 **For Group Admins:**
• `/settings` - Configure bot settings
• `/broadcast` - Send message to all users
• `/stats` - Show group statistics

💡 **Note:** Some commands may require admin privileges."""

    # Admin commands help
    ADMIN_CMD = """🔐 **Study Bot Admin Commands**

👮 **User Management:**
• `/ban <user_id> [reason]` - Ban a user
• `/unban <user_id>` - Unban a user
• `/banlist` - List banned users
• `/baninfo <user_id>` - Get ban information

📢 **Broadcasting:**
• `/broadcast <message>` - Send to all users
• `/broadcast` - Interactive broadcast menu

🏘️ **Group Management:**
• `/leave <chat_id>` - Leave a group
• `/disable <chat_id> [reason]` - Disable a group
• `/enable <chat_id>` - Enable a group

📊 **Statistics:**
• `/stats` - Show bot statistics
• `/channel` - Channel management

💡 **Note:** These commands are only for bot admins."""

    # Premium end message
    PREMIUM_END_TEXT = """⭐ **Premium Subscription Ended**

👤 **User:** {}

❌ Your premium subscription has expired.

💡 **To continue enjoying premium features:**
• Contact admin to renew
• Upgrade to premium plan
• Enjoy exclusive study materials

🎯 **Premium Features:**
• Priority content access
• Advanced search filters
• Download history
• Custom study plans
• Priority support

🔗 **Contact:** @your_admin_username"""

    # Premium broadcast message
    BPREMIUM_TXT = """⭐ **Premium Subscription Available**

🎯 **Upgrade to Premium for Enhanced Learning Experience!**

🚀 **Premium Features:**
• Priority content access
• Advanced search filters
• Download history
• Custom study plans
• Priority support
• Exclusive study materials
• No ads or limitations

💎 **Premium Plans:**
• Monthly: $5/month
• Quarterly: $12/3 months
• Yearly: $40/year

🔗 **Contact admin to subscribe:**
@your_admin_username

💡 **Why Premium?**
Get the most out of your study sessions with exclusive features and priority access to all content."""

# Default file caption
CAPTION = """📚 **Study Material**

📖 **File:** {file_name}
📏 **Size:** {file_size}
📁 **Type:** {file_type}

🎯 **Content:** {content_type}
📚 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}

💡 **Download and start studying!**

🔗 **Bot:** @{bot_username}
📢 **Channel:** @{channel_username}"""

# IMDB template (for compatibility)
IMDB_TEMPLATE_TXT = """📚 **Study Material Details**

📖 **File Name:** {file_name}
📏 **File Size:** {file_size}
📁 **File Type:** {file_type}

🎯 **Content Type:** {content_type}
📚 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}

💡 **Description:** {caption}

🔗 **Download Link:** {file_link}
📱 **Bot:** @{bot_username}"""

# Source code message
SOURCE_TXT = """📚 **Study Bot Source Code**

🔗 **GitHub Repository:**
https://github.com/yourusername/StudyBot

💻 **Technology Stack:**
• Python 3.8+
• Pyrogram (Telegram MTProto API)
• MongoDB (Database)
• Motor (Async MongoDB Driver)
• Umongo (ODM)

🚀 **Features Implemented:**
• Dual Bot System
• Content Management
• User Progress Tracking
• Admin Panel
• Broadcasting System
• File Indexing
• Search & Filter

📖 **Documentation:**
• Setup Guide: README.md
• Deployment: DEPLOYMENT.md
• Features: FEATURES_COMPLETE.md

🌟 **Contributions Welcome!**
Feel free to contribute to make Study Bot even better!"""

# Log message templates
LOG_TEXT_G = """#NewGroup
Group: {}
Group ID: {}
Members: {}
Added by: {}"""
