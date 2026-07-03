import asyncio
import aiohttp
import time
import logging
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse

from app.config import config
from app.fetcher.headers import HeaderManager


logger = logging.getLogger(__name__)


class HTTPFetcher:
    """HTTP fetcher using aiohttp for async requests"""
    
    def __init__(self):
        self.header_manager = HeaderManager()
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_timeout = aiohttp.ClientTimeout(total=config.timeout)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def start_session(self):
        """Start the aiohttp session"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=config.max_concurrent_requests,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self._session_timeout,
                headers=self.header_manager.get_random_headers()
            )
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch(self, url: str, referer: Optional[str] = None, **kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Fetch a URL and return content and metadata"""
        
        if not self.session or self.session.closed:
            await self.start_session()
        
        try:
            headers = self.header_manager.get_random_headers(referer)
            
            # Override with custom headers if provided
            if 'headers' in kwargs:
                headers.update(kwargs.pop('headers'))
            
            async with self.session.get(url, headers=headers, **kwargs) as response:
                content = await self.read_content(response)
                
                metadata = {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'content_type': response.content_type,
                    'url': str(response.url),
                    'final_url': str(response.url),
                    'redirect_count': len(response.history),
                    'size': len(content) if content else 0,
                    'fetched_at': time.time(),
                }
                
                logger.debug(f"Fetched {url} (status: {response.status}, size: {metadata['size']})")
                
                return content, metadata
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url}")
            return None, {'error': 'timeout', 'url': url}
        except aiohttp.ClientError as e:
            logger.warning(f"Client error fetching {url}: {e}")
            return None, {'error': str(e), 'url': url}
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None, {'error': str(e), 'url': url}
    
    async def read_content(self, response: aiohttp.ClientResponse) -> Optional[str]:
        """Read content from response based on content type"""
        try:
            content_type = response.content_type.lower()
            
            if 'text' in content_type or 'html' in content_type or 'xml' in content_type or 'json' in content_type:
                # Try to decode as text
                content = await response.text()
                return content
            else:
                # For binary content, return None or handle differently
                logger.debug(f"Skipping binary content: {content_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading content: {e}")
            return None
    
    async def fetch_with_retry(self, url: str, max_retries: int = 3, retry_delay: float = 1.0, **kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Fetch with retry logic"""
        
        for attempt in range(max_retries + 1):
            try:
                content, metadata = await self.fetch(url, **kwargs)
                
                if content is not None and metadata and metadata.get('status_code', 0) < 500:
                    return content, metadata
                
                # If we got a 5xx error, retry
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying {url} in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                
            except Exception as e:
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying {url} in {wait_time}s due to error: {e} (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} retries: {e}")
                    return None, {'error': f'Failed after {max_retries} retries: {e}', 'url': url}
        
        return None, {'error': f'Failed after {max_retries} retries', 'url': url}
    
    async def check_url_exists(self, url: str) -> bool:
        """Check if a URL exists (HEAD request)"""
        try:
            if not self.session or self.session.closed:
                await self.start_session()
            
            headers = self.header_manager.get_random_headers()
            async with self.session.head(url, headers=headers, allow_redirects=True) as response:
                return response.status < 400
                
        except Exception as e:
            logger.debug(f"Error checking URL {url}: {e}")
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        if not self.session:
            return {'session_active': False}
        
        return {
            'session_active': not self.session.closed,
            'connector_limit': self.session.connector.limit,
            'connector_limit_per_host': self.session.connector.limit_per_host,
        }
