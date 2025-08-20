"""
Study Bot - Check Alive Plugin
Provides bot status checking and health monitoring
"""

import asyncio
import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import *

logger = logging.getLogger(__name__)

class BotHealthMonitor:
    """Monitor bot health and status"""
    
    def __init__(self):
        self.start_time = time.time()
        self.uptime = 0
        self.message_count = 0
        self.error_count = 0
        self.last_check = time.time()
    
    def update_stats(self, message_type: str = "message"):
        """Update bot statistics"""
        self.uptime = time.time() - self.start_time
        if message_type == "message":
            self.message_count += 1
        elif message_type == "error":
            self.error_count += 1
        self.last_check = time.time()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_used": disk.used,
                "disk_total": disk.total
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_bot_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        return {
            "uptime": self.uptime,
            "message_count": self.message_count,
            "error_count": self.error_count,
            "last_check": self.last_check,
            "start_time": self.start_time
        }
    
    def format_uptime(self) -> str:
        """Format uptime in human readable format"""
        uptime = int(self.uptime)
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

# Global health monitor instance
health_monitor = BotHealthMonitor()

# Bot commands
@Client.on_message(filters.command("alive") & filters.private)
async def alive_command(client: Client, message: Message):
    """Handle alive command"""
    try:
        # Update stats
        health_monitor.update_stats("message")
        
        # Get system info
        system_info = health_monitor.get_system_info()
        bot_stats = health_monitor.get_bot_stats()
        
        # Format response
        alive_text = "🤖 **Study Bot is Alive!**\n\n"
        alive_text += f"✅ **Status:** Online\n"
        alive_text += f"⏰ **Uptime:** {health_monitor.format_uptime()}\n"
        alive_text += f"📊 **Messages Processed:** {bot_stats['message_count']}\n"
        alive_text += f"❌ **Errors:** {bot_stats['error_count']}\n"
        alive_text += f"🕐 **Last Check:** {datetime.fromtimestamp(bot_stats['last_check']).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if system_info:
            alive_text += "💻 **System Information:**\n"
            alive_text += f"🖥️ **CPU Usage:** {system_info.get('cpu_percent', 'N/A')}%\n"
            alive_text += f"🧠 **Memory Usage:** {system_info.get('memory_percent', 'N/A')}%\n"
            alive_text += f"💾 **Disk Usage:** {system_info.get('disk_percent', 'N/A')}%\n\n"
        
        alive_text += "🚀 **Bot Features:**\n"
        alive_text += "• Dual Bot System\n"
        alive_text += "• Study Material Management\n"
        alive_text += "• Progress Tracking\n"
        alive_text += "• Admin Controls\n"
        alive_text += "• File Management\n"
        alive_text += "• Broadcasting System\n\n"
        
        alive_text += "📅 **Started:** " + datetime.fromtimestamp(bot_stats['start_time']).strftime('%Y-%m-%d %H:%M:%S')
        
        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_alive"),
                InlineKeyboardButton("📊 Stats", callback_data="show_stats")
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="show_help"),
                InlineKeyboardButton("📞 Support", callback_data="show_support")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await message.reply_text(alive_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in alive command: {e}")
        await message.reply_text(f"❌ Error checking bot status: {e}")

@Client.on_message(filters.command("ping") & filters.private)
async def ping_command(client: Client, message: Message):
    """Handle ping command"""
    try:
        # Update stats
        health_monitor.update_stats("message")
        
        start_time = time.time()
        ping_msg = await message.reply_text("🏓 Pinging...")
        end_time = time.time()
        
        ping_time = (end_time - start_time) * 1000
        
        await ping_msg.edit_text(
            f"🏓 **Pong!**\n\n"
            f"⏱️ **Response Time:** {ping_time:.2f}ms\n"
            f"🤖 **Bot Status:** Online\n"
            f"⏰ **Uptime:** {health_monitor.format_uptime()}"
        )
        
    except Exception as e:
        logger.error(f"Error in ping command: {e}")
        await message.reply_text(f"❌ Error in ping: {e}")

@Client.on_message(filters.command("status") & filters.private)
async def status_command(client: Client, message: Message):
    """Handle status command"""
    try:
        # Update stats
        health_monitor.update_stats("message")
        
        # Get system info
        system_info = health_monitor.get_system_info()
        bot_stats = health_monitor.get_bot_stats()
        
        # Format status
        status_text = "📊 **Bot Status Report**\n\n"
        
        # Bot Status
        status_text += "🤖 **Bot Information:**\n"
        status_text += f"✅ **Status:** Online\n"
        status_text += f"⏰ **Uptime:** {health_monitor.format_uptime()}\n"
        status_text += f"📊 **Messages:** {bot_stats['message_count']}\n"
        status_text += f"❌ **Errors:** {bot_stats['error_count']}\n"
        status_text += f"📈 **Success Rate:** {((bot_stats['message_count'] - bot_stats['error_count']) / max(bot_stats['message_count'], 1) * 100):.1f}%\n\n"
        
        # System Status
        if system_info:
            status_text += "💻 **System Status:**\n"
            status_text += f"🖥️ **CPU:** {system_info.get('cpu_percent', 'N/A')}%\n"
            status_text += f"🧠 **Memory:** {system_info.get('memory_percent', 'N/A')}%\n"
            status_text += f"💾 **Disk:** {system_info.get('disk_percent', 'N/A')}%\n\n"
            
            # Memory details
            memory_used = health_monitor.format_size(system_info.get('memory_used', 0))
            memory_total = health_monitor.format_size(system_info.get('memory_total', 0))
            status_text += f"🧠 **Memory Details:** {memory_used} / {memory_total}\n"
            
            # Disk details
            disk_used = health_monitor.format_size(system_info.get('disk_used', 0))
            disk_total = health_monitor.format_size(system_info.get('disk_total', 0))
            status_text += f"💾 **Disk Details:** {disk_used} / {disk_total}\n\n"
        
        # Performance indicators
        status_text += "📈 **Performance Indicators:**\n"
        if bot_stats['uptime'] > 3600:  # More than 1 hour
            status_text += "✅ **Stability:** Excellent\n"
        elif bot_stats['uptime'] > 1800:  # More than 30 minutes
            status_text += "✅ **Stability:** Good\n"
        else:
            status_text += "⚠️ **Stability:** Starting up\n"
        
        if system_info.get('cpu_percent', 0) < 50:
            status_text += "✅ **CPU Load:** Normal\n"
        elif system_info.get('cpu_percent', 0) < 80:
            status_text += "⚠️ **CPU Load:** High\n"
        else:
            status_text += "❌ **CPU Load:** Critical\n"
        
        if system_info.get('memory_percent', 0) < 70:
            status_text += "✅ **Memory Usage:** Normal\n"
        elif system_info.get('memory_percent', 0) < 90:
            status_text += "⚠️ **Memory Usage:** High\n"
        else:
            status_text += "❌ **Memory Usage:** Critical\n"
        
        await message.reply_text(status_text)
        
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await message.reply_text(f"❌ Error getting status: {e}")

@Client.on_message(filters.command("health") & filters.private)
async def health_command(client: Client, message: Message):
    """Handle health command"""
    try:
        # Check if user is admin
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ This command is only for admins!")
            return
        
        # Update stats
        health_monitor.update_stats("message")
        
        # Get system info
        system_info = health_monitor.get_system_info()
        bot_stats = health_monitor.get_bot_stats()
        
        # Health check
        health_score = 100
        health_issues = []
        
        # Check CPU usage
        if system_info.get('cpu_percent', 0) > 80:
            health_score -= 20
            health_issues.append("High CPU usage")
        elif system_info.get('cpu_percent', 0) > 50:
            health_score -= 10
            health_issues.append("Moderate CPU usage")
        
        # Check memory usage
        if system_info.get('memory_percent', 0) > 90:
            health_score -= 20
            health_issues.append("Critical memory usage")
        elif system_info.get('memory_percent', 0) > 70:
            health_score -= 10
            health_issues.append("High memory usage")
        
        # Check disk usage
        if system_info.get('disk_percent', 0) > 90:
            health_score -= 15
            health_issues.append("Critical disk usage")
        elif system_info.get('disk_percent', 0) > 80:
            health_score -= 5
            health_issues.append("High disk usage")
        
        # Check error rate
        if bot_stats['message_count'] > 0:
            error_rate = (bot_stats['error_count'] / bot_stats['message_count']) * 100
            if error_rate > 10:
                health_score -= 20
                health_issues.append("High error rate")
            elif error_rate > 5:
                health_score -= 10
                health_issues.append("Moderate error rate")
        
        # Determine health status
        if health_score >= 90:
            health_status = "🟢 Excellent"
        elif health_score >= 70:
            health_status = "🟡 Good"
        elif health_score >= 50:
            health_status = "🟠 Fair"
        else:
            health_status = "🔴 Poor"
        
        # Format health report
        health_text = "🏥 **Bot Health Report**\n\n"
        health_text += f"📊 **Health Score:** {health_score}/100\n"
        health_text += f"🏥 **Status:** {health_status}\n"
        health_text += f"⏰ **Uptime:** {health_monitor.format_uptime()}\n\n"
        
        if health_issues:
            health_text += "⚠️ **Issues Found:**\n"
            for issue in health_issues:
                health_text += f"• {issue}\n"
            health_text += "\n"
        else:
            health_text += "✅ **No issues detected**\n\n"
        
        health_text += "📈 **Recommendations:**\n"
        if health_score < 70:
            health_text += "• Monitor system resources\n"
            health_text += "• Check for memory leaks\n"
            health_text += "• Review error logs\n"
            health_text += "• Consider restarting bot\n"
        elif health_score < 90:
            health_text += "• Monitor resource usage\n"
            health_text += "• Check error patterns\n"
        else:
            health_text += "• Continue monitoring\n"
            health_text += "• Maintain current setup\n"
        
        await message.reply_text(health_text)
        
    except Exception as e:
        logger.error(f"Error in health command: {e}")
        await message.reply_text(f"❌ Error checking health: {e}")

# Callback query handlers
@Client.on_callback_query(filters.regex(r"^refresh_alive$"))
async def refresh_alive_callback(client: Client, callback_query):
    """Handle refresh alive callback"""
    try:
        # Update stats
        health_monitor.update_stats("message")
        
        # Get updated info
        system_info = health_monitor.get_system_info()
        bot_stats = health_monitor.get_bot_stats()
        
        # Format updated response
        alive_text = "🤖 **Study Bot is Alive!**\n\n"
        alive_text += f"✅ **Status:** Online\n"
        alive_text += f"⏰ **Uptime:** {health_monitor.format_uptime()}\n"
        alive_text += f"📊 **Messages Processed:** {bot_stats['message_count']}\n"
        alive_text += f"❌ **Errors:** {bot_stats['error_count']}\n"
        alive_text += f"🕐 **Last Check:** {datetime.fromtimestamp(bot_stats['last_check']).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if system_info:
            alive_text += "💻 **System Information:**\n"
            alive_text += f"🖥️ **CPU Usage:** {system_info.get('cpu_percent', 'N/A')}%\n"
            alive_text += f"🧠 **Memory Usage:** {system_info.get('memory_percent', 'N/A')}%\n"
            alive_text += f"💾 **Disk Usage:** {system_info.get('disk_percent', 'N/A')}%\n\n"
        
        alive_text += "🚀 **Bot Features:**\n"
        alive_text += "• Dual Bot System\n"
        alive_text += "• Study Material Management\n"
        alive_text += "• Progress Tracking\n"
        alive_text += "• Admin Controls\n"
        alive_text += "• File Management\n"
        alive_text += "• Broadcasting System\n\n"
        
        alive_text += "📅 **Started:** " + datetime.fromtimestamp(bot_stats['start_time']).strftime('%Y-%m-%d %H:%M:%S')
        
        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_alive"),
                InlineKeyboardButton("📊 Stats", callback_data="show_stats")
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="show_help"),
                InlineKeyboardButton("📞 Support", callback_data="show_support")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await callback_query.message.edit_text(alive_text, reply_markup=reply_markup)
        await callback_query.answer("🔄 Status refreshed!")
        
    except Exception as e:
        logger.error(f"Error in refresh alive callback: {e}")
        await callback_query.answer("❌ Error refreshing status!")

