import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Document, fields
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance
from typing import Optional, List, Dict, Any
from datetime import datetime

# Try to import configuration
try:
    from config import DATABASE_URI, DATABASE_NAME
except ImportError:
    # Fallback configuration
    DATABASE_URI = "mongodb://localhost:27017"
    DATABASE_NAME = "study_bot"

# Initialize Motor instance with proper error handling
try:
    motor_client = AsyncIOMotorClient(DATABASE_URI)
    db = motor_client[DATABASE_NAME]
    instance = MotorAsyncIOInstance(db)
except Exception as e:
    print(f"Warning: Could not initialize database connection in refer.py: {e}")
    motor_client = None
    db = None
    instance = None

# Only register document classes if instance is available
if instance:
    @instance.register
    class Referral(Document):
        """Referral model for tracking user referrals"""
        
        referrer_id = fields.IntegerField(required=True, index=True)
        referred_id = fields.IntegerField(required=True, unique=True, index=True)
        referrer_name = fields.StringField(required=True)
        referred_name = fields.StringField(required=True)
        referrer_username = fields.StringField()
        referred_username = fields.StringField()
        referral_code = fields.StringField(required=True, unique=True, index=True)
        status = fields.StringField(default_factory=lambda: "pending", choices=["pending", "completed", "expired"])
        bonus_claimed = fields.BooleanField(default_factory=lambda: False)
        bonus_amount = fields.IntegerField(default_factory=lambda: 0)
        created_at = fields.DateTimeField(default_factory=datetime.utcnow)
        completed_at = fields.DateTimeField()
        expires_at = fields.DateTimeField()
        
        class Meta:
            collection_name = "referrals"
            indexes = [
                "referrer_id",
                "referred_id", 
                "referral_code",
                "status"
            ]

    @instance.register
    class ReferralCode(Document):
        """Referral code model for generating and managing codes"""
        
        user_id = fields.IntegerField(required=True, unique=True, index=True)
        username = fields.StringField()
        referral_code = fields.StringField(required=True, unique=True, index=True)
        is_active = fields.BooleanField(default_factory=lambda: True)
        max_uses = fields.IntegerField(default_factory=lambda: -1)  # -1 means unlimited
        current_uses = fields.IntegerField(default_factory=lambda: 0)
        bonus_per_referral = fields.IntegerField(default_factory=lambda: 100)
        created_at = fields.DateTimeField(default_factory=datetime.utcnow)
        last_used = fields.DateTimeField()
        
        class Meta:
            collection_name = "referral_codes"
            indexes = [
                "user_id",
                "referral_code",
                "is_active"
            ]

    @instance.register
    class ReferralBonus(Document):
        """Referral bonus model for tracking bonuses"""
        
        user_id = fields.IntegerField(required=True, index=True)
        referral_id = fields.ReferenceField(Referral, required=True)
        bonus_amount = fields.IntegerField(required=True)
        bonus_type = fields.StringField(default_factory=lambda: "referral", choices=["referral", "signup", "activity"])
        status = fields.StringField(default_factory=lambda: "pending", choices=["pending", "credited", "expired"])
        credited_at = fields.DateTimeField()
        expires_at = fields.DateTimeField()
        created_at = fields.DateTimeField(default_factory=datetime.utcnow)
        
        class Meta:
            collection_name = "referral_bonuses"
            indexes = [
                "user_id",
                "referral_id",
                "status"
            ]
else:
    # Placeholder classes when database is not available
    class Referral:
        pass
    
    class ReferralCode:
        pass
    
    class ReferralBonus:
        pass

