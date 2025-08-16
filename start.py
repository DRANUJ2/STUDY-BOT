#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Study Bot Startup Script

This script provides an easy way to start the Study Bot with proper error handling.
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("study_bot.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'pyrogram',
        'umongo',
        'aiohttp',
        'pytz'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    # Check motor separately as it\'s imported as motor.motor_asyncio
    try:
        from motor import motor_asyncio
    except ImportError:
        missing_modules.append("motor")

    if missing_modules:
        print(f"❌ Missing required modules: {\', \'.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are available")
    return True

def check_config():
    """Check if configuration is available (either .env file or environment variables)"""
    # Check if .env file exists
    config_file = Path(".env")
    if config_file.exists():
        print("✅ Configuration file (.env) found")
        return True
    
    # Check if essential environment variables are set
    essential_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN']
    missing_vars = []
    
    for var in essential_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  No .env file found and missing essential environment variables:")
        print(f"   Missing: {\', \'.join(missing_vars)}")
        print("   Please either:")
        print("   1. Copy env_template.txt to .env and configure it, or")
        print("   2. Set the environment variables directly")
        return False
    
    print("✅ Essential environment variables are configured")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting Study Bot...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Check configuration
        if not check_config():
            print("Please configure the bot before starting")
            sys.exit(1)
        
        print("✅ All checks passed")
        print("🚀 Starting Study Bot...")
        print("=" * 50)
        
        # Import and start the bot
        from bot import studybot_start
        
        # Start the bot
        import asyncio
        asyncio.run(studybot_start())
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

