import asyncio
import signal
import logging
from typing import Dict, Any

from app.config import config
from app.scheduler.frontier import URLFrontier
from app.storage.postgres import PostgreSQLStorage
from app.storage.cache import cache
from app.services.logger import setup_logging
from workers.fetch_worker import FetchManager
from workers.parse_worker import ParseManager


logger = logging.getLogger(__name__)


class CrawlerEngine:
    """Main crawler engine that orchestrates all components"""
    
    def __init__(self):
        self.frontier = URLFrontier()
        self.db_storage = PostgreSQLStorage()
        self.fetch_manager = None
        self.parse_manager = None
        self.running = False
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing crawler engine...")
        
        # Setup logging
        setup_logging(config.logs_dir)
        
        # Initialize storage
        try:
            await self.db_storage.initialize()
            logger.info("Database storage initialized")
        except Exception as e:
            logger.warning(f"Database storage not available: {e}")
            self.db_storage = None
        
        # Initialize cache
        try:
            await cache.initialize()
            logger.info("Cache initialized")
        except Exception as e:
            logger.warning(f"Cache not available: {e}")
        
        # Add seed URLs to frontier
        self.frontier.add_seed_urls()
        logger.info(f"Added {len(config.seed_urls)} seed URLs to frontier")
        
        # Create worker managers
        self.fetch_manager = FetchManager(self.frontier, self.db_storage)
        self.parse_manager = ParseManager(self.frontier, self.db_storage)
        
        logger.info("Crawler engine initialized")
    
    async def start(self):
        """Start the crawler engine"""
        if not self.fetch_manager or not self.parse_manager:
            raise RuntimeError("Engine not initialized")
        
        self.running = True
        logger.info("Starting crawler engine...")
        
        # Start workers
        await self.fetch_manager.start()
        await self.parse_manager.start()
        
        logger.info("Crawler engine started")
    
    async def stop(self):
        """Stop the crawler engine"""
        self.running = False
        logger.info("Stopping crawler engine...")
        
        # Stop workers
        if self.fetch_manager:
            await self.fetch_manager.stop()
        
        if self.parse_manager:
            await self.parse_manager.stop()
        
        # Close storage
        if self.db_storage:
            await self.db_storage.close()
        
        await cache.close()
        
        logger.info("Crawler engine stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get crawler engine statistics"""
        return {
            'frontier': self.frontier.get_stats() if self.frontier else {},
            'fetch': self.fetch_manager.get_stats() if self.fetch_manager else {},
            'parse': self.parse_manager.get_stats() if self.parse_manager else {},
        }
    
    async def add_url(self, url: str, priority: int = None):
        """Add a URL to the frontier"""
        if self.frontier:
            await self.frontier.add_url(url, priority=priority)
            logger.info(f"Added URL: {url}")


async def main():
    """Main entry point"""
    engine = CrawlerEngine()
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(engine.stop())
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize engine
        await engine.initialize()
        
        # Start engine
        await engine.start()
        
        # Keep running until interrupted
        while engine.running:
            await asyncio.sleep(1)
            
            # Log stats periodically
            stats = engine.get_stats()
            if stats['frontier'].get('total_processed', 0) % 100 == 0:
                logger.info(f"Crawler stats: {stats}")
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
    
    finally:
        await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())

