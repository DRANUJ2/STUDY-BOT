import asyncio
import logging
from studybot.Bot import clients, studybot, content_bot

logger = logging.getLogger(__name__)

async def initialize_clients():
    """Initialize all bot clients"""
    try:
        # Start content bot if token is provided
        if content_bot.bot_token:
            await content_bot.start()
            logger.info("Content Bot started successfully")
        else:
            logger.warning("Content Bot token not provided, skipping initialization")
            
        logger.info("All clients initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing clients: {e}")
        return False

async def stop_clients():
    """Stop all bot clients"""
    try:
        if content_bot.is_connected:
            await content_bot.stop()
            logger.info("Content Bot stopped successfully")
            
        logger.info("All clients stopped successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error stopping clients: {e}")
        return False

def get_client(client_type="main"):
    """Get client by type"""
    return clients.get(client_type, studybot)

async def broadcast_message(client_type, chat_ids, message, **kwargs):
    """Broadcast message using specified client"""
    try:
        client = get_client(client_type)
        success_count = 0
        failed_count = 0
        
        for chat_id in chat_ids:
            try:
                await client.send_message(chat_id, message, **kwargs)
                success_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to send message to {chat_id}: {e}")
                failed_count += 1
                
        logger.info(f"Broadcast completed: {success_count} success, {failed_count} failed")
        return {"success": success_count, "failed": failed_count}
        
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        return {"success": 0, "failed": 0}
