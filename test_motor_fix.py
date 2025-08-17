#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify motor import fix
"""

import sys
import os

def test_motor_import():
    """Test motor import"""
    try:
        import motor
        print("✅ Motor import successful")
        return True
    except ImportError as e:
        print(f"❌ Motor import failed: {e}")
        return False

def test_database_imports():
    """Test database module imports"""
    try:
        # Test importing database modules
        from database import study_db, ia_filterdb, refer
        print("✅ Database module imports successful")
        return True
    except Exception as e:
        print(f"❌ Database module imports failed: {e}")
        return False

def test_config_import():
    """Test config import"""
    try:
        from config import *
        print("✅ Config import successful")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

def main():
    """Main test function"""
    print("Testing motor import fix...")
    print("=" * 50)
    
    # Test motor import
    motor_ok = test_motor_import()
    
    # Test config import
    config_ok = test_config_import()
    
    # Test database imports
    db_ok = test_database_imports()
    
    print("=" * 50)
    if motor_ok and config_ok and db_ok:
        print("✅ All tests passed! Motor import issue should be fixed.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
