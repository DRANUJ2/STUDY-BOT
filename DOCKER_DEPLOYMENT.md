# 🐳 Study Bot Docker Deployment Guide

This guide will help you deploy the Study Bot using Docker.

## 🚀 Quick Start

### 1. Prerequisites
- Docker installed and running
- Docker Compose installed
- Git (to clone the repository)

### 2. Clone and Setup
```bash
git clone <your-repo-url>
cd Study_Bot
```

### 3. Build and Run
```bash
# Make the build script executable
chmod +x docker-build.sh

# Build and test the Docker image
./docker-build.sh
```

## 🔧 Manual Docker Build

If you prefer to build manually:

```bash
# Build the image
docker build -t study-bot:latest .

# Test the container
docker run -d --name study-bot-test study-bot:latest

# Check logs
docker logs study-bot-test

# Stop and remove test container
docker stop study-bot-test
docker rm study-bot-test
```

## 🐙 Using Docker Compose

### 1. Basic Setup (MongoDB + Bot)
```bash
# Start only the essential services
docker-compose up -d mongodb studybot
```

### 2. Full Stack (MongoDB + Redis + Bot + Monitoring)
```bash
# Start all services
docker-compose up -d
```

### 3. View Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f studybot
```

## 📋 Environment Variables

Create a `.env` file in your project root:

```env
# Bot Configuration
SESSION=StudyBot_Session
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
CONTENT_BOT_TOKEN=your_content_bot_token

# Database
DATABASE_URI=mongodb://studybot:your_password@mongodb:27017/studybot_db?authSource=admin
DATABASE_NAME=studybot_db

# Channels
ADMINS=your_admin_id
CHANNELS=your_channel_id
LOG_CHANNEL=your_log_channel_id

# Other Settings
ON_HEROKU=false
PORT=8080
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Build Fails with Dependency Conflicts
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t study-bot:latest .
```

#### 2. Container Won't Start
```bash
# Check container logs
docker logs study-bot

# Check container status
docker ps -a
```

#### 3. Database Connection Issues
```bash
# Check MongoDB container
docker-compose logs mongodb

# Test MongoDB connection
docker exec -it studybot_mongodb mongosh
```

### Debug Commands

```bash
# Enter running container
docker exec -it studybot_app bash

# Check container resources
docker stats studybot_app

# View container details
docker inspect studybot_app
```

## 📊 Monitoring

### Health Checks
The containers include health checks that you can monitor:

```bash
# Check health status
docker-compose ps

# View health check logs
docker inspect studybot_app | grep -A 10 Health
```

### Logs and Metrics
- **Application Logs**: `docker-compose logs -f studybot`
- **Database Logs**: `docker-compose logs -f mongodb`
- **System Metrics**: Access Grafana at `http://localhost:3000`

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use Docker secrets for production deployments
- Rotate API keys and passwords regularly

### 2. Network Security
- Expose only necessary ports
- Use internal Docker networks
- Consider using reverse proxy (Nginx) for SSL termination

### 3. Container Security
- Run containers as non-root users
- Keep base images updated
- Scan images for vulnerabilities

## 🚀 Production Deployment

### 1. Multi-Environment Setup
```bash
# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

### 2. Load Balancing
```bash
# Scale the bot service
docker-compose up -d --scale studybot=3
```

### 3. Backup Strategy
```bash
# Backup MongoDB
docker exec studybot_mongodb mongodump --out /backup

# Backup volumes
docker run --rm -v studybot_mongodb_data:/data -v $(pwd):/backup alpine tar czf /backup/mongodb_backup.tar.gz -C /data .
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Docker Guide](https://hub.docker.com/_/mongo)
- [Redis Docker Guide](https://hub.docker.com/_/redis)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review container logs
3. Check the main README.md for general setup issues
4. Open an issue in the repository

---

**Happy Deploying! 🎉**