@Client.on_callback_query(filters.regex(r"^show_stats$"))
async def show_stats_callback(client: Client, callback_query):
    """Handle show stats callback"""
    try:
        # Get stats
        system_info = health_monitor.get_system_info()
        bot_stats = health_monitor.get_bot_stats()
        
        # Format stats
        stats_text = "📊 **Detailed Statistics**\n\n"
        stats_text += "🤖 **Bot Statistics:**\n"
        stats_text += f"⏰ **Uptime:** {health_monitor.format_uptime()}\n"
        stats_text += f"📊 **Total Messages:** {bot_stats['message_count']}\n"
        stats_text += f"❌ **Total Errors:** {bot_stats['error_count']}\n"
        stats_text += f"📈 **Success Rate:** {((bot_stats['message_count'] - bot_stats['error_count']) / max(bot_stats['message_count'], 1) * 100):.1f}%\n"
        stats_text += f"🕐 **Started:** {datetime.fromtimestamp(bot_stats['start_time']).strftime('%Y-%m-%d %H:%M:%S')}\n"
        stats_text += f"🔄 **Last Check:** {datetime.fromtimestamp(bot_stats['last_check']).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if system_info:
            stats_text += "💻 **System Statistics:**\n"
            stats_text += f"🖥️ **CPU Usage:** {system_info.get('cpu_percent', 'N/A')}%\n"
            stats_text += f"🧠 **Memory Usage:** {system_info.get('memory_percent', 'N/A')}%\n"
            stats_text += f"💾 **Disk Usage:** {system_info.get('disk_percent', 'N/A')}%\n\n"
            
            # Memory details
            memory_used = health_monitor.format_size(system_info.get('memory_used', 0))
            memory_total = health_monitor.format_size(system_info.get('memory_total', 0))
            stats_text += f"🧠 **Memory:** {memory_used} / {memory_total}\n"
            
            # Disk details
            disk_used = health_monitor.format_size(system_info.get('disk_used', 0))
            disk_total = health_monitor.format_size(system_info.get('disk_total', 0))
            stats_text += f"💾 **Disk:** {disk_used} / {disk_total}\n"
        
        # Add back button
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_alive")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await callback_query.message.edit_text(stats_text, reply_markup=reply_markup)
        await callback_query.answer("📊 Statistics displayed!")
        
    except Exception as e:
        logger.error(f"Error in show stats callback: {e}")
        await callback_query.answer("❌ Error showing stats!")

@Client.on_callback_query(filters.regex(r"^back_to_alive$"))
async def back_to_alive_callback(client: Client, callback_query):
    """Handle back to alive callback"""
    try:
        # Call alive command to show main status
        await alive_command(client, callback_query.message)
        await callback_query.answer("🔙 Back to main status!")
        
    except Exception as e:
        logger.error(f"Error in back to alive callback: {e}")
        await callback_query.answer("❌ Error going back!")

# Utility functions for other plugins
def update_bot_stats(message_type: str = "message"):
    """Update bot statistics"""
    health_monitor.update_stats(message_type)

def get_bot_uptime() -> str:
    """Get bot uptime"""
    return health_monitor.format_uptime()

def get_system_health() -> Dict[str, Any]:
    """Get system health information"""
    return health_monitor.get_system_info()

def is_bot_healthy() -> bool:
    """Check if bot is healthy"""
    system_info = health_monitor.get_system_info()
    
    # Basic health checks
    if system_info.get('cpu_percent', 0) > 90:
        return False
    if system_info.get('memory_percent', 0) > 95:
        return False
    if system_info.get('disk_percent', 0) > 95:
        return False
    
    return True
