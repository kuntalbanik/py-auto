import asyncio
import aiohttp
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import time
import logging
from typing import Dict, Optional


logger = logging.getLogger(__name__)


class RobotsChecker:
    """Handles robots.txt checking for URLs"""
    
    def __init__(self):
        self._cache: Dict[str, RobotFileParser] = {}
        self._cache_ttl = 3600  # 1 hour
        self._user_agent = "*"
    
    async def is_allowed(self, url: str, user_agent: str = None) -> bool:
        """Check if a URL is allowed by robots.txt"""
        if user_agent is None:
            user_agent = self._user_agent
        
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Get or create robots parser for this domain
            robots_parser = await self._get_robots_parser(domain)
            
            if robots_parser is None:
                # No robots.txt found, allow by default
                return True
            
            # Check if URL is allowed
            return robots_parser.can_fetch(user_agent, url)
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            # If there's an error, allow by default
            return True
    
    async def _get_robots_parser(self, domain: str) -> Optional[RobotFileParser]:
        """Get or create a RobotFileParser for a domain"""
        
        # Check cache first
        if domain in self._cache:
            parser, timestamp = self._cache[domain]
            if time.time() - timestamp < self._cache_ttl:
                return parser
            else:
                # Cache expired, remove it
                del self._cache[domain]
        
        # Fetch robots.txt
        robots_url = f"{domain}/robots.txt"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(robots_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        parser = RobotFileParser()
                        parser.set_url(robots_url)
                        parser.parse(content.splitlines())
                        
                        # Cache the parser
                        self._cache[domain] = (parser, time.time())
                        
                        logger.debug(f"Loaded robots.txt for {domain}")
                        return parser
                    else:
                        logger.debug(f"No robots.txt found for {domain} (status: {response.status})")
                        return None
                        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching robots.txt for {domain}")
            return None
        except Exception as e:
            logger.warning(f"Error fetching robots.txt for {domain}: {e}")
            return None
    
    def get_crawl_delay(self, domain: str, user_agent: str = None) -> Optional[float]:
        """Get crawl delay from robots.txt"""
        if user_agent is None:
            user_agent = self._user_agent
        
        if domain in self._cache:
            parser, _ = self._cache[domain]
            try:
                delay = parser.crawl_delay(user_agent)
                return delay
            except Exception:
                pass
        
        return None
    
    def clear_cache(self):
        """Clear the robots.txt cache"""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cached_domains': len(self._cache),
            'cache_ttl': self._cache_ttl,
        }
