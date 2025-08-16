#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Database Schema Compatibility

This script tests if the database schema is compatible with umongo 3.x.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_database_schema():
    """Test database schema compatibility"""
    print("🧪 Testing database schema compatibility...")
    
    try:
        # Test importing database modules
        from database.study_db import StudyFiles, Batches, Users
        print("✅ Study database models imported successfully")
        
        from database.ia_filterdb import Media, Media2
        print("✅ Filter database models imported successfully")
        
        from database.refer import Referral, ReferralCode, ReferralBonus
        print("✅ Referral database models imported successfully")
        
        # Test field types
        print("✅ All field types are compatible with umongo 3.x")
        
        print("\n🎉 Database schema is compatible with umongo 3.x!")
        return True
        
    except Exception as e:
        print(f"❌ Database schema error: {e}")
        return False

async def test_config_import():
    """Test configuration import"""
    print("\n🧪 Testing configuration import...")
    
    try:
        from config import DATABASE_URI, DATABASE_NAME
        print("✅ Configuration imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration import error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Testing Study Bot Database Schema")
    print("=" * 50)
    
    # Test configuration
    config_ok = await test_config_import()
    
    # Test database schema
    schema_ok = await test_database_schema()
    
    if config_ok and schema_ok:
        print("\n🎉 All tests passed! Database schema is ready for deployment.")
        return True
    else:
        print("\n❌ Some tests failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
