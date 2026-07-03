import asyncio
from collections import deque
from typing import Set, Optional, List
from urllib.parse import urljoin, urlparse
import time
import logging

from app.config import config
from app.scheduler.priority import PriorityCalculator
from app.scheduler.robots import RobotsChecker


logger = logging.getLogger(__name__)


class URLFrontier:
    """Manages the URL frontier - the queue of URLs to be crawled"""
    
    def __init__(self):
        self._queue = asyncio.PriorityQueue()
        self._seen_urls: Set[str] = set()
        self._in_progress: Set[str] = set()
        self._priority_calculator = PriorityCalculator()
        self._robots_checker = RobotsChecker()
        self._domain_delays = {}  # Track last request time per domain
        self._stats = {
            'total_added': 0,
            'total_processed': 0,
            'total_failed': 0,
            'queue_size': 0
        }
    
    async def add_url(self, url: str, priority: Optional[int] = None, source_url: Optional[str] = None) -> bool:
        """Add a URL to the frontier"""
        try:
            # Normalize URL
            normalized_url = self._normalize_url(url, source_url)
            
            # Skip if already seen
            if normalized_url in self._seen_urls:
                return False
            
            # Check robots.txt
            if not await self._robots_checker.is_allowed(normalized_url):
                logger.debug(f"URL blocked by robots.txt: {normalized_url}")
                return False
            
            # Calculate priority if not provided
            if priority is None:
                priority = self._priority_calculator.calculate_priority(normalized_url, source_url)
            
            # Check domain delay
            domain = urlparse(normalized_url).netloc
            if not self._can_request_domain(domain):
                # Add back to queue with delay
                await asyncio.sleep(config.request_delay)
            
            # Add to queue
            await self._queue.put((priority, time.time(), normalized_url))
            self._seen_urls.add(normalized_url)
            self._stats['total_added'] += 1
            self._stats['queue_size'] = self._queue.qsize()
            
            logger.debug(f"Added URL to frontier: {normalized_url} (priority: {priority})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding URL {url}: {e}")
            return False
    
    async def get_next_url(self) -> Optional[str]:
        """Get the next URL to crawl"""
        try:
            if self._queue.empty():
                return None
            
            priority, timestamp, url = await self._queue.get()
            
            # Check if URL is still valid (not too old)
            if time.time() - timestamp > 3600:  # 1 hour timeout
                logger.warning(f"URL expired in queue: {url}")
                return await self.get_next_url()
            
            self._in_progress.add(url)
            self._stats['queue_size'] = self._queue.qsize()
            
            # Update domain delay
            domain = urlparse(url).netloc
            self._domain_delays[domain] = time.time()
            
            logger.debug(f"Retrieved URL from frontier: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error getting next URL: {e}")
            return None
    
    def mark_completed(self, url: str, success: bool = True):
        """Mark a URL as completed"""
        if url in self._in_progress:
            self._in_progress.remove(url)
            self._stats['total_processed'] += 1
            
            if not success:
                self._stats['total_failed'] += 1
    
    def add_seed_urls(self):
        """Add seed URLs to the frontier"""
        for url in config.seed_urls:
            asyncio.create_task(self.add_url(url, priority=0))
    
    def _normalize_url(self, url: str, source_url: Optional[str] = None) -> str:
        """Normalize and resolve URL"""
        # If relative URL, resolve against source URL
        if source_url and not url.startswith(('http://', 'https://')):
            url = urljoin(source_url, url)
        
        # Parse and rebuild URL to normalize
        parsed = urlparse(url)
        
        # Remove fragment
        parsed = parsed._replace(fragment='')
        
        # Convert to lowercase scheme and netloc
        parsed = parsed._replace(scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower())
        
        return parsed.geturl()
    
    def _can_request_domain(self, domain: str) -> bool:
        """Check if we can request a domain based on delay rules"""
        if domain not in self._domain_delays:
            return True
        
        last_request = self._domain_delays[domain]
        return time.time() - last_request >= config.request_delay
    
    def get_stats(self) -> dict:
        """Get frontier statistics"""
        return self._stats.copy()
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self._queue.qsize()
    
    def is_empty(self) -> bool:
        """Check if frontier is empty"""
        return self._queue.empty()
    
    async def clear(self):
        """Clear the frontier"""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        self._seen_urls.clear()
        self._in_progress.clear()
        self._domain_delays.clear()
        self._stats = {
            'total_added': 0,
            'total_processed': 0,
            'total_failed': 0,
            'queue_size': 0
        }
