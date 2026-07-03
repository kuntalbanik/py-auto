import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SelectorManager:
    """Manages and adapts CSS selectors for different sites"""
    
    def __init__(self):
        self.selectors_file = "data/site_selectors.json"
        self.default_selectors = {
            'title': ['h1', '.title', '#title', '.post-title'],
            'content': ['article', '.content', '#content', '.post-content', '.entry-content'],
            'author': ['.author', '.byline', '[rel="author"]'],
            'date': ['.date', 'time', '.published', '[property="datePublished"]'],
            'links': ['a[href]'],
            'images': ['img[src]'],
        }
        self.site_specific = {}
        self._load_selectors()
    
    def _load_selectors(self):
        """Load site-specific selectors from file"""
        if os.path.exists(self.selectors_file):
            try:
                with open(self.selectors_file, 'r') as f:
                    self.site_specific = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading selectors: {e}")
    
    def _save_selectors(self):
        """Save site-specific selectors to file"""
        try:
            os.makedirs(os.path.dirname(self.selectors_file), exist_ok=True)
            with open(self.selectors_file, 'w') as f:
                json.dump(self.site_specific, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving selectors: {e}")
    
    def get_selectors(self, domain: str) -> Dict[str, List[str]]:
        """Get selectors for a domain, falling back to defaults"""
        if domain in self.site_specific:
            return self.site_specific[domain]
        return self.default_selectors
    
    def register_selectors(self, domain: str, selectors: Dict[str, List[str]]):
        """Register site-specific selectors"""
        self.site_specific[domain] = selectors
        self._save_selectors()
    
    def adapt_selector(self, html_content: str, selector: str) -> Optional[str]:
        """Try to adapt a selector to match the HTML content"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try exact selector
        if soup.select(selector):
            return selector
        
        # Try variations
        variations = self._generate_variations(selector)
        for variation in variations:
            if soup.select(variation):
                return variation
        
        return None
    
    def _generate_variations(self, selector: str) -> List[str]:
        """Generate selector variations"""
        variations = []
        
        # Try different classes/IDs
        parts = selector.split()
        if parts:
            last_part = parts[-1]
            variations.append(last_part)
            
            # Try just the tag
            tag = last_part.split('.')[0].split('#')[0]
            if tag:
                variations.append(tag)
        
        return variations
