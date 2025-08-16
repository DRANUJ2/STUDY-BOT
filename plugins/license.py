"""
Study Bot - License Plugin
Provides license management and verification functionality
"""

import hashlib
import time
import json
import logging
from typing import Optional, Dict, Any
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS

logger = logging.getLogger(__name__)

class LicenseManager:
    """License management system"""
    
    def __init__(self):
        self.licenses = {}
        self.license_file = "licenses.json"
        self.load_licenses()
    
    def load_licenses(self):
        """Load licenses from file"""
        try:
            with open(self.license_file, 'r') as f:
                self.licenses = json.load(f)
        except FileNotFoundError:
            self.licenses = {}
            self.save_licenses()
        except Exception as e:
            logger.error(f"Error loading licenses: {e}")
            self.licenses = {}
    
    def save_licenses(self):
        """Save licenses to file"""
        try:
            with open(self.license_file, 'w') as f:
                json.dump(self.licenses, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving licenses: {e}")
    
    def generate_license(self, user_id: int, duration_days: int = 30, 
                        features: list = None) -> str:
        """
        Generate a new license
        
        Args:
            user_id (int): User ID
            duration_days (int): License duration in days
            features (list): List of enabled features
            
        Returns:
            str: Generated license key
        """
        if features is None:
            features = ["basic"]
        
        # Create license data
        license_data = {
            "user_id": user_id,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + (duration_days * 24 * 60 * 60),
            "features": features,
            "status": "active"
        }
        
        # Generate license key
        license_key = self._hash_license_data(license_data)
        
        # Store license
        self.licenses[license_key] = license_data
        self.save_licenses()
        
        return license_key
    
    def _hash_license_data(self, data: dict) -> str:
        """Hash license data to create key"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16].upper()
    
    def validate_license(self, license_key: str, user_id: int = None) -> Dict[str, Any]:
        """
        Validate a license
        
        Args:
            license_key (str): License key to validate
            user_id (int, optional): User ID to check against
            
        Returns:
            Dict[str, Any]: Validation result
        """
        if license_key not in self.licenses:
            return {"valid": False, "error": "Invalid license key"}
        
        license_data = self.licenses[license_key]
        
        # Check if license is active
        if license_data["status"] != "active":
            return {"valid": False, "error": "License is not active"}
        
        # Check if license has expired
        if time.time() > license_data["expires_at"]:
            license_data["status"] = "expired"
            self.save_licenses()
            return {"valid": False, "error": "License has expired"}
        
        # Check user ID if provided
        if user_id and license_data["user_id"] != user_id:
            return {"valid": False, "error": "License not valid for this user"}
        
        return {
            "valid": True,
            "features": license_data["features"],
            "expires_at": license_data["expires_at"],
            "days_remaining": (license_data["expires_at"] - time.time()) // (24 * 60 * 60)
        }
    
    def revoke_license(self, license_key: str) -> bool:
        """
        Revoke a license
        
        Args:
            license_key (str): License key to revoke
            
        Returns:
            bool: True if revoked successfully
        """
        if license_key in self.licenses:
            self.licenses[license_key]["status"] = "revoked"
            self.save_licenses()
            return True
        return False
    
    def extend_license(self, license_key: str, additional_days: int) -> bool:
        """
        Extend a license
        
        Args:
            license_key (str): License key to extend
            additional_days (int): Additional days to add
            
        Returns:
            bool: True if extended successfully
        """
        if license_key in self.licenses:
            self.licenses[license_key]["expires_at"] += (additional_days * 24 * 60 * 60)
            self.save_licenses()
            return True
        return False
    
    def get_user_licenses(self, user_id: int) -> list:
        """
        Get all licenses for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of user licenses
        """
        user_licenses = []
        for key, data in self.licenses.items():
            if data["user_id"] == user_id:
                user_licenses.append({
                    "key": key,
                    "data": data
                })
        return user_licenses
    
    def get_license_stats(self) -> Dict[str, Any]:
        """
        Get license statistics
        
        Returns:
            Dict[str, Any]: License statistics
        """
        total = len(self.licenses)
        active = sum(1 for data in self.licenses.values() if data["status"] == "active")
        expired = sum(1 for data in self.licenses.values() if data["status"] == "expired")
        revoked = sum(1 for data in self.licenses.values() if data["status"] == "revoked")
        
        return {
            "total": total,
            "active": active,
            "expired": expired,
            "revoked": revoked
        }

# Global license manager instance
license_manager = LicenseManager()

# Bot commands
@Client.on_message(filters.command("generate_license") & filters.private)
async def generate_license_command(client: Client, message: Message):
    """Handle generate license command"""
    try:
        # Check if user is admin
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ This command is only for admins!")
            return
        
        # Parse command arguments
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text(
                "❌ **Usage:** `/generate_license <user_id> <duration_days> [features]`\n\n"
                "**Example:** `/generate_license 123456789 30 basic,premium`"
            )
            return
        
        try:
            user_id = int(args[1])
            duration_days = int(args[2])
        except ValueError:
            await message.reply_text("❌ Invalid user ID or duration!")
            return
        
        # Parse features
        features = ["basic"]
        if len(args) > 3:
            features = args[3].split(",")
        
        # Generate license
        license_key = license_manager.generate_license(user_id, duration_days, features)
        
        await message.reply_text(
            f"✅ **License Generated Successfully!**\n\n"
            f"🔑 **License Key:** `{license_key}`\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"⏱️ **Duration:** {duration_days} days\n"
            f"🚀 **Features:** {', '.join(features)}\n"
            f"📅 **Expires:** <code>{time.ctime(time.time() + (duration_days * 24 * 60 * 60))}</code>"
        )
        
    except Exception as e:
        logger.error(f"Error in generate license command: {e}")
        await message.reply_text(f"❌ Error generating license: {e}")

@Client.on_message(filters.command("validate_license") & filters.private)
async def validate_license_command(client: Client, message: Message):
    """Handle validate license command"""
    try:
        # Parse command arguments
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(
                "❌ **Usage:** `/validate_license <license_key>`\n\n"
                "**Example:** `/validate_license ABC123DEF456GHIJ`"
            )
            return
        
        license_key = args[1].upper()
        user_id = message.from_user.id
        
        # Validate license
        result = license_manager.validate_license(license_key, user_id)
        
        if result["valid"]:
            await message.reply_text(
                f"✅ **License Valid!**\n\n"
                f"🔑 **License Key:** `{license_key}`\n"
                f"🚀 **Features:** {', '.join(result['features'])}\n"
                f"⏰ **Days Remaining:** {result['days_remaining']}\n"
                f"📅 **Expires:** <code>{time.ctime(result['expires_at'])}</code>"
            )
        else:
            await message.reply_text(
                f"❌ **License Invalid!**\n\n"
                f"🔑 **License Key:** `{license_key}`\n"
                f"❌ **Error:** {result['error']}"
            )
        
    except Exception as e:
        logger.error(f"Error in validate license command: {e}")
        await message.reply_text(f"❌ Error validating license: {e}")

@Client.on_message(filters.command("revoke_license") & filters.private)
async def revoke_license_command(client: Client, message: Message):
    """Handle revoke license command"""
    try:
        # Check if user is admin
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ This command is only for admins!")
            return
        
        # Parse command arguments
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(
                "❌ **Usage:** `/revoke_license <license_key>`\n\n"
                "**Example:** `/revoke_license ABC123DEF456GHIJ`"
            )
            return
        
        license_key = args[1].upper()
        
        # Revoke license
        if license_manager.revoke_license(license_key):
            await message.reply_text(
                f"✅ **License Revoked Successfully!**\n\n"
                f"🔑 **License Key:** `{license_key}`\n"
                f"📅 **Revoked At:** <code>{time.ctime()}</code>"
            )
        else:
            await message.reply_text("❌ License not found!")
        
    except Exception as e:
        logger.error(f"Error in revoke license command: {e}")
        await message.reply_text(f"❌ Error revoking license: {e}")

@Client.on_message(filters.command("extend_license") & filters.private)
async def extend_license_command(client: Client, message: Message):
    """Handle extend license command"""
    try:
        # Check if user is admin
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ This command is only for admins!")
            return
        
        # Parse command arguments
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text(
                "❌ **Usage:** `/extend_license <license_key> <additional_days>`\n\n"
                "**Example:** `/extend_license ABC123DEF456GHIJ 30`"
            )
            return
        
        license_key = args[1].upper()
        try:
            additional_days = int(args[2])
        except ValueError:
            await message.reply_text("❌ Invalid number of days!")
            return
        
        # Extend license
        if license_manager.extend_license(license_key, additional_days):
            # Get updated license info
            result = license_manager.validate_license(license_key)
            if result["valid"]:
                await message.reply_text(
                    f"✅ **License Extended Successfully!**\n\n"
                    f"🔑 **License Key:** `{license_key}`\n"
                    f"⏰ **Additional Days:** {additional_days}\n"
                    f"📅 **New Expiry:** <code>{time.ctime(result['expires_at'])}</code>"
                )
            else:
                await message.reply_text("✅ License extended but validation failed!")
        else:
            await message.reply_text("❌ License not found!")
        
    except Exception as e:
        logger.error(f"Error in extend license command: {e}")
        await message.reply_text(f"❌ Error extending license: {e}")

@Client.on_message(filters.command("license_stats") & filters.private)
async def license_stats_command(client: Client, message: Message):
    """Handle license stats command"""
    try:
        # Check if user is admin
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ This command is only for admins!")
            return
        
        # Get license statistics
        stats = license_manager.get_license_stats()
        
        await message.reply_text(
            f"📊 **License Statistics**\n\n"
            f"🔑 **Total Licenses:** {stats['total']}\n"
            f"✅ **Active:** {stats['active']}\n"
            f"⏰ **Expired:** {stats['expired']}\n"
            f"❌ **Revoked:** {stats['revoked']}\n\n"
            f"📅 **Generated At:** <code>{time.ctime()}</code>"
        )
        
    except Exception as e:
        logger.error(f"Error in license stats command: {e}")
        await message.reply_text(f"❌ Error getting license stats: {e}")

@Client.on_message(filters.command("my_licenses") & filters.private)
async def my_licenses_command(client: Client, message: Message):
    """Handle my licenses command"""
    try:
        user_id = message.from_user.id
        
        # Get user licenses
        user_licenses = license_manager.get_user_licenses(user_id)
        
        if not user_licenses:
            await message.reply_text(
                "📋 **Your Licenses**\n\n"
                "❌ No licenses found for your account.\n\n"
                "💡 Contact an admin to get a license!"
            )
            return
        
        # Format licenses
        licenses_text = f"📋 **Your Licenses**\n\n"
        licenses_text += f"🔑 **Total Licenses:** {len(user_licenses)}\n\n"
        
        for i, license_info in enumerate(user_licenses, 1):
            key = license_info["key"]
            data = license_info["data"]
            
            # Check if license is valid
            result = license_manager.validate_license(key, user_id)
            status_emoji = "✅" if result["valid"] else "❌"
            status_text = "Active" if result["valid"] else "Invalid"
            
            licenses_text += f"{i}. {status_emoji} **{status_text}**\n"
            licenses_text += f"   🔑 **Key:** `{key}`\n"
            licenses_text += f"   🚀 **Features:** {', '.join(data['features'])}\n"
            licenses_text += f"   📅 **Expires:** <code>{time.ctime(data['expires_at'])}</code>\n\n"
        
        await message.reply_text(licenses_text)
        
    except Exception as e:
        logger.error(f"Error in my licenses command: {e}")
        await message.reply_text(f"❌ Error getting licenses: {e}")

# Utility functions for other plugins
def is_license_valid(license_key: str, user_id: int = None) -> bool:
    """
    Check if a license is valid
    
    Args:
        license_key (str): License key to check
        user_id (int, optional): User ID to check against
        
    Returns:
        bool: True if license is valid
    """
    result = license_manager.validate_license(license_key, user_id)
    return result["valid"]

def get_license_features(license_key: str) -> list:
    """
    Get features for a license
    
    Args:
        license_key (str): License key
        
    Returns:
        list: List of features
    """
    result = license_manager.validate_license(license_key)
    if result["valid"]:
        return result.get("features", [])
    return []

def has_feature(license_key: str, feature: str) -> bool:
    """
    Check if a license has a specific feature
    
    Args:
        license_key (str): License key
        feature (str): Feature to check
        
    Returns:
        bool: True if feature is available
    """
    features = get_license_features(license_key)
    return feature in features

def require_license(feature: str = "basic"):
    """
    Decorator to require a valid license for a function
    
    Args:
        feature (str): Required feature
        
    Returns:
        function: Decorated function
    """
    def decorator(func):
        async def wrapper(client, message, *args, **kwargs):
            # Check if user has a valid license
            user_id = message.from_user.id
            user_licenses = license_manager.get_user_licenses(user_id)
            
            has_valid_license = False
            for license_info in user_licenses:
                if license_manager.validate_license(license_info["key"], user_id)["valid"]:
                    if feature in license_info["data"]["features"]:
                        has_valid_license = True
                        break
            
            if not has_valid_license:
                await message.reply_text(
                    f"❌ **License Required!**\n\n"
                    f"🚀 **Feature:** {feature}\n"
                    f"💡 Contact an admin to get a license with this feature!"
                )
                return
            
            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator
