"""
Study Bot - Logging Helper Module
Provides enhanced logging functionality for the bot
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

class StudyBotLogger:
    """Enhanced logger for Study Bot"""
    
    def __init__(self, name: str = "StudyBot", log_dir: str = "logs"):
        """
        Initialize Study Bot Logger
        
        Args:
            name (str): Logger name
            log_dir (str): Directory for log files
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Make sure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # File handler for all logs
        all_log_file = self.log_dir / "study_bot.log"
        file_handler = logging.handlers.RotatingFileHandler(
            str(all_log_file),  # Convert Path to string
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Error log handler
        error_log_file = self.log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            str(error_log_file),  # Convert Path to string
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8',
            mode='a'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s\n'
            'Exception: %(exc_info)s\n'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
        
        # Access log handler
        access_log_file = self.log_dir / "access.log"
        access_handler = logging.handlers.RotatingFileHandler(
            str(access_log_file),  # Convert Path to string
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8',
            mode='a'
        )
        access_handler.setLevel(logging.INFO)
        access_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        access_handler.setFormatter(access_formatter)
        self.logger.addHandler(access_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception message"""
        self.logger.exception(message, *args, **kwargs)
    
    def log_user_action(self, user_id: int, action: str, details: str = ""):
        """Log user actions"""
        message = f"User {user_id} - {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_bot_action(self, action: str, details: str = ""):
        """Log bot actions"""
        message = f"Bot Action - {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context"""
        message = f"Error in {context}: {str(error)}"
        self.logger.error(message, exc_info=True)
    
    def log_performance(self, operation: str, duration: float, details: str = ""):
        """Log performance metrics"""
        message = f"Performance - {operation}: {duration:.3f}s"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_security(self, event: str, user_id: int = None, details: str = ""):
        """Log security events"""
        message = f"Security - {event}"
        if user_id:
            message += f" - User: {user_id}"
        if details:
            message += f" - {details}"
        self.logger.warning(message)

class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class StructuredFormatter(logging.Formatter):
    """Structured formatter for JSON-like output"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName', 'process',
                          'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return str(log_entry)

def setup_logging(name: str = "StudyBot", level: str = "INFO", 
                 log_dir: str = "logs", colored: bool = True,
                 structured: bool = False) -> StudyBotLogger:
    """
    Setup logging for Study Bot
    
    Args:
        name (str): Logger name
        level (str): Logging level
        log_dir (str): Directory for log files
        colored (bool): Enable colored console output
        structured (bool): Enable structured logging
        
    Returns:
        StudyBotLogger: Configured logger instance
    """
    # Set root logging level
    logging.basicConfig(level=getattr(logging, level.upper()))
    
    # Create logger
    logger = StudyBotLogger(name, log_dir)
    
    # Configure console handler with colors if requested
    if colored:
        for handler in logger.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setFormatter(ColoredFormatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
    
    # Configure structured logging if requested
    if structured:
        for handler in logger.logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.setFormatter(StructuredFormatter())
    
    return logger

def get_logger(name: str = "StudyBot") -> StudyBotLogger:
    """
    Get existing logger or create new one
    
    Args:
        name (str): Logger name
        
    Returns:
        StudyBotLogger: Logger instance
    """
    return StudyBotLogger(name)

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {e}", exc_info=True)
            raise
    return wrapper

def log_async_function_call(func):
    """Decorator to log async function calls"""
    async def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Async function {func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Async function {func.__name__} failed: {e}", exc_info=True)
            raise
    return wrapper

# Global logger instance
study_bot_logger = StudyBotLogger()

# Convenience functions
def debug(message: str, *args, **kwargs):
    """Log debug message using global logger"""
    study_bot_logger.debug(message, *args, **kwargs)

def info(message: str, *args, **kwargs):
    """Log info message using global logger"""
    study_bot_logger.info(message, *args, **kwargs)

def warning(message: str, *args, **kwargs):
    """Log warning message using global logger"""
    study_bot_logger.warning(message, *args, **kwargs)

def error(message: str, *args, **kwargs):
    """Log error message using global logger"""
    study_bot_logger.error(message, *args, **kwargs)

def critical(message: str, *args, **kwargs):
    """Log critical message using global logger"""
    study_bot_logger.critical(message, *args, **kwargs)

def exception(message: str, *args, **kwargs):
    """Log exception message using global logger"""
    study_bot_logger.exception(message, *args, **kwargs)

def log_user_action(user_id: int, action: str, details: str = ""):
    """Log user action using global logger"""
    study_bot_logger.log_user_action(user_id, action, details)

def log_bot_action(action: str, details: str = ""):
    """Log bot action using global logger"""
    study_bot_logger.log_bot_action(action, details)

def log_error(error: Exception, context: str = ""):
    """Log error using global logger"""
    study_bot_logger.log_error(error, context)

def log_performance(operation: str, duration: float, details: str = ""):
    """Log performance using global logger"""
    study_bot_logger.log_performance(operation, duration, details)

def log_security(event: str, user_id: int = None, details: str = ""):
    """Log security event using global logger"""
    study_bot_logger.log_security(event, user_id, details)
