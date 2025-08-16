#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Study Bot Setup Script

This script helps you set up the Study Bot by creating the necessary configuration files.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_template = Path('env_template.txt')
    env_file = Path('.env')
    
    if not env_template.exists():
        print("❌ env_template.txt not found!")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return False
    
    try:
        # Read template
        with open(env_template, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Create .env file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print("✅ .env file created successfully!")
        print("📝 Please edit .env file with your actual values before starting the bot.")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
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

    # Motor ko alag se check karein
    try:
        from motor import motor_asyncio
    except ImportError:
        missing_modules.append("motor")

    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are available")
    return True
    
    

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'downloads',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created successfully")
    return True

def main():
    """Main setup function"""
    print("🚀 Study Bot Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create directories")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("\n❌ Failed to create .env file")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your actual values")
    print("2. Make sure MongoDB is running")
    print("3. Run: python start.py")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
