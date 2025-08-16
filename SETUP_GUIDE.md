# 🚀 Study Bot Setup Guide

## 📋 Prerequisites

Before setting up your Study Bot, you need:

1. **Telegram Account** - Your personal account
2. **Python 3.8+** - Installed on your system
3. **MongoDB Database** - Free tier available at [MongoDB Atlas](https://www.mongodb.com/atlas)
4. **Git** - For cloning the repository

## 🔑 Step 1: Get Bot Credentials

### 1.1 Get API ID & API Hash
1. Go to [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. Login with your phone number
3. Create a new application
4. Copy the **API ID** and **API Hash**

### 1.2 Get Bot Tokens
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create two bots:
   - **Main Bot** (for user interaction)
   - **Content Bot** (for file delivery)
3. Copy both bot tokens

### 1.3 Get Your User ID
1. Message [@userinfobot](https://t.me/userinfobot)
2. Copy your **User ID** (this will be your admin ID)

## 🗄️ Step 2: Setup MongoDB

### 2.1 Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create free account
3. Create a new cluster
4. Create database user
5. Get connection string

### 2.2 Connection String Format
```
mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
```

## ⚙️ Step 3: Configure Environment

### 3.1 Create .env File
1. Copy `env_template.txt` to `.env`
2. Fill in the required values:

```bash
# ⭐ MUST FILL - BOT CREDENTIALS ⭐
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
CONTENT_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# ⭐ MUST FILL - ADMIN & CHANNELS ⭐
ADMINS=123456789
CHANNELS=-1001234567890
LOG_CHANNEL=-1001234567890

# ⭐ MUST FILL - STUDY CONTENT CHANNELS ⭐
STUDY_CONTENT_CHANNELS=-1001234567890
PHYSICS_CHANNEL=-1001234567890
CHEMISTRY_CHANNEL=-1001234567890
BIOLOGY_CHANNEL=-1001234567890

# ⭐ MUST FILL - BOT INFORMATION ⭐
BOT_USERNAME=YourStudyBot
CONTENT_BOT_USERNAME=YourContentBot
MAIN_CHANNEL=https://t.me/your_channel
SUPPORT_GROUP=https://t.me/your_support_group
OWNER_LNK=https://t.me/your_username

# ⭐ MUST FILL - DATABASE ⭐
DATABASE_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
```

## 📱 Step 4: Setup Telegram Channels

### 4.1 Create Study Content Channels
1. Create private channels for each subject:
   - Physics Channel
   - Chemistry Channel
   - Biology Channel
2. Add your bots as admins
3. Get channel IDs using [@userinfobot](https://t.me/userinfobot)

### 4.2 Create Log Channel
1. Create a private channel for bot logs
2. Add your main bot as admin
3. Copy the channel ID

### 4.3 Create Support Group
1. Create a group for user support
2. Add your bots as admins
3. Get the group link

## 🚀 Step 5: Install Dependencies

### 5.1 Install Python Packages
```bash
pip install -r requirements.txt
```

### 5.2 Install System Dependencies (if needed)
```bash
# For Windows
# No additional packages needed

# For Linux/Mac
sudo apt-get install python3-dev
```

## 🔧 Step 6: Test Configuration

### 6.1 Test Config File
```bash
python -c "import config; print('✅ Config loaded successfully!')"
```

### 6.2 Test Database Connection
```bash
python -c "from database.study_db import db; print('✅ Database connected!')"
```

## 🎯 Step 7: Run the Bot

### 7.1 Start Main Bot
```bash
python bot.py
```

### 7.2 Start Content Bot (in separate terminal)
```bash
python content_bot.py
```

### 7.3 Test Basic Commands
1. Send `/start` to your main bot
2. Send `/start` to your content bot
3. Test `/help` command

## 📚 Step 8: Upload Study Materials

### 8.1 Prepare Your Files
- Organize files by subject and chapter
- Use clear naming: `Physics_Chapter1_Lecture1.pdf`
- Upload to respective subject channels

### 8.2 Index Files
1. Use admin commands to index files
2. Set up auto-indexing if needed
3. Verify search functionality

## 🎨 Step 9: Customize Bot

### 9.1 Custom Messages
- Edit `Script.py` for custom text
- Update welcome messages
- Customize help text

### 9.2 Custom Images
- Replace default images with your own
- Update image URLs in config
- Test image display

## 🔒 Step 10: Security & Privacy

### 10.1 Secure Your .env File
```bash
# Never commit .env to git
echo ".env" >> .gitignore
```

### 10.2 Set Bot Privacy
1. Message [@BotFather](https://t.me/BotFather)
2. Use `/setprivacy` command
3. Set to **Disabled** for group use

## 🚨 Troubleshooting

### Common Issues

#### 1. Bot Not Starting
- Check API credentials
- Verify bot tokens
- Check Python version (3.8+)

#### 2. Database Connection Error
- Verify MongoDB URI
- Check network connectivity
- Verify database permissions

#### 3. Channel Access Error
- Ensure bots are admins
- Check channel privacy settings
- Verify channel IDs

#### 4. File Upload Issues
- Check file size limits
- Verify channel permissions
- Check bot admin rights

### Debug Mode
Enable debug logging in `logging.conf`:
```ini
[logger_root]
level=DEBUG
```

## 📞 Support

If you encounter issues:

1. **Check Logs** - Look for error messages
2. **Verify Config** - Ensure all required fields are filled
3. **Test Step by Step** - Don't skip configuration steps
4. **Check Permissions** - Ensure bots have proper access

## 🎉 Congratulations!

Your Study Bot is now ready to help students access study materials efficiently!

---

**Next Steps:**
- Upload study materials to channels
- Test all bot features
- Customize bot appearance
- Set up user management
- Configure premium features

**Remember:** Start with minimal configuration and add features gradually!
