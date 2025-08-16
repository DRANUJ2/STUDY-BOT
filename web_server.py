#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Web Server for Study Bot

This file provides a basic web server for Heroku deployment and health checks.
"""

import os
import asyncio
from aiohttp import web
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_home(request):
    """Handle home page request"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Study Bot - Status</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .status { background: #27ae60; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }
            .info { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .feature { margin: 15px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 Study Bot</h1>
            <div class="status">
                🟢 <strong>Status: Online & Running</strong>
            </div>
            <div class="info">
                <h2>About Study Bot</h2>
                <p>Study Bot is your ultimate study companion, providing organized access to comprehensive study materials including lectures, DPPs, and study materials.</p>
                
                <h3>Key Features:</h3>
                <div class="feature">🎯 <strong>Batch-based Learning:</strong> Organized by study batches (NEET2026, JEE2025, etc.)</div>
                <div class="feature">📖 <strong>Subject Organization:</strong> Physics, Chemistry, Biology with expert teachers</div>
                <div class="feature">📚 <strong>Rich Content:</strong> Lectures, DPPs, Mind Maps, Revision notes, and more</div>
                <div class="feature">🔍 <strong>Easy Navigation:</strong> Intuitive button-based interface</div>
                <div class="feature">📊 <strong>Progress Tracking:</strong> Monitor your learning journey</div>
                <div class="feature">🔐 <strong>Dual Bot System:</strong> Efficient content delivery</div>
            </div>
            
            <div class="info">
                <h3>How to Use:</h3>
                <ol>
                    <li>Start the bot with <code>/start</code></li>
                    <li>Use <code>/Anuj &lt;batch_name&gt;</code> to access study materials</li>
                    <li>Navigate through subjects, teachers, and chapters</li>
                    <li>Select content type and enjoy learning!</li>
                </ol>
            </div>
            
            <div class="info">
                <h3>Contact & Support:</h3>
                <p>For support or questions, contact the bot admin or use the <code>/contact</code> command in the bot.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

async def handle_health(request):
    """Handle health check request"""
    health_data = {
        "status": "healthy",
        "service": "Study Bot",
        "version": "1.0.0",
        "timestamp": asyncio.get_event_loop().time(),
        "environment": os.getenv("ON_HEROKU", "false")
    }
    return web.json_response(health_data)

async def handle_stats(request):
    """Handle statistics request"""
    stats_data = {
        "service": "Study Bot",
        "uptime": "running",
        "endpoints": ["/", "/health", "/stats"],
        "features": [
            "Batch Management",
            "Content Delivery",
            "User Progress Tracking",
            "Admin Panel",
            "File Upload System"
        ]
    }
    return web.json_response(stats_data)

async def handle_status(request):
    """Handle status request"""
    status_data = {
        "status": "operational",
        "database": "connected",
        "content_bot": "active",
        "web_server": "running",
        "api": "operational"
    }
    return web.json_response(status_data)

def create_app():
    """Create and configure the web application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', handle_home)
    app.router.add_get('/health', handle_health)
    app.router.add_get('/stats', handle_stats)
    app.router.add_get('/status', handle_status)
    
    # Add CORS middleware
    app.middlewares.append(web.middleware.cors.cors_middleware)
    
    return app

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8080))
    
    # Create app
    app = create_app()
    
    # Run the web server
    logger.info(f"Starting Study Bot web server on port {port}")
    web.run_app(app, port=port, host='0.0.0.0')