class ReferralManager:
    """Manager class for referral operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        if db_instance:
            self.referrals = db_instance.referrals
            self.referral_codes = db_instance.referral_codes
            self.referral_bonuses = db_instance.referral_bonuses
        else:
            self.referrals = None
            self.referral_codes = None
            self.referral_bonuses = None
    
    async def create_referral_code(self, user_id: int, username: str = None) -> Optional[str]:
        """Create a new referral code for a user"""
        if not self.db:
            print("Database not available")
            return None
            
        try:
            # Check if user already has a referral code
            existing = await self.referral_codes.find_one({"user_id": user_id})
            if existing:
                return existing["referral_code"]
            
            # Generate unique referral code
            import random
            import string
            
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not await self.referral_codes.find_one({"referral_code": code}):
                    break
            
            # Create referral code document
            referral_code_doc = ReferralCode(
                user_id=user_id,
                username=username,
                referral_code=code
            )
            await referral_code_doc.commit()
            
            return code
            
        except Exception as e:
            print(f"Error creating referral code: {e}")
            return None
    
    async def get_referral_code(self, user_id: int) -> Optional[str]:
        """Get referral code for a user"""
        if not self.db:
            print("Database not available")
            return None
            
        try:
            doc = await self.referral_codes.find_one({"user_id": user_id, "is_active": True})
            return doc["referral_code"] if doc else None
        except Exception as e:
            print(f"Error getting referral code: {e}")
            return None
    
    async def validate_referral_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Validate a referral code"""
        if not self.db:
            print("Database not available")
            return None
            
        try:
            doc = await self.referral_codes.find_one({
                "referral_code": code,
                "is_active": True
            })
            
            if not doc:
                return None
            
            # Check if max uses reached
            if doc["max_uses"] > 0 and doc["current_uses"] >= doc["max_uses"]:
                return None
            
            return {
                "user_id": doc["user_id"],
                "username": doc["username"],
                "bonus_per_referral": doc["bonus_per_referral"]
            }
            
        except Exception as e:
            print(f"Error validating referral code: {e}")
            return None
    
    async def create_referral(self, referrer_id: int, referred_id: int, 
                             referrer_name: str, referred_name: str,
                             referrer_username: str = None, referred_username: str = None) -> bool:
        """Create a new referral"""
        if not self.db:
            print("Database not available")
            return False
            
        try:
            # Check if user was already referred
            existing = await self.referrals.find_one({"referred_id": referred_id})
            if existing:
                return False
            
            # Get referral code
            referral_code = await self.get_referral_code(referrer_id)
            if not referral_code:
                return False
            
            # Create referral document
            referral_doc = Referral(
                referrer_id=referrer_id,
                referred_id=referred_id,
                referrer_name=referrer_name,
                referred_name=referred_name,
                referrer_username=referrer_username,
                referred_username=referred_username,
                referral_code=referral_code
            )
            await referral_doc.commit()
            
            # Update referral code usage
            await self.referral_codes.update_one(
                {"referral_code": referral_code},
                {"$inc": {"current_uses": 1}, "$set": {"last_used": datetime.utcnow()}}
            )
            
            return True
            
        except Exception as e:
            print(f"Error creating referral: {e}")
            return False
    
    async def complete_referral(self, referred_id: int) -> bool:
        """Mark a referral as completed"""
        if not self.db:
            print("Database not available")
            return False
            
        try:
            referral = await self.referrals.find_one({"referred_id": referred_id})
            if not referral:
                return False
            
            # Update referral status
            await self.referrals.update_one(
                {"referred_id": referred_id},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            # Create bonus for referrer
            bonus_doc = ReferralBonus(
                user_id=referral["referrer_id"],
                referral_id=referral["_id"],
                bonus_amount=referral.get("bonus_amount", 100),
                status="pending"
            )
            await bonus_doc.commit()
            
            return True
            
        except Exception as e:
            print(f"Error completing referral: {e}")
            return False
    
    async def get_user_referrals(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all referrals for a user"""
        if not self.db:
            print("Database not available")
            return []
            
        try:
            cursor = self.referrals.find({"referrer_id": user_id})
            referrals = await cursor.to_list(length=None)
            
            result = []
            for referral in referrals:
                result.append({
                    "referred_id": referral["referred_id"],
                    "referred_name": referral["referred_name"],
                    "referred_username": referral.get("referred_username"),
                    "status": referral["status"],
                    "created_at": referral["created_at"],
                    "completed_at": referral.get("completed_at")
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting user referrals: {e}")
            return []
    
    async def get_referral_stats(self, user_id: int) -> Dict[str, Any]:
        """Get referral statistics for a user"""
        if not self.db:
            print("Database not available")
            return {}
            
        try:
            total_referrals = await self.referrals.count_documents({"referrer_id": user_id})
            completed_referrals = await self.referrals.count_documents({
                "referrer_id": user_id,
                "status": "completed"
            })
            pending_referrals = await self.referrals.count_documents({
                "referrer_id": user_id,
                "status": "pending"
            })
            
            # Calculate total bonus earned
            total_bonus = 0
            cursor = self.referral_bonuses.find({
                "user_id": user_id,
                "status": "credited"
            })
            bonuses = await cursor.to_list(length=None)
            for bonus in bonuses:
                total_bonus += bonus["bonus_amount"]
            
            return {
                "total_referrals": total_referrals,
                "completed_referrals": completed_referrals,
                "pending_referrals": pending_referrals,
                "total_bonus": total_bonus,
                "referral_code": await self.get_referral_code(user_id)
            }
            
        except Exception as e:
            print(f"Error getting referral stats: {e}")
            return {}
    
    async def claim_bonus(self, user_id: int, bonus_id: str) -> bool:
        """Claim a referral bonus"""
        if not self.db:
            print("Database not available")
            return False
            
        try:
            bonus = await self.referral_bonuses.find_one({"_id": bonus_id, "user_id": user_id})
            if not bonus or bonus["status"] != "pending":
                return False
            
            # Update bonus status
            await self.referral_bonuses.update_one(
                {"_id": bonus_id},
                {
                    "$set": {
                        "status": "credited",
                        "credited_at": datetime.utcnow()
                    }
                }
            )
            
            # Update referral bonus claimed
            await self.referrals.update_one(
                {"_id": bonus["referral_id"]},
                {"$set": {"bonus_claimed": True}}
            )
            
            return True
            
        except Exception as e:
            print(f"Error claiming bonus: {e}")
            return False

# Global referral manager instance
referral_manager = ReferralManager(db)

# Convenience functions
async def create_referral_code(user_id: int, username: str = None) -> Optional[str]:
    """Create referral code for user"""
    return await referral_manager.create_referral_code(user_id, username)

async def get_referral_code(user_id: int) -> Optional[str]:
    """Get referral code for user"""
    return await referral_manager.get_referral_code(user_id)

async def validate_referral_code(code: str) -> Optional[Dict[str, Any]]:
    """Validate referral code"""
    return await referral_manager.validate_referral_code(code)

async def create_referral(referrer_id: int, referred_id: int,
                         referrer_name: str, referred_name: str,
                         referrer_username: str = None, referred_username: str = None) -> bool:
    """Create new referral"""
    return await referral_manager.create_referral(
        referrer_id, referred_id, referrer_name, referred_name,
        referrer_username, referred_username
    )

async def complete_referral(referred_id: int) -> bool:
    """Complete referral"""
    return await referral_manager.complete_referral(referred_id)

async def get_user_referrals(user_id: int) -> List[Dict[str, Any]]:
    """Get user referrals"""
    return await referral_manager.get_user_referrals(user_id)

async def get_referral_stats(user_id: int) -> Dict[str, Any]:
    """Get referral statistics"""
    return await referral_manager.get_referral_stats(user_id)

async def claim_bonus(user_id: int, bonus_id: str) -> bool:
    """Claim referral bonus"""
    return await referral_manager.claim_bonus(user_id, bonus_id)
