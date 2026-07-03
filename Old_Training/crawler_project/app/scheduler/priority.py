from urllib.parse import urlparse
from typing import Optional
import re


class PriorityCalculator:
    """Calculates priority for URLs based on various factors"""
    
    def __init__(self):
        # High priority patterns (lower number = higher priority)
        self.high_priority_patterns = [
            r'.*/api/.*',           # API endpoints
            r'.*/json.*',           # JSON endpoints
            r'.*/data.*',           # Data endpoints
        ]
        
        # Low priority patterns (higher number = lower priority)
        self.low_priority_patterns = [
            r'.*/login.*',          # Login pages
            r'.*/register.*',       # Registration pages
            r'.*/logout.*',         # Logout pages
            r'.*/admin.*',          # Admin pages
            r'.*/dashboard.*',      # Dashboard pages
            r'.*/settings.*',       # Settings pages
            r'.*/profile.*',        # Profile pages
            r'.*/cart.*',           # Shopping cart
            r'.*/checkout.*',       # Checkout pages
            r'.*/payment.*',        # Payment pages
            r'.*/account.*',        # Account pages
            r'.*/user.*',           # User pages
            r'.*/search.*',         # Search pages (can be infinite)
            r'.*/tag.*',            # Tag pages
            r'.*/category.*',       # Category pages
            r'.*/page/.*',          # Paginated pages
            r'.*\?.*page=.*',       # Query parameter pagination
            r'.*/feed.*',           # RSS/Atom feeds
            r'.*/rss.*',            # RSS feeds
            r'.*/atom.*',           # Atom feeds
            r'.*/sitemap.*',        # Sitemaps
            r'.*/robots\.txt.*',    # Robots.txt
            r'.*/favicon\.ico.*',   # Favicon
            r'.*/404.*',            # Error pages
            r'.*/500.*',            # Error pages
            r'.*/error.*',          # Error pages
        ]
        
        # File extensions to avoid
        self.avoid_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.tar', '.gz', '.exe', '.dmg', '.pkg',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
            '.css', '.js', '.json', '.xml', '.txt', '.log'
        ]
    
    def calculate_priority(self, url: str, source_url: Optional[str] = None) -> int:
        """Calculate priority for a URL (lower number = higher priority)"""
        
        # Default priority
        priority = 100
        
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            full_url = url.lower()
            
            # Check for file extensions to avoid
            for ext in self.avoid_extensions:
                if path.endswith(ext):
                    return 1000  # Very low priority
            
            # Check high priority patterns
            for pattern in self.high_priority_patterns:
                if re.match(pattern, path) or re.match(pattern, full_url):
                    priority = min(priority, 10)
                    break
            
            # Check low priority patterns
            for pattern in self.low_priority_patterns:
                if re.match(pattern, path) or re.match(pattern, full_url):
                    priority = max(priority, 500)
                    break
            
            # Depth-based priority (prefer shallower pages)
            depth = path.count('/')
            if depth > 0:
                priority += depth * 10
            
            # URL length priority (prefer shorter URLs)
            url_length = len(url)
            if url_length > 100:
                priority += (url_length - 100) // 10
            
            # Source-based priority
            if source_url:
                # Same domain gets slight priority boost
                if urlparse(source_url).netloc == parsed.netloc:
                    priority -= 5
                
                # Same path hierarchy gets priority boost
                source_path = urlparse(source_url).path
                if path.startswith(source_path.rsplit('/', 1)[0]):
                    priority -= 3
            
            # Homepage gets highest priority
            if path in ['', '/', '/index.html', '/index.htm']:
                priority = 1
            
            # Common important pages
            important_pages = ['/about', '/contact', '/products', '/services']
            if path in important_pages or path.endswith('/') and path[:-1] in important_pages:
                priority = min(priority, 20)
            
            # Ensure priority is within reasonable bounds
            priority = max(1, min(1000, priority))
            
        except Exception:
            # If anything goes wrong, return default priority
            priority = 100
        
        return priority
    
    def should_crawl(self, url: str) -> bool:
        """Determine if a URL should be crawled at all"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Check for file extensions to avoid
            for ext in self.avoid_extensions:
                if path.endswith(ext):
                    return False
            
            # Check for very low priority patterns
            very_low_patterns = [
                r'.*/login.*',
                r'.*/logout.*',
                r'.*/admin.*',
                r'.*/dashboard.*',
                r'.*/settings.*',
                r'.*/profile.*',
                r'.*/cart.*',
                r'.*/checkout.*',
                r'.*/payment.*',
                r'.*/account.*',
            ]
            
            for pattern in very_low_patterns:
                if re.match(pattern, path):
                    return False
            
            return True
            
        except Exception:
            return False
