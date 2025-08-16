#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Study Bot Test Script

This script tests the basic functionality of the Study Bot setup.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import config
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from database.study_db import init_db
        print("✅ Study database imported successfully")
    except Exception as e:
        print(f"❌ Failed to import study database: {e}")
        return False
    
    try:
        from studybot.Bot import studybot
        print("✅ Study bot imported successfully")
    except Exception as e:
        print(f"❌ Failed to import study bot: {e}")
        return False
    
    return True

def test_config():
    """Test configuration values"""
    print("\n🔧 Testing configuration...")
    
    try:
        import config
        
        # Check essential config values
        essential_configs = [
            'API_ID',
            'API_HASH', 
            'BOT_TOKEN',
            'DATABASE_URI',
            'DATABASE_NAME'
        ]
        
        for config_name in essential_configs:
            value = getattr(config, config_name, None)
            if value:
                print(f"✅ {config_name}: {'*' * len(str(value)) if 'TOKEN' in config_name or 'HASH' in config_name else value}")
            else:
                print(f"⚠️  {config_name}: Not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test configuration: {e}")
        return False

async def test_database():
    """Test database connection"""
    print("\n🗄️  Testing database connection...")
    
    try:
        from database.study_db import init_db
        
        # Try to initialize database
        success = await init_db()
        if success:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'config.py',
        'bot.py',
        'start.py',
        'requirements.txt',
        'env_template.txt',
        '.env'
    ]
    
    required_dirs = [
        'database',
        'plugins',
        'studybot'
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_good = False
    
    for dir_path in required_dirs:
        if Path(dir_path).exists() and Path(dir_path).is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing")
            all_good = False
    
    return all_good

async def main():
    """Main test function"""
    print("🧪 Study Bot Setup Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test configuration
    if not test_config():
        print("\n❌ Configuration tests failed")
        return False
    
    # Test file structure
    if not test_file_structure():
        print("\n❌ File structure tests failed")
        return False
    
    # Test database (only if .env exists)
    if Path('.env').exists():
        if not await test_database():
            print("\n⚠️  Database tests failed (check your .env configuration)")
        else:
            print("\n✅ Database tests passed")
    else:
        print("\n⚠️  Skipping database tests (no .env file)")
    
    print("\n🎉 Basic tests completed!")
    print("\n📋 Recommendations:")
    print("1. Make sure all required values are set in .env")
    print("2. Verify MongoDB connection string")
    print("3. Check bot tokens and API credentials")
    print("4. Run: python start.py")
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
