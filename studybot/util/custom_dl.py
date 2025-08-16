import os
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from urllib.parse import urlparse

class CustomDownloader:
    """Custom downloader with progress tracking and resume support"""
    
    def __init__(self, download_dir: str = "downloads"):
        """
        Initialize custom downloader
        
        Args:
            download_dir (str): Directory to save downloads
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.active_downloads = {}
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def download_file(
        self,
        url: str,
        filename: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        resume: bool = True,
        chunk_size: int = 8192
    ) -> Dict[str, Any]:
        """
        Download a file with progress tracking
        
        Args:
            url (str): URL to download from
            filename (str, optional): Custom filename
            progress_callback (callable, optional): Progress callback function
            resume (bool): Enable resume support
            chunk_size (int): Download chunk size
            
        Returns:
            Dict[str, Any]: Download result information
        """
        if not self.session:
            raise RuntimeError("Downloader not initialized. Use async context manager.")
        
        # Parse URL and determine filename
        parsed_url = urlparse(url)
        if not filename:
            filename = os.path.basename(parsed_url.path) or "download"
        
        file_path = self.download_dir / filename
        
        # Check if file exists and resume is enabled
        existing_size = 0
        if resume and file_path.exists():
            existing_size = file_path.stat().st_size
        
        try:
            headers = {}
            if resume and existing_size > 0:
                headers['Range'] = f'bytes={existing_size}-'
            
            async with self.session.get(url, headers=headers) as response:
                if response.status not in [200, 206]:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status}: {response.reason}',
                        'file_path': str(file_path)
                    }
                
                total_size = int(response.headers.get('content-length', 0))
                if resume and existing_size > 0:
                    total_size += existing_size
                
                # Track download progress
                downloaded_size = existing_size
                start_time = asyncio.get_event_loop().time()
                
                # Open file for writing
                mode = 'ab' if resume and existing_size > 0 else 'wb'
                async with aiofiles.open(file_path, mode) as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Call progress callback if provided
                        if progress_callback and total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            speed = downloaded_size / (asyncio.get_event_loop().time() - start_time)
                            await progress_callback(progress, downloaded_size, total_size, speed)
                
                # Verify download
                final_size = file_path.stat().st_size
                if total_size > 0 and final_size != total_size:
                    return {
                        'success': False,
                        'error': f'Size mismatch: expected {total_size}, got {final_size}',
                        'file_path': str(file_path)
                    }
                
                return {
                    'success': True,
                    'file_path': str(file_path),
                    'filename': filename,
                    'size': final_size,
                    'url': url,
                    'download_time': asyncio.get_event_loop().time() - start_time
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }
    
    async def download_multiple(
        self,
        urls: list,
        progress_callback: Optional[Callable] = None,
        max_concurrent: int = 3
    ) -> Dict[str, Any]:
        """
        Download multiple files concurrently
        
        Args:
            urls (list): List of URLs to download
            progress_callback (callable, optional): Progress callback function
            max_concurrent (int): Maximum concurrent downloads
            
        Returns:
            Dict[str, Any]: Download results summary
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(url):
            async with semaphore:
                return await self.download_file(url, progress_callback=progress_callback)
        
        tasks = [download_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = []
        failed = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({
                    'url': urls[i],
                    'error': str(result)
                })
            elif result['success']:
                successful.append(result)
            else:
                failed.append(result)
        
        return {
            'total': len(urls),
            'successful': len(successful),
            'failed': len(failed),
            'results': results,
            'successful_downloads': successful,
            'failed_downloads': failed
        }
    
    def get_download_progress(self, download_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress of a specific download
        
        Args:
            download_id (str): Download identifier
            
        Returns:
            Dict[str, Any]: Download progress information
        """
        return self.active_downloads.get(download_id)
    
    def cancel_download(self, download_id: str) -> bool:
        """
        Cancel an active download
        
        Args:
            download_id (str): Download identifier
            
        Returns:
            bool: True if download was cancelled
        """
        if download_id in self.active_downloads:
            download_info = self.active_downloads[download_id]
            download_info['cancelled'] = True
            return True
        return False
    
    def cleanup_incomplete_downloads(self) -> int:
        """
        Clean up incomplete downloads
        
        Returns:
            int: Number of files cleaned up
        """
        cleaned = 0
        for file_path in self.download_dir.glob("*.part"):
            try:
                file_path.unlink()
                cleaned += 1
            except OSError:
                pass
        return cleaned

async def download_with_progress(
    url: str,
    filename: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Convenience function for downloading with progress
    
    Args:
        url (str): URL to download
        filename (str, optional): Custom filename
        progress_callback (callable, optional): Progress callback
        
    Returns:
        Dict[str, Any]: Download result
    """
    async with CustomDownloader() as downloader:
        return await downloader.download_file(url, filename, progress_callback)

async def download_multiple_files(
    urls: list,
    progress_callback: Optional[Callable] = None,
    max_concurrent: int = 3
) -> Dict[str, Any]:
    """
    Convenience function for downloading multiple files
    
    Args:
        urls (list): List of URLs
        progress_callback (callable, optional): Progress callback
        max_concurrent (int): Maximum concurrent downloads
        
    Returns:
        Dict[str, Any]: Download results
    """
    async with CustomDownloader() as downloader:
        return await downloader.download_multiple(urls, progress_callback, max_concurrent)

def create_progress_callback(update_interval: float = 1.0) -> Callable:
    """
    Create a progress callback function
    
    Args:
        update_interval (float): Minimum interval between updates in seconds
        
    Returns:
        Callable: Progress callback function
    """
    last_update = 0
    
    async def progress_callback(progress: float, downloaded: int, total: int, speed: float):
        nonlocal last_update
        current_time = asyncio.get_event_loop().time()
        
        if current_time - last_update >= update_interval:
            # Format progress information
            progress_str = f"{progress:.1f}%"
            downloaded_str = human_readable_size(downloaded)
            total_str = human_readable_size(total)
            speed_str = human_readable_size(int(speed)) + "/s"
            
            # Print or log progress
            print(f"Download Progress: {progress_str} | {downloaded_str}/{total_str} | {speed_str}")
            
            last_update = current_time
    
    return progress_callback

def human_readable_size(size_bytes: int) -> str:
    """
    Convert bytes to human readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Human readable size string
    """
    from .human_readable import humanbytes
    return humanbytes(size_bytes)
