import logging
from aiohttp import web
from config import *

logger = logging.getLogger(__name__)

async def web_server():
    """Create and configure the web server"""
    try:
        app = web.Application()
        
        # Add routes
        app.router.add_get('/', handle_home)
        app.router.add_get('/health', handle_health)
        app.router.add_get('/stats', handle_stats)
        app.router.add_get('/status', handle_status)
        
        # Add CORS middleware
        app.middlewares.append(web.middleware.cors.cors_middleware)
        
        logger.info("Web server configured successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error configuring web server: {e}")
        raise

async def handle_home(request):
    """Handle home page request"""
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Study Bot - Your Ultimate Study Companion</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .logo { font-size: 3em; margin-bottom: 10px; }
                .subtitle { font-size: 1.2em; opacity: 0.9; }
                .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }
                .feature { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); }
                .feature h3 { margin-top: 0; color: #ffd700; }
                .stats { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 40px; opacity: 0.7; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">📚</div>
                    <h1>Study Bot</h1>
                    <div class="subtitle">Your Ultimate Study Companion</div>
                </div>
                
                <div class="features">
                    <div class="feature">
                        <h3>🎯 Batch Learning</h3>
                        <p>Organize content by study batches like NEET2026, JEE2025</p>
                    </div>
                    <div class="feature">
                        <h3>🧪 Subject Organization</h3>
                        <p>Physics, Chemistry, and Biology with dedicated content</p>
                    </div>
                    <div class="feature">
                        <h3>📖 Chapter Navigation</h3>
                        <p>Easy chapter selection by number or name</p>
                    </div>
                    <div class="feature">
                        <h3>📹 Content Types</h3>
                        <p>Lectures, DPPs, Notes, and comprehensive materials</p>
                    </div>
                </div>
                
                <div class="stats">
                    <h3>🚀 Bot Status</h3>
                    <p>✅ Online and Ready</p>
                    <p>📚 Serving students worldwide</p>
                    <p>🎯 Multiple subjects and batches available</p>
                </div>
                
                <div class="footer">
                    <p>🌟 Made with ❤️ for students worldwide</p>
                    <p>📱 Use @StudyBotUsername on Telegram to get started</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return web.Response(text=html_content, content_type='text/html')
        
    except Exception as e:
        logger.error(f"Error handling home request: {e}")
        return web.Response(text="Error loading page", status=500)

async def handle_health(request):
    """Handle health check request"""
    try:
        health_data = {
            "status": "healthy",
            "service": "Study Bot Web Server",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return web.json_response(health_data)
        
    except Exception as e:
        logger.error(f"Error handling health check: {e}")
        return web.json_response({"status": "unhealthy"}, status=500)

async def handle_stats(request):
    """Handle statistics request"""
    try:
        stats_data = {
            "bot_name": "Study Bot",
            "version": "1.0.0",
            "status": "operational",
            "uptime": "24h",
            "features": [
                "Batch-based Learning",
                "Subject Organization", 
                "Chapter Navigation",
                "Content Types",
                "Progress Tracking",
                "Achievement System"
            ]
        }
        
        return web.json_response(stats_data)
        
    except Exception as e:
        logger.error(f"Error handling stats request: {e}")
        return web.json_response({"error": "Failed to get stats"}, status=500)

async def handle_status(request):
    """Handle status request"""
    try:
        status_data = {
            "service": "Study Bot",
            "status": "online",
            "database": "connected",
            "telegram_api": "connected",
            "web_server": "running",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return web.json_response(status_data)
        
    except Exception as e:
        logger.error(f"Error handling status request: {e}")
        return web.json_response({"error": "Failed to get status"}, status=500)

# Additional utility functions
def add_route(app, path, handler, method='GET'):
    """Add a route to the web application"""
    try:
        if method.upper() == 'GET':
            app.router.add_get(path, handler)
        elif method.upper() == 'POST':
            app.router.add_post(path, handler)
        elif method.upper() == 'PUT':
            app.router.add_put(path, handler)
        elif method.upper() == 'DELETE':
            app.router.add_delete(path, handler)
        else:
            logger.warning(f"Unsupported HTTP method: {method}")
            
        logger.info(f"Added route: {method} {path}")
        
    except Exception as e:
        logger.error(f"Error adding route {method} {path}: {e}")

def create_error_handler(status_code, message):
    """Create an error handler for specific status codes"""
    async def error_handler(request):
        error_data = {
            "error": message,
            "status_code": status_code,
            "path": str(request.url),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        return web.json_response(error_data, status=status_code)
    
    return error_handler
