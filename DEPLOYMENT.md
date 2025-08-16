# 🚀 Study Bot Deployment Guide

This guide covers various deployment options for the Study Bot, from local development to production deployment.

## 📋 Prerequisites

Before deploying, ensure you have:

- **Python 3.8+** installed
- **Git** for version control
- **Telegram Bot Tokens** (Main Bot + Content Bot)
- **MongoDB** database (local or cloud)
- **API Credentials** from Telegram

## 🏠 Local Development

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Study_Bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env_template.txt .env

# Edit .env file with your credentials
nano .env
```

**Required Environment Variables:**
```env
# Bot Information
SESSION=StudyBot_Session
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_main_bot_token_here
CONTENT_BOT_TOKEN=your_content_bot_token_here

# Database
DATABASE_URI=mongodb://localhost:27017/studybot
DATABASE_NAME=studybot

# Bot Settings
ENABLE_PM=true
ENABLE_GROUP=true
OWNER_ID=your_telegram_user_id
```

### 3. Database Setup

```bash
# Start MongoDB (if local)
mongod --dbpath /path/to/data

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:6.0
```

### 4. Run the Bot

```bash
# Start the bot
python start.py

# Or run web server separately
python web_server.py
```

## 🐳 Docker Deployment

### 1. Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f studybot

# Stop services
docker-compose down
```

### 2. Manual Docker Build

```bash
# Build image
docker build -t studybot .

# Run container
docker run -d \
  --name studybot \
  -p 8080:8080 \
  -e DATABASE_URI=mongodb://host.docker.internal:27017/studybot \
  -e BOT_TOKEN=your_token \
  studybot
```

### 3. Environment Variables for Docker

```bash
# Create .env file for docker-compose
DATABASE_URI=mongodb://studybot:password@mongodb:27017/studybot_db?authSource=admin
REDIS_URI=redis://redis:6379
BOT_TOKEN=your_bot_token
CONTENT_BOT_TOKEN=your_content_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
OWNER_ID=your_user_id
```

## ☁️ Cloud Deployment

### 1. Heroku Deployment

#### Setup Heroku CLI
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login
```

#### Deploy to Heroku
```bash
# Create Heroku app
heroku create your-studybot-app

# Set environment variables
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set CONTENT_BOT_TOKEN=your_content_bot_token
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set OWNER_ID=your_user_id
heroku config:set DATABASE_URI=your_mongodb_uri

# Deploy
git push heroku main

# Scale dynos
heroku ps:scale worker=1
heroku ps:scale web=1
```

#### Heroku Environment Variables
```bash
# Required variables
BOT_TOKEN=your_main_bot_token
CONTENT_BOT_TOKEN=your_content_bot_token
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
OWNER_ID=your_telegram_user_id
DATABASE_URI=your_mongodb_connection_string

# Optional variables
ENABLE_PM=true
ENABLE_GROUP=true
MAX_FILE_SIZE=52428800
ON_HEROKU=true
```

### 2. Railway Deployment

#### Setup Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

#### Deploy to Railway
```bash
# Initialize Railway project
railway init

# Add environment variables
railway variables set BOT_TOKEN=your_bot_token
railway variables set CONTENT_BOT_TOKEN=your_content_bot_token
railway variables set API_ID=your_api_id
railway variables set API_HASH=your_api_hash
railway variables set OWNER_ID=your_user_id
railway variables set DATABASE_URI=your_mongodb_uri

# Deploy
railway up
```

### 3. Render Deployment

#### Setup Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository

#### Render Configuration
```yaml
# render.yaml
services:
  - type: web
    name: studybot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python web_server.py
    envVars:
      - key: BOT_TOKEN
        value: your_bot_token
      - key: CONTENT_BOT_TOKEN
        value: your_content_bot_token
      - key: API_ID
        value: your_api_id
      - key: API_HASH
        value: your_api_hash
      - key: OWNER_ID
        value: your_user_id
      - key: DATABASE_URI
        value: your_mongodb_uri
```

## 🗄️ Database Setup

### 1. MongoDB Atlas (Cloud)

1. **Create Cluster**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Create free cluster
   - Choose provider and region

2. **Database Access**
   - Create database user
   - Set username and password
   - Grant appropriate permissions

3. **Network Access**
   - Add IP address (0.0.0.0/0 for all)
   - Or add specific IP addresses

4. **Connection String**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/studybot?retryWrites=true&w=majority
   ```

