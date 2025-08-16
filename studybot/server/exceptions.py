class StudyBotException(Exception):
    """Base exception for Study Bot"""
    pass

class DatabaseError(StudyBotException):
    """Database operation error"""
    pass

class AuthenticationError(StudyBotException):
    """Authentication/authorization error"""
    pass

class FileUploadError(StudyBotException):
    """File upload error"""
    pass

class ContentNotFoundError(StudyBotException):
    """Content not found error"""
    pass

class RateLimitError(StudyBotException):
    """Rate limit exceeded error"""
    pass

class ConfigurationError(StudyBotException):
    """Configuration error"""
    pass

class NetworkError(StudyBotException):
    """Network/connection error"""
    pass

class ValidationError(StudyBotException):
    """Data validation error"""
    pass

class PermissionError(StudyBotException):
    """Permission denied error"""
    pass

class BotError(StudyBotException):
    """Bot operation error"""
    pass
