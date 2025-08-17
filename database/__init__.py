"""
Study Bot Database Package
Contains all database models and utilities
"""

# Import database modules with error handling
try:
    from .study_db import *
except Exception as e:
    print(f"Warning: Could not import study_db: {e}")

try:
    from .config_db import *
except Exception as e:
    print(f"Warning: Could not import config_db: {e}")

try:
    from .topdb import *
except Exception as e:
    print(f"Warning: Could not import topdb: {e}")

try:
    from .users_chats_db import *
except Exception as e:
    print(f"Warning: Could not import users_chats_db: {e}")

try:
    from .ia_filterdb import *
except Exception as e:
    print(f"Warning: Could not import ia_filterdb: {e}")

try:
    from .refer import *
except Exception as e:
    print(f"Warning: Could not import refer: {e}")

__all__ = [
    'study_db',
    'config_db', 
    'topdb',
    'users_chats_db',
    'ia_filterdb',
    'refer'
]
