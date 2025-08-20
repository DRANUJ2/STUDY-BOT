#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify logging configuration
"""

import os
import sys
import logging
import logging.config
from pathlib import Path

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

def test_basic_logging():
    """Test basic logging setup"""
    print("Testing basic logging...")
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/test.log", mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create logger
    logger = logging.getLogger("TestLogger")
    
    # Log some messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("Basic logging test completed. Check logs/test.log")

def test_config_logging():
    """Test logging configuration from file"""
    print("\nTesting logging configuration from file...")
    
    # Load logging configuration
    try:
        logging.config.fileConfig('logging.conf')
        logger = logging.getLogger("studybot")
        
        # Log some messages
        logger.debug("This is a debug message from config")
        logger.info("This is an info message from config")
        logger.warning("This is a warning message from config")
        logger.error("This is an error message from config")
        
        print("Config logging test completed. Check logs/studybot.log")
    except Exception as e:
        print(f"Error loading logging configuration: {e}")

def main():
    """Main function"""
    print("=== Testing Logging Configuration ===")
    
    # Test basic logging
    test_basic_logging()
    
    # Test config logging
    test_config_logging()
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    main()