### 2. Local MongoDB

```bash
# Install MongoDB
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Start MongoDB service
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 3. MongoDB with Docker

```bash
# Run MongoDB container
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:6.0

# Connection string
mongodb://admin:password@localhost:27017/studybot?authSource=admin
```

## 🔧 Production Configuration

### 1. Security Settings

```env
# Production security
ENABLE_PM=true
ENABLE_GROUP=false
MAX_FILE_SIZE=52428800
MAINTENANCE_MODE=false

# Database security
DATABASE_URI=mongodb+srv://user:pass@cluster.mongodb.net/studybot?retryWrites=true&w=majority
REDIS_URI=redis://localhost:6379

# Bot security
OWNER_ID=your_user_id
ADMIN_IDS=user1_id,user2_id
```

### 2. Monitoring and Logging

```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG

# Monitor with Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# View logs
docker-compose logs -f studybot
```

### 3. Backup and Recovery

```bash
# Database backup
mongodump --uri="mongodb://user:pass@cluster.mongodb.net/studybot" --out=./backup

# Database restore
mongorestore --uri="mongodb://user:pass@cluster.mongodb.net/studybot" --drop ./backup/studybot

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --uri="$DATABASE_URI" --out="./backups/backup_$DATE"
```

## 🚨 Troubleshooting

### Common Issues

1. **Bot Not Starting**
   ```bash
   # Check logs
   docker-compose logs studybot
   
   # Verify environment variables
   heroku config
   
   # Test database connection
   python -c "from database.study_db import init_db; import asyncio; asyncio.run(init_db())"
   ```

2. **Database Connection Issues**
   ```bash
   # Test MongoDB connection
   mongosh "mongodb://user:pass@cluster.mongodb.net/studybot"
   
   # Check network access
   # Ensure IP is whitelisted in MongoDB Atlas
   ```

3. **File Upload Issues**
   ```bash
   # Check file size limits
   # Verify bot permissions
   # Check storage space
   ```

### Performance Optimization

1. **Database Indexing**
   ```javascript
   // Create indexes for better performance
   db.studyfiles.createIndex({"batch_name": 1, "subject": 1, "teacher": 1})
   db.users.createIndex({"user_id": 1})
   db.batches.createIndex({"batch_name": 1})
   ```

2. **Caching**
   ```python
   # Enable Redis caching
   REDIS_URI=redis://localhost:6379
   CACHE_ENABLED=true
   CACHE_TTL=3600
   ```

3. **Load Balancing**
   ```yaml
   # Scale multiple instances
   heroku ps:scale worker=2
   heroku ps:scale web=2
   ```

## 📊 Health Checks

### Endpoints

- **Health Check:** `GET /health`
- **Status:** `GET /status`
- **Statistics:** `GET /stats`
- **Home Page:** `GET /`

### Monitoring

```bash
# Check bot health
curl https://your-app.herokuapp.com/health

# Monitor with uptimerobot
# Set up monitoring at https://uptimerobot.com
```

## 🔄 Updates and Maintenance

### 1. Update Bot

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart services
docker-compose restart studybot
# or
heroku restart
```

### 2. Database Migrations

```python
# Run database migrations
python -c "from database.study_db import migrate_database; import asyncio; asyncio.run(migrate_database())"
```

### 3. Backup Before Updates

```bash
# Always backup before major updates
mongodump --uri="$DATABASE_URI" --out="./backups/pre_update_$(date +%Y%m%d)"
```

## 📞 Support

For deployment issues:

1. **Check Logs:** Always start with logs
2. **Verify Environment:** Ensure all variables are set
3. **Test Locally:** Test configuration locally first
4. **Documentation:** Refer to this guide and README
5. **Community:** Check GitHub issues and discussions

## 🎯 Next Steps

After successful deployment:

1. **Test Bot Commands:** Verify all features work
2. **Monitor Performance:** Set up monitoring and alerts
3. **User Onboarding:** Create user guides and tutorials
4. **Content Upload:** Start adding study materials
5. **User Feedback:** Collect and implement user suggestions

---

**Happy Deploying! 🚀**

Your Study Bot is now ready to help students learn effectively!
