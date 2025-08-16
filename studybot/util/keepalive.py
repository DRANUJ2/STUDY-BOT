import asyncio
import aiohttp
import logging
from config import *

logger = logging.getLogger(__name__)

async def ping_server():
    """Keep the bot alive by pinging external services"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                # Ping uptimerobot or similar service
                if ON_HEROKU:
                    url = f"https://{HEROKU_APP_NAME}.herokuapp.com"
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                logger.info("Keepalive ping successful")
                            else:
                                logger.warning(f"Keepalive ping failed with status {response.status}")
                    except Exception as e:
                        logger.error(f"Keepalive ping error: {e}")
                
                # Wait for 25 minutes before next ping
                await asyncio.sleep(1500)
                
        except Exception as e:
            logger.error(f"Error in keepalive: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retry

async def start_keepalive():
    """Start the keepalive task"""
    try:
        asyncio.create_task(ping_server())
        logger.info("Keepalive task started")
    except Exception as e:
        logger.error(f"Failed to start keepalive: {e}")
