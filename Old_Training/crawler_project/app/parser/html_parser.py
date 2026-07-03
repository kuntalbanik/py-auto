import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
import logging

from app.parser.base import BaseParser


logger = logging.getLogger(__name__)


class HTMLParser(BaseParser):
    """HTML parser using BeautifulSoup"""
    
    def __init__(self):
        super().__init__()
        self.link_selectors = [
            'a[href]',
            'link[href]',
            'script[src]',
            'img[src]',
            'iframe[src]',
            'source[src]',
            'video[src]',
            'audio[src]',
        ]
    
    def can_parse(self, content_type: str, url: str = None) -> bool:
        """Check if this parser can handle the content type"""
        return content_type and any(ct in content_type.lower() for ct in ['text/html', 'application/xhtml+xml'])
    
    async def parse(self, content: str, url: str = None, **kwargs) -> Dict[str, Any]:
        """Parse HTML content and extract data"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract basic metadata
            metadata = self._extract_metadata(soup)
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Extract text content
            text_content = self._extract_text_content(soup)
            
            # Extract structured data
            structured_data = self._extract_structured_data(soup)
            
            # Extract images
            images = self._extract_images(soup, url)
            
            # Extract forms
            forms = self._extract_forms(soup)
            
            result = {
                'metadata': metadata,
                'links': links,
                'text_content': text_content,
                'structured_data': structured_data,
                'images': images,
                'forms': forms,
                'word_count': len(text_content.split()) if text_content else 0,
                'parser': 'html_parser',
            }
            
            logger.debug(f"Parsed HTML content for {url}: {len(links)} links, {result['word_count']} words")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing HTML content for {url}: {e}")
            return {
                'error': str(e),
                'parser': 'html_parser',
            }
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML"""
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = self.clean_text(title_tag.get_text())
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            
            if name and content:
                metadata[name.lower()] = content
        
        # Language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag.get('lang')
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata['canonical_url'] = canonical.get('href')
        
        # Description (common meta tags)
        for desc_key in ['description', 'og:description', 'twitter:description']:
            if desc_key in metadata:
                metadata['description'] = metadata[desc_key]
                break
        
        return metadata
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str = None) -> List[Dict[str, Any]]:
        """Extract all links from the HTML"""
        links = []
        
        for selector in self.link_selectors:
            elements = soup.select(selector)
            
            for element in elements:
                href = element.get('href') or element.get('src')
                if not href:
                    continue
                
                # Skip certain types of links
                if href.startswith(('javascript:', 'mailto:', 'tel:', 'ftp:')):
                    continue
                
                # Resolve relative URLs
                if base_url and not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                
                # Validate URL
                if not self.validate_url(href):
                    continue
                
                link_data = {
                    'url': href,
                    'text': self.clean_text(element.get_text()) if element.name == 'a' else '',
                    'tag': element.name,
                    'attributes': dict(element.attrs),
                }
                
                # Add additional info for different tag types
                if element.name == 'a':
                    link_data['title'] = element.get('title', '')
                    link_data['rel'] = element.get('rel', [])
                    link_data['target'] = element.get('target', '')
                
                links.append(link_data)
        
        return links
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text from main content areas first
        main_content = ""
        for selector in ['main', 'article', '[role="main"]', '.content', '#content']:
            main_element = soup.select_one(selector)
            if main_element:
                main_content = main_element.get_text()
                break
        
        # If no main content found, use body
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text()
        
        return self.clean_text(main_content)
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD, microdata, etc.)"""
        structured_data = []
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string)
                structured_data.append({
                    'type': 'json-ld',
                    'data': data
                })
            except Exception as e:
                logger.warning(f"Error parsing JSON-LD: {e}")
        
        # Microdata (basic extraction)
        items = soup.find_all(attrs={'itemscope': True})
        for item in items:
            item_data = {
                'type': 'microdata',
                'itemtype': item.get('itemtype', ''),
                'properties': {}
            }
            
            # Extract properties
            props = item.find_all(attrs={'itemprop': True})
            for prop in props:
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or self.clean_text(prop.get_text())
                item_data['properties'][prop_name] = prop_value
            
            structured_data.append(item_data)
        
        return structured_data
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str = None) -> List[Dict[str, Any]]:
        """Extract image information"""
        images = []
        
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src')
            if not src:
                continue
            
            # Resolve relative URLs
            if base_url and not src.startswith(('http://', 'https://')):
                src = urljoin(base_url, src)
            
            image_data = {
                'src': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'attributes': dict(img.attrs),
            }
            
            images.append(image_data)
        
        return images
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information"""
        forms = []
        
        form_tags = soup.find_all('form')
        for form in form_tags:
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'enctype': form.get('enctype', ''),
                'fields': []
            }
            
            # Extract form fields
            inputs = form.find_all(['input', 'textarea', 'select'])
            for input_field in inputs:
                field_data = {
                    'type': input_field.get('type', input_field.name),
                    'name': input_field.get('name', ''),
                    'id': input_field.get('id', ''),
                    'value': input_field.get('value', ''),
                    'required': input_field.has_attr('required'),
                    'attributes': dict(input_field.attrs),
                }
                form_data['fields'].append(field_data)
            
            forms.append(form_data)
        
        return forms
