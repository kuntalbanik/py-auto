from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging


logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Base class for all parsers"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def can_parse(self, content_type: str, url: str = None) -> bool:
        """Check if this parser can handle the given content type"""
        pass
    
    @abstractmethod
    async def parse(self, content: str, url: str = None, **kwargs) -> Dict[str, Any]:
        """Parse the content and return extracted data"""
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common unwanted characters
        unwanted_chars = ['\t', '\n', '\r']
        for char in unwanted_chars:
            text = text.replace(char, ' ')
        
        # Remove multiple spaces
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        return text.strip()
    
    def extract_urls(self, text: str, base_url: str = None) -> List[str]:
        """Extract URLs from text (basic implementation)"""
        import re
        from urllib.parse import urljoin, urlparse
        
        # Basic URL regex
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Resolve relative URLs if base_url is provided
        if base_url:
            resolved_urls = []
            for url in urls:
                if url.startswith(('http://', 'https://')):
                    resolved_urls.append(url)
                else:
                    resolved_urls.append(urljoin(base_url, url))
            return resolved_urls
        
        return urls
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        from urllib.parse import urlparse
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
