import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class FallbackExtractors:
    """Fallback extraction methods when primary extractors fail"""
    
    def __init__(self):
        # Common content patterns
        self.content_patterns = [
            r'<p[^>]*>(.*?)</p>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
        ]
        
        # Boilerplate patterns to remove
        self.boilerplate_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<style[^>]*>.*?</style>',
            r'<nav[^>]*>.*?</nav>',
            r'<header[^>]*>.*?</header>',
            r'<footer[^>]*>.*?</footer>',
            r'<aside[^>]*>.*?</aside>',
            r'<!--.*?-->',
            r'<[^>]*class="[^"]*sidebar[^"]*"[^>]*>.*?</[^>]*>',
            r'<[^>]*class="[^"]*menu[^"]*"[^>]*>.*?</[^>]*>',
            r'<[^>]*class="[^"]*navigation[^"]*"[^>]*>.*?</[^>]*>',
        ]
        
        # Link patterns
        self.link_patterns = [
            r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            r'<link\s+[^>]*href=["\']([^"\']+)["\'][^>]*>',
            r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>',
            r'<script\s+[^>]*src=["\']([^"\']+)["\'][^>]*>',
        ]
    
    async def extract_content_fallback(self, html_content: str, url: str = None) -> Dict[str, Any]:
        """Fallback content extraction using regex patterns"""
        try:
            result = {
                'title': self._extract_title_fallback(html_content),
                'content': self._extract_content_fallback(html_content),
                'links': self._extract_links_fallback(html_content),
                'images': self._extract_images_fallback(html_content),
                'metadata': self._extract_metadata_fallback(html_content),
                'extractor': 'fallback_extractor',
            }
            
            logger.debug(f"Fallback extraction for {url}: {len(result['content'])} chars")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in fallback extraction for {url}: {e}")
            return {
                'error': str(e),
                'extractor': 'fallback_extractor',
            }
    
    def _extract_title_fallback(self, html_content: str) -> str:
        """Extract title using fallback methods"""
        # Try title tag first
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = re.sub(r'\s+', ' ', title_match.group(1)).strip()
            if title and len(title) > 3:
                return title
        
        # Try h1 tags
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        for h1_text in h1_matches:
            h1_text = re.sub(r'\s+', ' ', h1_text).strip()
            if h1_text and len(h1_text) > 3:
                return h1_text
        
        # Try meta title
        meta_title = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        if meta_title:
            return meta_title.group(1).strip()
        
        return ""
    
    def _extract_content_fallback(self, html_content: str) -> str:
        """Extract content using fallback methods"""
        # Remove boilerplate
        cleaned_html = html_content
        for pattern in self.boilerplate_patterns:
            cleaned_html = re.sub(pattern, '', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
        
        # Try content patterns
        for pattern in self.content_patterns:
            matches = re.findall(pattern, cleaned_html, re.IGNORECASE | re.DOTALL)
            if matches:
                content = ' '.join(matches)
                content = self._clean_html_text(content)
                
                if len(content) > 100:  # Reasonable content length
                    return content
        
        # Fallback: extract all paragraph text
        p_matches = re.findall(r'<p[^>]*>(.*?)</p>', cleaned_html, re.IGNORECASE | re.DOTALL)
        if p_matches:
            content = ' '.join(p_matches)
            content = self._clean_html_text(content)
            return content
        
        # Last resort: extract all text
        text_content = re.sub(r'<[^>]+>', ' ', cleaned_html)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        return text_content
    
    def _extract_links_fallback(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract links using fallback methods"""
        links = []
        
        # Extract all href attributes
        href_pattern = r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(href_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        for href, text in matches:
            href = href.strip()
            text = re.sub(r'<[^>]+>', '', text).strip()
            
            # Skip certain types of links
            if href.startswith(('javascript:', 'mailto:', 'tel:', 'ftp:')):
                continue
            
            links.append({
                'url': href,
                'text': text,
                'tag': 'a',
            })
        
        return links
    
    def _extract_images_fallback(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract images using fallback methods"""
        images = []
        
        # Extract img tags
        img_pattern = r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(img_pattern, html_content, re.IGNORECASE)
        
        for src in matches:
            images.append({
                'src': src.strip(),
                'alt': '',
                'title': '',
            })
        
        return images
    
    def _extract_metadata_fallback(self, html_content: str) -> Dict[str, Any]:
        """Extract metadata using fallback methods"""
        metadata = {}
        
        # Extract meta tags
        meta_pattern = r'<meta\s+[^>]*(name|property|http-equiv)=["\']([^"\']+)["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
        matches = re.findall(meta_pattern, html_content, re.IGNORECASE)
        
        for attr_type, name, content in matches:
            metadata[name.lower()] = content
        
        # Extract language
        lang_match = re.search(r'<html[^>]*lang=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        if lang_match:
            metadata['language'] = lang_match.group(1)
        
        return metadata
    
    def _clean_html_text(self, text: str) -> str:
        """Clean HTML text"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common boilerplate
        boilerplate_phrases = [
            r'\bclick here\b',
            r'\bread more\b',
            r'\bcontinue reading\b',
            r'\bsubscribe\b',
            r'\bnewsletter\b',
            r'\badvertisement\b',
            r'\bsponsored\b',
        ]
        
        for phrase in boilerplate_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    async def extract_json_fallback(self, content: str) -> Dict[str, Any]:
        """Fallback JSON extraction"""
        try:
            # Try to find JSON in script tags
            json_pattern = r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>'
            matches = re.findall(json_pattern, content, re.IGNORECASE | re.DOTALL)
            
            json_data = []
            for match in matches:
                try:
                    import json
                    data = json.loads(match.strip())
                    json_data.append(data)
                except json.JSONDecodeError:
                    continue
            
            return {'json_data': json_data}
            
        except Exception as e:
            logger.error(f"Error in JSON fallback extraction: {e}")
            return {'error': str(e)}
    
    async def extract_xml_fallback(self, content: str) -> Dict[str, Any]:
        """Fallback XML extraction"""
        try:
            import xml.etree.ElementTree as ET
            
            # Try to parse as XML
            root = ET.fromstring(content)
            
            result = {
                'root_tag': root.tag,
                'attributes': dict(root.attrib),
                'text': root.text.strip() if root.text else '',
                'children': [],
            }
            
            for child in root:
                child_data = {
                    'tag': child.tag,
                    'attributes': dict(child.attrib),
                    'text': child.text.strip() if child.text else '',
                }
                result['children'].append(child_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in XML fallback extraction: {e}")
            return {'error': str(e)}
    
    def detect_content_type_fallback(self, content: str) -> str:
        """Detect content type using fallback methods"""
        content_lower = content.lower()
        
        # Check for HTML
        if re.search(r'<html|<!doctype|<head|<body', content_lower):
            return 'text/html'
        
        # Check for JSON
        if content.strip().startswith('{') or content.strip().startswith('['):
            return 'application/json'
        
        # Check for XML
        if content.strip().startswith('<?xml') or '<' in content[:100]:
            return 'application/xml'
        
        # Check for plain text
        if not re.search(r'<[^>]+>', content):
            return 'text/plain'
        
        return 'application/octet-stream'
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from plain text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Clean and validate URLs
        clean_urls = []
        for url in urls:
            url = url.rstrip('.,;:!?)')  # Remove trailing punctuation
            if len(url) > 10:  # Minimum reasonable URL length
                clean_urls.append(url)
        
        return clean_urls
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_emails = []
        for email in emails:
            if email.lower() not in seen:
                seen.add(email.lower())
                unique_emails.append(email)
        
        return unique_emails
    
    def extract_phone_numbers_from_text(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # US format
            r'\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b',  # International
            r'\b\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b',  # US with parentheses
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        # Remove duplicates
        return list(set(phones))
