# 📚 Study Bot - Your Ultimate Study Companion

A powerful Telegram bot designed to provide students with easy access to comprehensive study materials, organized by subjects, chapters, and content types.

## 🌟 Features

### 🎯 Core Study Features
- **Batch-based Learning**: Organize content by study batches (NEET2026, JEE2025, etc.)
- **Subject Organization**: Physics, Chemistry, and Biology with dedicated content
- **Chapter Navigation**: Easy chapter selection by number or name
- **Content Types**: Lectures, DPPs, Notes, and comprehensive study materials
- **Teacher Selection**: Choose from available teachers for each subject

### 🚀 Advanced Features
- **Auto Suggestion**: Smart content recommendations
- **Gamification**: Achievement system and progress tracking
- **Full-Text Search**: Find content quickly with intelligent search
- **Hybrid Storage**: Optimized file storage and delivery
- **Multi-language Support**: Ready for international students

### 📱 User Experience
- **Intuitive Interface**: Easy-to-use button-based navigation
- **PM Integration**: Seamless content delivery to private messages
- **Progress Tracking**: Monitor your learning journey
- **Achievement System**: Earn badges and rewards
- **Surprise Content**: Hidden gems throughout the interface

### 🛠️ Admin Features
- **Content Management**: Easy upload and organization
- **User Analytics**: Track student engagement and progress
- **Batch Management**: Create and manage study batches
- **Broadcast System**: Send updates to all users
- **Force Subscribe**: Channel subscription management

## 🏗️ Architecture

### 🔧 Technology Stack
- **Backend**: Python 3.8+
- **Telegram API**: Pyrogram
- **Database**: MongoDB with Motor (async)
- **Web Server**: aiohttp
- **Caching**: Redis (optional)
- **File Storage**: Telegram + Cloud Storage

### 📊 Database Collections
- **StudyFiles**: Main content storage
- **Batches**: Batch information and settings
- **Chapters**: Chapter metadata and statistics
- **Users**: User profiles and progress
- **StudySessions**: Learning session tracking
- **ContentAnalytics**: Usage analytics
- **BotSettings**: Configuration management

## 🚀 Quick Start

### 📋 Prerequisites
- Python 3.8 or higher
- MongoDB database
- Telegram Bot Token
- API ID and Hash from my.telegram.org

### ⚙️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/study-bot.git
cd study-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run setup script (Recommended)**
```bash
python setup.py
```

4. **Or configure manually**
```bash
cp env_template.txt .env
# Edit .env with your configuration
```

5. **Test your setup**
```bash
python test_setup.py
```

6. **Run the bot**
```bash
python start.py
```

### 🔑 Configuration

Create a `.env` file with the following variables:

```env
# Bot Information
SESSION=StudyBot_Session
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_main_bot_token_here
CONTENT_BOT_TOKEN=your_content_bot_token_here

# Database
DATABASE_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=StudyBotDB

# Channels and Admins
ADMINS=123456789,987654321
LOG_CHANNEL=-1001234567890
CHANNELS=-1001234567890
```

## 📖 Usage Guide

### 🎯 For Students

1. **Start the bot**: Send `/start` to begin
2. **Select batch**: Use `/Anuj <batch_name>` (e.g., `/Anuj NEET2026`)
3. **Choose subject**: Physics, Chemistry, or Biology
4. **Select teacher**: Mr Sir or Saleem Sir
5. **Pick chapter**: By number (CH01, CH02) or name
6. **Choose content**: Lectures, DPPs, or All Materials
7. **Receive content**: Files sent to your PM automatically

### 🛠️ For Admins

1. **Add batches**: `/addbatch <batch_name>`
2. **View statistics**: `/stats`
3. **Manage content**: Upload files to designated channels
4. **Monitor users**: Track engagement and progress
5. **Send broadcasts**: Update all users with new content

### 🔍 Search Commands

- **Search files**: `/search <query>`
- **Recent content**: `/recent`
- **User stats**: `/stats`
- **Study progress**: `/progress`
- **Available batches**: `/batch`

## 🎨 Customization

### 🎨 Themes and Branding
- Customize bot logo and welcome messages
- Modify button layouts and colors
- Add your institution's branding

### 📚 Content Organization
- Adjust subject categories
- Modify chapter structures
- Customize content types
- Add new study materials

### 🏆 Achievement System
- Define custom achievements
- Set progress milestones
- Create reward systems
- Track student accomplishments

## 🔒 Security Features

- **Rate Limiting**: Prevent abuse and spam
- **User Authentication**: Secure access control
- **Content Protection**: Prevent unauthorized sharing
- **Admin Controls**: Restricted administrative functions
- **Data Encryption**: Secure storage and transmission

## 📊 Monitoring and Analytics

### 📈 Performance Metrics
- User engagement statistics
- Content popularity analysis
- Learning progress tracking
- System performance monitoring

### 🔍 Usage Analytics
- Most accessed content
- Popular study patterns
- User behavior insights
- Content effectiveness metrics

## 🚀 Deployment

### 🌐 Heroku Deployment
1. Create Heroku app
2. Set environment variables
3. Deploy using Git
4. Enable dyno

### 🐳 Docker Deployment
```bash
docker build -t study-bot .
docker run -d --name study-bot study-bot
```

### 🖥️ VPS Deployment
1. Set up server environment
2. Install dependencies
3. Configure systemd service
4. Set up reverse proxy

## 🧪 Testing

### 🧪 Run Tests
```bash
pytest tests/
pytest tests/ -v --cov=.
```

### 🔍 Test Coverage
- Unit tests for core functions
- Integration tests for database
- API endpoint testing
- User interaction testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### 📝 Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions
- Include type hints
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### 📞 Contact Information
- **Bot Support**: @StudyBotSupport
- **Developer**: @YourUsername
- **Documentation**: [Wiki Link]
- **Issues**: [GitHub Issues]

### 🆘 Common Issues
- **Bot not responding**: Check token and API credentials
- **Database errors**: Verify MongoDB connection
- **File upload issues**: Check file size limits
- **Permission errors**: Verify admin status

### 🔧 Troubleshooting

#### Setup Issues
1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Configuration errors**: Use `python setup.py` to create .env file
3. **Import errors**: Ensure you're in the correct directory

#### Runtime Issues
1. **Bot won't start**: Check your .env configuration
2. **Database connection failed**: Verify MongoDB URI and credentials
3. **Plugin errors**: Check plugin files for syntax errors

#### Testing
- Run `python test_setup.py` to verify your setup
- Check logs for detailed error messages
- Ensure all required environment variables are set

## 🔮 Future Roadmap

### 🚀 Planned Features
- **AI-powered recommendations**
- **Advanced analytics dashboard**
- **Mobile app integration**
- **Video streaming capabilities**
- **Collaborative study groups**
- **Real-time tutoring sessions**

### 🎯 Long-term Goals
- **Multi-platform support**
- **Advanced ML features**
- **Global content distribution**
- **Educational partnerships**
- **Research integration**

## 🙏 Acknowledgments

- **Telegram Team**: For the excellent Bot API
- **Pyrogram**: For the powerful Python library
- **MongoDB**: For the robust database solution
- **Open Source Community**: For inspiration and support

## 📊 Statistics

- **Active Users**: 1000+
- **Total Content**: 10,000+ files
- **Subjects Covered**: 3
- **Chapters Available**: 50+
- **Uptime**: 99.9%

---

🌟 **Made with ❤️ for students worldwide**

📚 **Study Bot - Empowering Education Through Technology**
