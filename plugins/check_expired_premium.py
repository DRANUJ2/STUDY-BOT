import asyncio
import logging
from datetime import datetime, timedelta
from database.study_db import Users
from config import *

logger = logging.getLogger(__name__)

async def check_expired_premium(bot):
    """Check and handle expired premium users"""
    try:
        logger.info("Starting premium expiration check...")
        
        while True:
            try:
                # Find users with expired premium
                current_time = datetime.utcnow()
                expired_users = await Users.find({
                    "is_premium": True,
                    "premium_expiry": {"$lt": current_time}
                }).to_list(length=100)
                
                if expired_users:
                    logger.info(f"Found {len(expired_users)} expired premium users")
                    
                    for user in expired_users:
                        try:
                            # Update user status
                            user.is_premium = False
                            user.premium_expiry = None
                            await user.commit()
                            
                            # Send expiration notification
                            try:
                                await bot.send_message(
                                    chat_id=user.user_id,
                                    text="⚠️ **Premium Expired**\n\n"
                                         "Your premium subscription has expired.\n"
                                         "You can renew your premium to continue enjoying:\n"
                                         "• 🚀 Priority access to content\n"
                                         "• 📚 Unlimited downloads\n"
                                         "• 🎯 Advanced features\n"
                                         "• 🏆 Premium support\n\n"
                                         "Contact admin to renew your subscription."
                                )
                                logger.info(f"Sent expiration notice to user {user.user_id}")
                            except Exception as e:
                                logger.error(f"Failed to send expiration notice to user {user.user_id}: {e}")
                            
                        except Exception as e:
                            logger.error(f"Error processing expired user {user.user_id}: {e}")
                            continue
                    
                    logger.info(f"Processed {len(expired_users)} expired premium users")
                else:
                    logger.debug("No expired premium users found")
                
                # Check for users approaching expiration (7 days before)
                warning_date = current_time + timedelta(days=7)
                warning_users = await Users.find({
                    "is_premium": True,
                    "premium_expiry": {"$lt": warning_date, "$gte": current_time}
                }).to_list(length=100)
                
                if warning_users:
                    logger.info(f"Found {len(warning_users)} users approaching premium expiration")
                    
                    for user in warning_users:
                        try:
                            days_left = (user.premium_expiry - current_time).days
                            
                            # Send warning notification
                            await bot.send_message(
                                chat_id=user.user_id,
                                text=f"⚠️ **Premium Expiring Soon**\n\n"
                                     f"Your premium subscription will expire in {days_left} days.\n"
                                     "To continue enjoying premium features, please renew your subscription.\n\n"
                                     "Contact admin to renew."
                            )
                            logger.info(f"Sent expiration warning to user {user.user_id}")
                            
                        except Exception as e:
                            logger.error(f"Failed to send warning to user {user.user_id}: {e}")
                            continue
                
                # Wait for 24 hours before next check
                await asyncio.sleep(86400)  # 24 hours
                
            except Exception as e:
                logger.error(f"Error in premium check loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
                
    except Exception as e:
        logger.error(f"Fatal error in premium check: {e}")

async def get_premium_stats():
    """Get premium user statistics"""
    try:
        current_time = datetime.utcnow()
        
        # Total premium users
        total_premium = await Users.count_documents({"is_premium": True})
        
        # Active premium users (not expired)
        active_premium = await Users.count_documents({
            "is_premium": True,
            "premium_expiry": {"$gt": current_time}
        })
        
        # Expired premium users
        expired_premium = await Users.count_documents({
            "is_premium": True,
            "premium_expiry": {"$lt": current_time}
        })
        
        # Users expiring in next 7 days
        expiring_soon = await Users.count_documents({
            "is_premium": True,
            "premium_expiry": {
                "$lt": current_time + timedelta(days=7),
                "$gte": current_time
            }
        })
        
        return {
            "total_premium": total_premium,
            "active_premium": active_premium,
            "expired_premium": expired_premium,
            "expiring_soon": expiring_soon
        }
        
    except Exception as e:
        logger.error(f"Error getting premium stats: {e}")
        return {}

async def extend_premium(user_id: int, days: int):
    """Extend premium subscription for a user"""
    try:
        user = await Users.find_one({"_id": user_id})
        if not user:
            return False, "User not found"
        
        current_time = datetime.utcnow()
        
        # Calculate new expiry date
        if user.is_premium and user.premium_expiry and user.premium_expiry > current_time:
            # Extend from current expiry
            new_expiry = user.premium_expiry + timedelta(days=days)
        else:
            # Start from current time
            new_expiry = current_time + timedelta(days=days)
        
        # Update user
        user.is_premium = True
        user.premium_expiry = new_expiry
        await user.commit()
        
        logger.info(f"Extended premium for user {user_id} by {days} days")
        return True, f"Premium extended by {days} days"
        
    except Exception as e:
        logger.error(f"Error extending premium for user {user_id}: {e}")
        return False, f"Error: {str(e)}"

async def revoke_premium(user_id: int):
    """Revoke premium subscription for a user"""
    try:
        user = await Users.find_one({"_id": user_id})
        if not user:
            return False, "User not found"
        
        # Update user
        user.is_premium = False
        user.premium_expiry = None
        await user.commit()
        
        logger.info(f"Revoked premium for user {user_id}")
        return True, "Premium revoked successfully"
        
    except Exception as e:
        logger.error(f"Error revoking premium for user {user_id}: {e}")
        return False, f"Error: {str(e)}"

async def get_premium_plans():
    """Get available premium plans"""
    try:
        return PREMIUM_PLANS
    except Exception as e:
        logger.error(f"Error getting premium plans: {e}")
        return {}

async def check_user_premium(user_id: int):
    """Check if a user has active premium"""
    try:
        user = await Users.find_one({"_id": user_id})
        if not user:
            return False
        
        if not user.is_premium:
            return False
        
        if not user.premium_expiry:
            return False
        
        return user.premium_expiry > datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Error checking premium for user {user_id}: {e}")
        return False
