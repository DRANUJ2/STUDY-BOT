#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify filter conflict fix
"""

import sys
import os

def test_filter_imports():
    """Test that filters can be imported without conflicts"""
    try:
        from pyrogram import filters
        print("✅ Pyrogram filters import successful")
        return True
    except Exception as e:
        print(f"❌ Pyrogram filters import failed: {e}")
        return False

def test_database_imports():
    """Test database imports without conflicts"""
    try:
        from database.study_db import db as study_db
        print("✅ Database study_db import successful")
        return True
    except Exception as e:
        print(f"❌ Database study_db import failed: {e}")
        return False

def test_filter_usage():
    """Test that filters can be used without conflicts"""
    try:
        from pyrogram import filters
        
        # Test the specific filter that was causing issues
        test_filter = filters.text & filters.private & ~filters.command
        print("✅ Filter usage test successful")
        return True
    except Exception as e:
        print(f"❌ Filter usage test failed: {e}")
        return False

def test_combined_imports():
    """Test both database and filters together"""
    try:
        from pyrogram import filters
        from database.study_db import db as study_db
        
        # Test filter usage
        test_filter = filters.text & filters.private & ~filters.command
        print("✅ Combined imports test successful")
        return True
    except Exception as e:
        print(f"❌ Combined imports test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Testing filter conflict fix...")
    print("=" * 50)
    
    # Test individual components
    filter_import_ok = test_filter_imports()
    db_import_ok = test_database_imports()
    filter_usage_ok = test_filter_usage()
    combined_ok = test_combined_imports()
    
    print("=" * 50)
    if filter_import_ok and db_import_ok and filter_usage_ok and combined_ok:
        print("✅ All tests passed! Filter conflict should be fixed.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
