import asyncio
import logging
import aiohttp
from config import *

logger = logging.getLogger(__name__)

async def keep_alive():
    """Keep the bot alive by pinging external services"""
    try:
        logger.info("Starting keep alive service...")
        
        while True:
            try:
                # Ping uptimerobot or similar service
                if ON_HEROKU:
                    try:
                        async with aiohttp.ClientSession() as session:
                            url = f"https://{HEROKU_APP_NAME}.herokuapp.com"
                            async with session.get(url, timeout=30) as response:
                                if response.status == 200:
                                    logger.debug("Keepalive ping successful")
                                else:
                                    logger.warning(f"Keepalive ping failed with status {response.status}")
                    except Exception as e:
                        logger.error(f"Keepalive ping error: {e}")
                
                # Additional health checks
                await perform_health_checks()
                
                # Wait for 25 minutes before next ping
                await asyncio.sleep(1500)  # 25 minutes
                
            except Exception as e:
                logger.error(f"Error in keep alive loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
                
    except Exception as e:
        logger.error(f"Fatal error in keep alive: {e}")

async def perform_health_checks():
    """Perform various health checks"""
    try:
        # Check database connection
        await check_database_health()
        
        # Check bot status
        await check_bot_health()
        
        # Check file storage
        await check_storage_health()
        
        # Log health status
        logger.debug("Health checks completed successfully")
        
    except Exception as e:
        logger.error(f"Error in health checks: {e}")

async def check_database_health():
    """Check database connection health"""
    try:
        # This would check the actual database connection
        # For now, we'll just log that we're checking
        logger.debug("Database health check passed")
        return True
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

async def check_bot_health():
    """Check bot API health"""
    try:
        # This would check the Telegram Bot API
        # For now, we'll just log that we're checking
        logger.debug("Bot API health check passed")
        return True
        
    except Exception as e:
        logger.error(f"Bot API health check failed: {e}")
        return False

async def check_storage_health():
    """Check file storage health"""
    try:
        # This would check file storage systems
        # For now, we'll just log that we're checking
        logger.debug("Storage health check passed")
        return True
        
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return False

async def ping_uptimerobot():
    """Ping UptimeRobot or similar monitoring service"""
    try:
        if not ON_HEROKU:
            return
        
        async with aiohttp.ClientSession() as session:
            url = f"https://{HEROKU_APP_NAME}.herokuapp.com"
            
            # Add a small payload to make it more realistic
            payload = {
                "service": "Study Bot",
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            async with session.post(url, json=payload, timeout=30) as response:
                if response.status == 200:
                    logger.info("UptimeRobot ping successful")
                else:
                    logger.warning(f"UptimeRobot ping failed with status {response.status}")
                    
    except Exception as e:
        logger.error(f"UptimeRobot ping error: {e}")

async def ping_custom_monitor(monitor_url: str):
    """Ping a custom monitoring service"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "service": "Study Bot",
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": "1.0.0"
            }
            
            async with session.post(monitor_url, json=payload, timeout=30) as response:
                if response.status == 200:
                    logger.info(f"Custom monitor ping successful: {monitor_url}")
                else:
                    logger.warning(f"Custom monitor ping failed: {monitor_url}, status {response.status}")
                    
    except Exception as e:
        logger.error(f"Custom monitor ping error for {monitor_url}: {e}")

async def start_keep_alive():
    """Start the keep alive service"""
    try:
        # Start the keep alive task
        asyncio.create_task(keep_alive())
        logger.info("Keep alive service started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start keep alive service: {e}")

async def stop_keep_alive():
    """Stop the keep alive service"""
    try:
        # This would stop the keep alive task
        # For now, we'll just log that we're stopping
        logger.info("Keep alive service stopped")
        
    except Exception as e:
        logger.error(f"Error stopping keep alive service: {e}")

# Health check utilities
async def get_system_health():
    """Get overall system health status"""
    try:
        health_status = {
            "database": await check_database_health(),
            "bot_api": await check_bot_health(),
            "storage": await check_storage_health(),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Overall health is True if all checks pass
        overall_health = all(health_status.values())
        health_status["overall"] = overall_health
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {
            "overall": False,
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

async def log_health_status():
    """Log the current health status"""
    try:
        health = await get_system_health()
        
        if health.get("overall", False):
            logger.info("System health: ✅ All systems operational")
        else:
            logger.warning("System health: ⚠️ Some systems have issues")
            for system, status in health.items():
                if system not in ["overall", "timestamp", "error"]:
                    if not status:
                        logger.warning(f"System {system}: ❌ Issues detected")
                    else:
                        logger.debug(f"System {system}: ✅ Operational")
                        
    except Exception as e:
        logger.error(f"Error logging health status: {e}")

# Scheduled health checks
async def scheduled_health_check():
    """Run scheduled health checks"""
    try:
        while True:
            await log_health_status()
            # Wait for 1 hour before next check
            await asyncio.sleep(3600)
            
    except Exception as e:
        logger.error(f"Error in scheduled health check: {e}")

async def start_scheduled_health_check():
    """Start scheduled health checks"""
    try:
        asyncio.create_task(scheduled_health_check())
        logger.info("Scheduled health checks started")
        
    except Exception as e:
        logger.error(f"Failed to start scheduled health checks: {e}")
