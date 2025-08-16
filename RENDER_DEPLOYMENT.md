# 🚀 Study Bot Render Deployment Guide

This guide will help you deploy the Study Bot on Render.com.

## 🎯 Prerequisites

- [Render account](https://render.com)
- [GitHub repository](https://github.com) with your Study Bot code
- [MongoDB Atlas](https://www.mongodb.com/atlas) account (or other MongoDB provider)
- [Telegram Bot Token](https://t.me/BotFather)
- [Telegram API credentials](https://my.telegram.org/apps)

## 🚀 Quick Deployment

### 1. Fork/Clone the Repository

```bash
git clone https://github.com/yourusername/study-bot.git
cd study-bot
```

### 2. Push to GitHub

```bash
git add .
git commit -m "Initial commit for Render deployment"
git push origin main
```

### 3. Deploy on Render

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**

#### Basic Settings
- **Name**: `study-bot` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Build Command**: `pip install -r requirements-docker.txt`
- **Start Command**: `python start.py`

#### Environment Variables
Add these environment variables in the Render dashboard:

```env
# Bot Configuration
SESSION=StudyBot_Session
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
CONTENT_BOT_TOKEN=your_content_bot_token_here

# Database
DATABASE_URI=mongodb+srv://username:password@cluster.mongodb.net/studybot_db?retryWrites=true&w=majority
DATABASE_NAME=studybot_db

# Channels
ADMINS=your_admin_id_here
CHANNELS=your_channel_id_here
LOG_CHANNEL=your_log_channel_id_here

# Study Content Channels
STUDY_CONTENT_CHANNELS=your_study_channel_ids_here
PHYSICS_CHANNEL=your_physics_channel_id_here
CHEMISTRY_CHANNEL=your_chemistry_channel_id_here
BIOLOGY_CHANNEL=your_biology_channel_id_here

# Bot Usernames
BOT_USERNAME=your_bot_username_here
CONTENT_BOT_USERNAME=your_content_bot_username_here

# Channel Links
MAIN_CHANNEL=https://t.me/your_channel
SUPPORT_GROUP=https://t.me/your_support_group
OWNER_LNK=https://t.me/your_username

# Other Settings
CACHE_TIME=300
PM_ON=True
PM_FILTER=True
AUTO_SUGGESTION=True
GAMIFICATION=True
MULTI_LANGUAGE=False
```

### 4. Deploy

Click **"Create Web Service"** and wait for the build to complete.

## 🔧 Advanced Configuration

### Environment Variables Reference

Use `env_deployment.txt` as a complete reference for all available environment variables.

### Custom Domain

1. **Go to your service settings**
2. **Click "Custom Domains"**
3. **Add your domain**
4. **Configure DNS records as instructed**

### Environment-Specific Deployments

Create different environments for testing and production:

```bash
# Development
git checkout -b develop
# Make changes
git push origin develop

# Production
git checkout main
git merge develop
git push origin main
```

## 📊 Monitoring and Logs

### View Logs

1. **Go to your service dashboard**
2. **Click "Logs" tab**
3. **Monitor real-time logs**

### Health Checks

The bot includes health checks that Render can monitor:

```python
# Health check endpoint (if web server is enabled)
@app.get('/health')
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Build Fails
```bash
# Check build logs
# Ensure requirements-docker.txt exists
# Verify Python version compatibility
```

#### 2. Bot Won't Start
```bash
# Check environment variables
# Verify MongoDB connection
# Check bot token validity
```

#### 3. Database Connection Issues
```bash
# Verify DATABASE_URI format
# Check MongoDB network access
# Verify credentials
```

### Debug Commands

```bash
# Check service status
curl https://your-service.onrender.com/health

# View recent logs
# Use Render dashboard logs tab
```

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit `.env` files
- Use Render's environment variable system
- Rotate API keys regularly

### 2. Database Security
- Use MongoDB Atlas with IP whitelisting
- Strong passwords and authentication
- Regular backups

### 3. Bot Security
- Keep bot tokens private
- Monitor bot usage
- Implement rate limiting

## 📈 Scaling

### Auto-Scaling

Render automatically scales based on traffic:
- **Free tier**: 1 instance
- **Paid tiers**: Multiple instances with load balancing

### Performance Optimization

1. **Enable Redis caching** (if needed)
2. **Optimize database queries**
3. **Use CDN for static assets**

## 💰 Cost Optimization

### Free Tier
- 750 hours/month
- 512 MB RAM
- Shared CPU

### Paid Tiers
- $7/month for dedicated resources
- Better performance and reliability
- Custom domains

## 🆘 Support

### Render Support
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Render Status](https://status.render.com)

### Study Bot Support
- Check the main README.md
- Review logs for errors
- Open issues in the repository

## 🎉 Success!

Once deployed, your Study Bot will be available at:
`https://your-service-name.onrender.com`

The bot will automatically start and connect to Telegram!

---

**Happy Deploying! 🚀**
