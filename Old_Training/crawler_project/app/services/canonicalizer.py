import re
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class URLCanonicalizer:
    """Normalizes and canonicalizes URLs for deduplication"""
    
    def __init__(self):
        # Tracking parameters to remove
        self.tracking_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'utm_id', 'utm_source_platform', 'utm_creative_format', 'utm_marketing_tactic',
            'fbclid', 'gclid', 'msclkid', 'dclid',
            'twclid', 'li_fat_id', 'mc_cid', 'mc_eid',
            '_ga', '_gid', '_gac', '_gl', '_gaid',
            'source', 'medium', 'campaign', 'ref', 'referrer',
            'trk', 'trk_contact', 'trk_msg', 'trk_module', 'trk_sid',
            'si', 'cs', 'cs_noapp', 'em', 'email', 'token', 'sessionid', 'phid',
        ]
    
    def canonicalize(self, url: str, base_url: Optional[str] = None) -> str:
        """Canonicalize a URL"""
        try:
            # Handle relative URLs
            if base_url and not url.startswith(('http://', 'https://')):
                from urllib.parse import urljoin
                url = urljoin(base_url, url)
            
            parsed = urlparse(url)
            
            # Lowercase scheme and netloc
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            
            # Remove default port
            if (scheme == 'http' and netloc.endswith(':80')) or \
               (scheme == 'https' and netloc.endswith(':443')):
                netloc = netloc.rsplit(':', 1)[0]
            
            # Remove www. prefix
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            # Remove fragment
            fragment = ''
            
            # Clean path (remove double slashes, decode)
            path = parsed.path
            path = re.sub(r'/{2,}', '/', path)
            path = path.replace(' ', '%20')
            
            # Clean query parameters
            query = self._clean_query(parsed.query)
            
            # Remove empty query
            if not query:
                query = ''
            
            # Remove trailing slash
            if path != '/' and path.endswith('/'):
                path = path[:-1]
            
            # Reconstruct URL
            canonical_url = urlunparse((scheme, netloc, path, parsed.params, query, fragment))
            
            return canonical_url
            
        except Exception as e:
            logger.error(f"Error canonicalizing URL {url}: {e}")
            return url.lower()
    
    def _clean_query(self, query: str) -> str:
        """Remove tracking parameters from query string"""
        if not query:
            return ''
        
        try:
            params = parse_qs(query, keep_blank_values=False)
            
            # Remove tracking parameters
            for param in self.tracking_params:
                params.pop(param, None)
            
            # Sort parameters for consistency
            sorted_params = dict(sorted(params.items()))
            
            # Encode back
            query = urlencode(sorted_params, doseq=True)
            return query
            
        except Exception:
            return ''
    
    def is_same_page(self, url1: str, url2: str) -> bool:
        """Check if two URLs point to the same page"""
        return self.canonicalize(url1) == self.canonicalize(url2)


class ContentCanonicalizer:
    """Canonicalizes content for deduplication"""
    
    def __init__(self):
        self.max_length = 5000
    
    def canonicalize(self, text: str) -> str:
        """Canonicalize text content"""
        if not text:
            return ''
        
        # Lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit length
        if len(text) > self.max_length:
            text = text[:self.max_length]
        
        return text
