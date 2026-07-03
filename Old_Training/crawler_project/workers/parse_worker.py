import asyncio
import logging
from typing import Dict, Any, Optional

from app.config import config
from app.models.page import Page, PageStatus
from app.parser.html_parser import HTMLParser
from app.parser.article_extractor import ArticleExtractor
from app.parser.structured_data import StructuredDataParser
from app.parser.fallback_extractors import FallbackExtractors
from app.storage.file_store import FileStore
from app.scheduler.frontier import URLFrontier


logger = logging.getLogger(__name__)


class ParseWorker:
    """Worker that parses fetched content"""
    
    def __init__(self, frontier: URLFrontier = None, db_storage=None):
        self.frontier = frontier
        self.db_storage = db_storage
        self.html_parser = HTMLParser()
        self.article_extractor = ArticleExtractor()
        self.structured_data_parser = StructuredDataParser()
        self.fallback_extractors = FallbackExtractors()
        self.file_store = FileStore()
        self.running = False
    
    async def start(self):
        """Start the parse worker"""
        self.running = True
        logger.info("Parse worker started")
        
        while self.running:
            try:
                # Get pages that need parsing
                if self.db_storage:
                    pages = await self.db_storage.get_pages_by_status(PageStatus.FETCHED, limit=10)
                    for page in pages:
                        await self.process_page(page)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in parse worker: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the parse worker"""
        self.running = False
        logger.info("Parse worker stopped")
    
    async def process_page(self, page: Page) -> bool:
        """Process a single page"""
        try:
            if not page.content:
                logger.warning(f"No content to parse for {page.url}")
                return False
            
            # Update status
            page.status = PageStatus.PARSING
            if self.db_storage:
                await self.db_storage.update_page_status(page.url, page.status)
            
            # Parse HTML content
            parse_result = await self.html_parser.parse(page.content, page.url)
            
            # Extract article content
            article_result = await self.article_extractor.extract_article(page.content, page.url)
            
            # Extract structured data
            structured_data = await self.structured_data_parser.extract_structured_data(page.content, page.url)
            
            # Combine results
            extracted_data = {
                'html_parse': parse_result,
                'article': article_result,
                'structured_data': structured_data,
            }
            
            # Update page with extracted data
            page.status = PageStatus.PARSED
            page.title = parse_result.get('metadata', {}).get('title', '')
            page.description = parse_result.get('metadata', {}).get('description', '')
            page.extracted_data = extracted_data
            page.extracted_links = [link['url'] for link in parse_result.get('links', [])]
            page.parsed_at = asyncio.get_event_loop().time()
            
            # Add new URLs to frontier
            if self.frontier:
                for link in parse_result.get('links', []):
                    url = link.get('url')
                    if url:
                        await self.frontier.add_url(url, source_url=page.url)
            
            # Save snapshot
            await self.file_store.save_snapshot(page.url, extracted_data)
            
            # Save to database
            if self.db_storage:
                await self.db_storage.save_page(page)
            
            logger.info(f"Successfully parsed: {page.url}")
            return True
            
        except Exception as e:
            logger.error(f"Error parsing {page.url}: {e}")
            page.status = PageStatus.FAILED
            page.error_message = str(e)
            if self.db_storage:
                await self.db_storage.update_page_status(page.url, page.status, str(e))
            return False
    
    async def process_content(self, url: str, content: str, content_type: str = 'text/html') -> Dict[str, Any]:
        """Process raw content without database"""
        try:
            # Check content type and parse accordingly
            if 'html' in content_type.lower():
                parse_result = await self.html_parser.parse(content, url)
                article_result = await self.article_extractor.extract_article(content, url)
                structured_data = await self.structured_data_parser.extract_structured_data(content, url)
                
                return {
                    'html_parse': parse_result,
                    'article': article_result,
                    'structured_data': structured_data,
                    'status': 'success',
                }
            
            elif 'json' in content_type.lower():
                import json
                return {
                    'data': json.loads(content),
                    'status': 'success',
                }
            
            elif 'xml' in content_type.lower():
                import xml.etree.ElementTree as ET
                return {
                    'data': ET.fromstring(content),
                    'status': 'success',
                }
            
            else:
                # Use fallback extractors
                return await self.fallback_extractors.extract_content_fallback(content, url)
                
        except Exception as e:
            logger.error(f"Error processing content for {url}: {e}")
            return {
                'error': str(e),
                'status': 'error',
            }


class ParseManager:
    """Manages multiple parse workers"""
    
    def __init__(self, frontier, db_storage=None, num_workers: int = None):
        self.frontier = frontier
        self.db_storage = db_storage
        self.num_workers = num_workers or config.num_parse_workers
        self.workers = []
        self.tasks = []
    
    async def start(self):
        """Start all parse workers"""
        logger.info(f"Starting {self.num_workers} parse workers")
        
        for i in range(self.num_workers):
            worker = ParseWorker(self.frontier, self.db_storage)
            self.workers.append(worker)
            task = asyncio.create_task(worker.start(), name=f"parse_worker_{i}")
            self.tasks.append(task)
    
    async def stop(self):
        """Stop all parse workers"""
        logger.info("Stopping parse workers")
        
        for worker in self.workers:
            await worker.stop()
        
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get parse worker statistics"""
        return {
            'num_workers': len(self.workers),
            'running_workers': sum(1 for w in self.workers if w.running),
        }
