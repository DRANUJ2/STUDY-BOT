"""
Study Bot - Telegraph Plugin
Provides Telegraph integration for creating and managing pages
"""

import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Any, List
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

class TelegraphAPI:
    """Telegraph API wrapper"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Telegraph API
        
        Args:
            access_token (str, optional): Access token for authenticated requests
        """
        self.access_token = access_token
        self.base_url = "https://api.telegra.ph"
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def create_account(self, short_name: str, author_name: str = "", 
                           author_url: str = "") -> Optional[Dict[str, Any]]:
        """
        Create a new Telegraph account
        
        Args:
            short_name (str): Short name for the account
            author_name (str): Author name
            author_url (str): Author URL
            
        Returns:
            Dict[str, Any]: Account information
        """
        try:
            data = {
                "short_name": short_name,
                "author_name": author_name,
                "author_url": author_url
            }
            
            async with self.session.post(f"{self.base_url}/createAccount", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        return result.get("result")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Telegraph account: {e}")
            return None
    
    async def create_page(self, title: str, content: str, author_name: str = "",
                         author_url: str = "", return_content: bool = False) -> Optional[Dict[str, Any]]:
        """
        Create a new Telegraph page
        
        Args:
            title (str): Page title
            content (str): Page content in HTML format
            author_name (str): Author name
            author_url (str): Author URL
            return_content (bool): Return content in response
            
        Returns:
            Dict[str, Any]: Page information
        """
        try:
            data = {
                "title": title,
                "content": content,
                "author_name": author_name,
                "author_url": author_url,
                "return_content": return_content
            }
            
            if self.access_token:
                data["access_token"] = self.access_token
            
            async with self.session.post(f"{self.base_url}/createPage", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        return result.get("result")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Telegraph page: {e}")
            return None
    
    async def edit_page(self, path: str, title: str, content: str,
                       author_name: str = "", author_url: str = "",
                       return_content: bool = False) -> Optional[Dict[str, Any]]:
        """
        Edit an existing Telegraph page
        
        Args:
            path (str): Page path
            title (str): New page title
            content (str): New page content
            author_name (str): Author name
            author_url (str): Author URL
            return_content (bool): Return content in response
            
        Returns:
            Dict[str, Any]: Updated page information
        """
        try:
            data = {
                "path": path,
                "title": title,
                "content": content,
                "author_name": author_name,
                "author_url": author_url,
                "return_content": return_content
            }
            
            if self.access_token:
                data["access_token"] = self.access_token
            
            async with self.session.post(f"{self.base_url}/editPage", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        return result.get("result")
                return None
                
        except Exception as e:
            logger.error(f"Error editing Telegraph page: {e}")
            return None
    
    async def get_page(self, path: str, return_content: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get Telegraph page information
        
        Args:
            path (str): Page path
            return_content (bool): Return content in response
            
        Returns:
            Dict[str, Any]: Page information
        """
        try:
            params = {"path": path}
            if return_content:
                params["return_content"] = "true"
            
            async with self.session.get(f"{self.base_url}/getPage", params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        return result.get("result")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Telegraph page: {e}")
            return None
    
    async def get_page_list(self, offset: int = 0, limit: int = 50) -> Optional[Dict[str, Any]]:
        """
        Get list of pages for an account
        
        Args:
            offset (int): Offset for pagination
            limit (int): Number of pages to return
            
        Returns:
            Dict[str, Any]: Page list information
        """
        try:
            if not self.access_token:
                return None
            
            params = {
                "access_token": self.access_token,
                "offset": offset,
                "limit": limit
            }
            
            async with self.session.get(f"{self.base_url}/getPageList", params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        return result.get("result")
                return None
                
        except Exception as e:
            logger.error(f"Error getting page list: {e}")
            return None
    
    async def get_views(self, path: str) -> Optional[int]:
        """
        Get page view count
        
        Args:
            path (str): Page path
            
        Returns:
            int: View count
        """
        try:
            params = {"path": path}
            
            async with self.session.get(f"{self.base_url}/getViews", params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        return result.get("result", {}).get("views", 0)
                return 0
                
        except Exception as e:
            logger.error(f"Error getting page views: {e}")
            return 0

def create_html_content(title: str, content: str, author: str = "") -> str:
    """
    Create HTML content for Telegraph
    
    Args:
        title (str): Page title
        content (str): Page content
        author (str): Author name
        
    Returns:
        str: Formatted HTML content
    """
    html = f"""
    <h1>{title}</h1>
    """
    
    if author:
        html += f'<p><em>By {author}</em></p>'
    
    html += f"""
    <hr>
    {content}
    """
    
    return html

def format_content_for_telegraph(content: str) -> str:
    """
    Format content for Telegraph (convert markdown-like syntax to HTML)
    
    Args:
        content (str): Raw content
        
    Returns:
        str: HTML formatted content
    """
    # Convert markdown-like syntax to HTML
    content = content.replace("**", "<strong>").replace("**", "</strong>")
    content = content.replace("*", "<em>").replace("*", "</em>")
    content = content.replace("`", "<code>").replace("`", "</code>")
    
    # Convert line breaks to paragraphs
    paragraphs = content.split('\n\n')
    formatted_paragraphs = []
    
    for para in paragraphs:
        if para.strip():
            # Handle lists
            if para.strip().startswith('- '):
                lines = para.strip().split('\n')
                list_items = []
                for line in lines:
                    if line.strip().startswith('- '):
                        item = line.strip()[2:]  # Remove '- '
                        list_items.append(f"<li>{item}</li>")
                if list_items:
                    formatted_paragraphs.append(f"<ul>{''.join(list_items)}</ul>")
            else:
                formatted_paragraphs.append(f"<p>{para.strip()}</p>")
    
    return '\n'.join(formatted_paragraphs)

# Bot commands
@Client.on_message(filters.command("telegraph") & filters.private)
async def telegraph_command(client: Client, message: Message):
    """Handle telegraph command"""
    try:
        # Check if user is admin
        from config import ADMINS
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ This command is only for admins!")
            return
        
        # Parse command arguments
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply_text(
                "❌ **Usage:** `/telegraph <title> <content>`\n\n"
                "**Example:** `/telegraph 'My Page' This is the content of my page.`"
            )
            return
        
        title = args[1]
        content = args[2]
        
        # Format content
        formatted_content = format_content_for_telegraph(content)
        html_content = create_html_content(title, formatted_content, message.from_user.first_name)
        
        # Create Telegraph page
        async with TelegraphAPI() as telegraph:
            page_info = await telegraph.create_page(
                title=title,
                content=html_content,
                author_name=message.from_user.first_name
            )
            
            if page_info:
                page_url = f"https://telegra.ph{page_info['path']}"
                await message.reply_text(
                    f"✅ **Telegraph Page Created!**\n\n"
                    f"📝 **Title:** {title}\n"
                    f"🔗 **URL:** {page_url}\n"
                    f"👤 **Author:** {message.from_user.first_name}\n"
                    f"📊 **Views:** {page_info.get('views', 0)}"
                )
            else:
                await message.reply_text("❌ Failed to create Telegraph page!")
                
    except Exception as e:
        logger.error(f"Error in telegraph command: {e}")
        await message.reply_text(f"❌ Error creating Telegraph page: {e}")

@Client.on_message(filters.command("telegraph_edit") & filters.private)
async def telegraph_edit_command(client: Client, message: Message):
    """Handle telegraph edit command"""
    try:
        # Check if user is admin
        from config import ADMINS
        if message.from_user.id not in ADMINS:
            await message.reply_text("❌ This command is only for admins!")
            return
        
        # Parse command arguments
        args = message.text.split(maxsplit=3)
        if len(args) < 4:
            await message.reply_text(
                "❌ **Usage:** `/telegraph_edit <path> <title> <content>`\n\n"
                "**Example:** `/telegraph_edit my-page 'New Title' New content here.`"
            )
            return
        
        path = args[1]
        title = args[2]
        content = args[3]
        
        # Format content
        formatted_content = format_content_for_telegraph(content)
        html_content = create_html_content(title, formatted_content, message.from_user.first_name)
        
        # Edit Telegraph page
        async with TelegraphAPI() as telegraph:
            page_info = await telegraph.edit_page(
                path=path,
                title=title,
                content=html_content,
                author_name=message.from_user.first_name
            )
            
            if page_info:
                page_url = f"https://telegra.ph{page_info['path']}"
                await message.reply_text(
                    f"✅ **Telegraph Page Updated!**\n\n"
                    f"📝 **Title:** {title}\n"
                    f"🔗 **URL:** {page_url}\n"
                    f"👤 **Author:** {message.from_user.first_name}\n"
                    f"📊 **Views:** {page_info.get('views', 0)}"
                )
            else:
                await message.reply_text("❌ Failed to update Telegraph page!")
                
    except Exception as e:
        logger.error(f"Error in telegraph edit command: {e}")
        await message.reply_text(f"❌ Error updating Telegraph page: {e}")

@Client.on_message(filters.command("telegraph_info") & filters.private)
async def telegraph_info_command(client: Client, message: Message):
    """Handle telegraph info command"""
    try:
        # Parse command arguments
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text(
                "❌ **Usage:** `/telegraph_info <path>`\n\n"
                "**Example:** `/telegraph_info my-page`"
            )
            return
        
        path = args[1]
        
        # Get Telegraph page info
        async with TelegraphAPI() as telegraph:
            page_info = await telegraph.get_page(path, return_content=True)
            views = await telegraph.get_views(path)
            
            if page_info:
                page_url = f"https://telegra.ph{page_info['path']}"
                await message.reply_text(
                    f"📄 **Telegraph Page Info**\n\n"
                    f"📝 **Title:** {page_info.get('title', 'Unknown')}\n"
                    f"🔗 **URL:** {page_url}\n"
                    f"👤 **Author:** {page_info.get('author_name', 'Unknown')}\n"
                    f"📊 **Views:** {views}\n"
                    f"📅 **Created:** {page_info.get('created', 'Unknown')}\n"
                    f"📏 **Content Length:** {len(page_info.get('content', ''))} characters"
                )
            else:
                await message.reply_text("❌ Page not found!")
                
    except Exception as e:
        logger.error(f"Error in telegraph info command: {e}")
        await message.reply_text(f"❌ Error getting page info: {e}")

# Utility functions for other plugins
async def create_telegraph_page(title: str, content: str, author_name: str = "") -> Optional[str]:
    """
    Create a Telegraph page and return URL
    
    Args:
        title (str): Page title
        content (str): Page content
        author_name (str): Author name
        
    Returns:
        str: Page URL if successful, None otherwise
    """
    try:
        formatted_content = format_content_for_telegraph(content)
        html_content = create_html_content(title, formatted_content, author_name)
        
        async with TelegraphAPI() as telegraph:
            page_info = await telegraph.create_page(
                title=title,
                content=html_content,
                author_name=author_name
            )
            
            if page_info:
                return f"https://telegra.ph{page_info['path']}"
            return None
            
    except Exception as e:
        logger.error(f"Error creating Telegraph page: {e}")
        return None

async def update_telegraph_page(path: str, title: str, content: str, 
                              author_name: str = "") -> Optional[str]:
    """
    Update a Telegraph page and return URL
    
    Args:
        path (str): Page path
        title (str): New title
        content (str): New content
        author_name (str): Author name
        
    Returns:
        str: Page URL if successful, None otherwise
    """
    try:
        formatted_content = format_content_for_telegraph(content)
        html_content = create_html_content(title, formatted_content, author_name)
        
        async with TelegraphAPI() as telegraph:
            page_info = await telegraph.edit_page(
                path=path,
                title=title,
                content=html_content,
                author_name=author_name
            )
            
            if page_info:
                return f"https://telegra.ph{page_info['path']}"
            return None
            
    except Exception as e:
        logger.error(f"Error updating Telegraph page: {e}")
        return None
