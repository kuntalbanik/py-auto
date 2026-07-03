import asyncio
import logging
from typing import Optional, Dict, Any

from app.config import config
from app.models.page import Page, PageStatus
from app.models.job import Job, JobStatus
from app.fetcher.http_fetcher import HTTPFetcher
from app.fetcher.playwright_fetcher import PlaywrightFetcher
from app.storage.file_store import FileStore
from app.services.change_detector import ChangeDetector


logger = logging.getLogger(__name__)


class FetchWorker:
    """Worker that fetches URLs from the frontier"""
    
    def __init__(self, frontier=None, db_storage=None):
        self.frontier = frontier
        self.db_storage = db_storage
        self.http_fetcher = HTTPFetcher()
        self.playwright_fetcher = PlaywrightFetcher()
        self.file_store = FileStore()
        self.change_detector = ChangeDetector()
        self.running = False
    
    async def start(self):
        """Start the fetch worker"""
        self.running = True
        await self.http_fetcher.start_session()
        logger.info("Fetch worker started")
        
        while self.running:
            try:
                url = await self.frontier.get_next_url()
                if url:
                    await self.process_url(url)
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in fetch worker: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the fetch worker"""
        self.running = False
        await self.http_fetcher.close_session()
        await self.playwright_fetcher.close_browser()
        logger.info("Fetch worker stopped")
    
    async def process_url(self, url: str) -> bool:
        """Process a single URL"""
        page = Page(url=url, status=PageStatus.FETCHING)
        
        try:
            # Try HTTP fetcher first
            content, metadata = await self.http_fetcher.fetch(url)
            
            # If content is empty or looks like it needs JS rendering, use Playwright
            if not content or self._needs_javascript(content):
                content, metadata = await self.playwright_fetcher.fetch(url)
            
            if not content:
                raise Exception("Failed to fetch content")
            
            # Update page status
            page.status = PageStatus.FETCHED
            page.content = content
            page.status_code = metadata.get('status_code')
            page.content_type = metadata.get('content_type')
            page.headers = metadata.get('headers')
            page.fetched_at = metadata.get('fetched_at')
            page.title = metadata.get('title', '')
            
            # Save to file store
            await self.file_store.save_html(url, content, metadata)
            
            # Save to database if available
            if self.db_storage:
                await self.db_storage.save_page(page)
            
            logger.info(f"Successfully fetched: {url}")
            self.frontier.mark_completed(url, success=True)
            return True
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            page.status = PageStatus.FAILED
            page.error_message = str(e)
            self.frontier.mark_completed(url, success=False)
            return False
    
    def _needs_javascript(self, content: str) -> bool:
        """Check if content might need JavaScript rendering"""
        if not content:
            return True
        
        # Check for common JS indicators
        js_indicators = [
            'window.location',
            'document.write',
            'React',
            'Vue',
            'Angular',
            'SPA',
            'dynamic content',
        ]
        
        for indicator in js_indicators:
            if indicator in content:
                return True
        
        return False


class FetchManager:
    """Manages multiple fetch workers"""
    
    def __init__(self, frontier, db_storage=None, num_workers: int = None):
        self.frontier = frontier
        self.db_storage = db_storage
        self.num_workers = num_workers or config.num_fetch_workers
        self.workers = []
        self.tasks = []
    
    async def start(self):
        """Start all fetch workers"""
        logger.info(f"Starting {self.num_workers} fetch workers")
        
        for i in range(self.num_workers):
            worker = FetchWorker(self.frontier, self.db_storage)
            self.workers.append(worker)
            task = asyncio.create_task(worker.start(), name=f"fetch_worker_{i}")
            self.tasks.append(task)
    
    async def stop(self):
        """Stop all fetch workers"""
        logger.info("Stopping fetch workers")
        
        for worker in self.workers:
            await worker.stop()
        
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get fetch worker statistics"""
        return {
            'num_workers': len(self.workers),
            'running_workers': sum(1 for w in self.workers if w.running),
        }

