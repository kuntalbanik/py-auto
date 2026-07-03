import asyncio
import time
import logging
from typing import Optional, Dict, Any, Tuple
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from app.config import config
from app.fetcher.headers import HeaderManager


logger = logging.getLogger(__name__)


class PlaywrightFetcher:
    """Playwright fetcher for JavaScript-heavy pages"""
    
    def __init__(self):
        self.header_manager = HeaderManager()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()
    
    async def start_browser(self):
        """Start the browser"""
        if self.browser is None or not self.browser.is_connected():
            self.playwright = await async_playwright().start()
            
            # Launch browser with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # Disable images for faster loading
                    '--disable-javascript',  # We'll enable JS per page as needed
                ]
            )
            
            # Create context with custom headers
            headers = self.header_manager.get_random_headers()
            self.context = await self.browser.new_context(
                user_agent=headers['User-Agent'],
                viewport={'width': 1920, 'height': 1080},
                java_script_enabled=True,
                ignore_https_errors=True,
                extra_http_headers=headers
            )
            
            logger.info("Playwright browser started")
    
    async def close_browser(self):
        """Close the browser"""
        try:
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser and self.browser.is_connected():
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                
            logger.info("Playwright browser closed")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def fetch(self, url: str, wait_for: Optional[str] = None, 
                   wait_for_timeout: int = 10000, javascript: bool = True,
                   screenshot: bool = False, **kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Fetch a URL using Playwright"""
        
        if not self.browser or not self.browser.is_connected():
            await self.start_browser()
        
        page = None
        try:
            # Create new page
            page = await self.context.new_page()
            
            # Set JavaScript
            await page.set_javascript_enabled(javascript)
            
            # Navigate to URL
            start_time = time.time()
            
            response = await page.goto(
                url,
                wait_until='networkidle',
                timeout=config.timeout * 1000  # Convert to milliseconds
            )
            
            load_time = time.time() - start_time
            
            # Wait for specific element if requested
            if wait_for:
                try:
                    await page.wait_for_selector(wait_for, timeout=wait_for_timeout)
                except Exception as e:
                    logger.warning(f"Wait for selector failed: {e}")
            
            # Get content
            content = await page.content()
            
            # Get page metadata
            metadata = await self._extract_metadata(page, response, load_time)
            
            # Take screenshot if requested
            if screenshot:
                try:
                    screenshot_path = f"data/screenshots/{urlparse(url).netloc}_{int(time.time())}.png"
                    await page.screenshot(path=screenshot_path, full_page=True)
                    metadata['screenshot_path'] = screenshot_path
                except Exception as e:
                    logger.warning(f"Screenshot failed: {e}")
            
            logger.debug(f"Playwright fetched {url} (status: {response.status if response else 'unknown'}, load_time: {load_time:.2f}s)")
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Playwright error fetching {url}: {e}")
            return None, {'error': str(e), 'url': url}
        finally:
            if page:
                await page.close()
    
    async def _extract_metadata(self, page: Page, response, load_time: float) -> Dict[str, Any]:
        """Extract metadata from the page"""
        metadata = {
            'status_code': response.status if response else 0,
            'url': page.url,
            'final_url': page.url,
            'load_time': load_time,
            'fetched_at': time.time(),
            'fetcher': 'playwright',
        }
        
        try:
            # Get page title
            title = await page.title()
            metadata['title'] = title
            
            # Get meta description
            description = await page.eval_on_selector_all('meta[name="description"]', 'els => els.map(el => el.content).join(", ")')
            metadata['description'] = description
            
            # Get page size
            content = await page.content()
            metadata['size'] = len(content)
            
            # Check if JavaScript was executed
            js_executed = await page.evaluate('() => !!window.document')
            metadata['javascript_executed'] = js_executed
            
            # Get console errors
            console_errors = []
            page.on('console', lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == 'error' else None)
            metadata['console_errors'] = console_errors
            
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        return metadata
    
    async def fetch_with_retry(self, url: str, max_retries: int = 2, retry_delay: float = 2.0, **kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Fetch with retry logic"""
        
        for attempt in range(max_retries + 1):
            try:
                content, metadata = await self.fetch(url, **kwargs)
                
                if content is not None and metadata and metadata.get('status_code', 0) < 500:
                    return content, metadata
                
                # If we got a 5xx error, retry
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying Playwright {url} in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                
            except Exception as e:
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying Playwright {url} in {wait_time}s due to error: {e} (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} with Playwright after {max_retries} retries: {e}")
                    return None, {'error': f'Failed after {max_retries} retries: {e}', 'url': url}
        
        return None, {'error': f'Failed after {max_retries} retries', 'url': url}
    
    async def wait_for_network_idle(self, page: Page, timeout: int = 5000):
        """Wait for network to be idle"""
        try:
            await page.wait_for_load_state('networkidle', timeout=timeout)
        except Exception as e:
            logger.warning(f"Network idle wait failed: {e}")
    
    def get_browser_stats(self) -> Dict[str, Any]:
        """Get browser statistics"""
        return {
            'browser_connected': self.browser.is_connected() if self.browser else False,
            'context_active': self.context is not None,
        }
