import json
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class StructuredDataParser:
    """Extracts structured data from web pages"""
    
    def __init__(self):
        self.json_ld_selectors = [
            'script[type="application/ld+json"]',
        ]
        
        self.microdata_selectors = [
            '[itemscope]',
        ]
        
        self.rdfa_selectors = [
            '[property]',
            '[typeof]',
        ]
    
    async def extract_structured_data(self, html_content: str, url: str = None) -> Dict[str, Any]:
        """Extract all structured data from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            result = {
                'json_ld': [],
                'microdata': [],
                'rdfa': [],
                'opengraph': {},
                'twitter_cards': {},
                'meta_tags': {},
                'total_items': 0,
            }
            
            # Extract JSON-LD
            result['json_ld'] = self._extract_json_ld(soup)
            
            # Extract Microdata
            result['microdata'] = self._extract_microdata(soup)
            
            # Extract RDFa
            result['rdfa'] = self._extract_rdfa(soup)
            
            # Extract Open Graph
            result['opengraph'] = self._extract_opengraph(soup)
            
            # Extract Twitter Cards
            result['twitter_cards'] = self._extract_twitter_cards(soup)
            
            # Extract other meta tags
            result['meta_tags'] = self._extract_meta_tags(soup)
            
            # Count total items
            result['total_items'] = (
                len(result['json_ld']) + 
                len(result['microdata']) + 
                len(result['rdfa']) +
                len(result['opengraph']) +
                len(result['twitter_cards'])
            )
            
            logger.debug(f"Extracted structured data from {url}: {result['total_items']} items")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting structured data from {url}: {e}")
            return {
                'error': str(e),
                'parser': 'structured_data',
            }
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data"""
        json_ld_data = []
        
        scripts = soup.select('script[type="application/ld+json"]')
        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string.strip())
                    if isinstance(data, list):
                        json_ld_data.extend(data)
                    else:
                        json_ld_data.append(data)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON-LD: {e}")
            except Exception as e:
                logger.warning(f"Error parsing JSON-LD: {e}")
        
        return json_ld_data
    
    def _extract_microdata(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Microdata"""
        microdata = []
        
        items = soup.find_all(attrs={'itemscope': True})
        for item in items:
            item_data = {
                'itemtype': item.get('itemtype', ''),
                'itemid': item.get('itemid', ''),
                'properties': {},
            }
            
            # Extract properties
            props = item.find_all(attrs={'itemprop': True})
            for prop in props:
                prop_name = prop.get('itemprop')
                
                # Get property value
                if prop.name in ['meta', 'link', 'audio', 'embed', 'iframe', 'img', 'source', 'track', 'video']:
                    value = prop.get('content', '') or prop.get('href', '') or prop.get('src', '')
                elif prop.name == 'time':
                    value = prop.get('datetime', '') or prop.get_text().strip()
                elif prop.name == 'data':
                    value = prop.get('value', '') or prop.get_text().strip()
                else:
                    value = prop.get_text().strip()
                
                if prop_name and value:
                    if prop_name not in item_data['properties']:
                        item_data['properties'][prop_name] = []
                    item_data['properties'][prop_name].append(value)
            
            # Convert single-item lists to strings
            for prop_name, values in item_data['properties'].items():
                if len(values) == 1:
                    item_data['properties'][prop_name] = values[0]
            
            if item_data['itemtype'] or item_data['properties']:
                microdata.append(item_data)
        
        return microdata
    
    def _extract_rdfa(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract RDFa data"""
        rdfa_data = []
        
        # Find elements with typeof attribute
        typeof_elements = soup.find_all(attrs={'typeof': True})
        for element in typeof_elements:
            rdfa_item = {
                'typeof': element.get('typeof', ''),
                'about': element.get('about', ''),
                'properties': {},
            }
            
            # Find property elements
            prop_elements = element.find_all(attrs={'property': True})
            for prop in prop_elements:
                prop_name = prop.get('property')
                
                if prop.name == 'meta':
                    value = prop.get('content', '')
                elif prop.name == 'link':
                    value = prop.get('href', '')
                elif prop.name == 'time':
                    value = prop.get('datetime', '') or prop.get_text().strip()
                else:
                    value = prop.get_text().strip()
                
                if prop_name and value:
                    rdfa_item['properties'][prop_name] = value
            
            if rdfa_item['typeof'] or rdfa_item['properties']:
                rdfa_data.append(rdfa_item)
        
        return rdfa_data
    
    def _extract_opengraph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph meta tags"""
        og_data = {}
        
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        for tag in og_tags:
            property_name = tag.get('property', '')
            content = tag.get('content', '')
            
            if property_name and content:
                og_data[property_name] = content
        
        return og_data
    
    def _extract_twitter_cards(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Twitter Card meta tags"""
        twitter_data = {}
        
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '')
            content = tag.get('content', '')
            
            if name and content:
                twitter_data[name] = content
        
        return twitter_data
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract other important meta tags"""
        meta_data = {}
        
        # Standard meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property') or tag.get('http-equiv')
            content = tag.get('content', '')
            
            if name and content and not name.startswith(('og:', 'twitter:')):
                meta_data[name] = content
        
        return meta_data
    
    def get_article_info(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract article-specific information from structured data"""
        article_info = {}
        
        # Check JSON-LD for article data
        for item in structured_data.get('json_ld', []):
            if isinstance(item, dict):
                item_type = item.get('@type', '')
                if isinstance(item_type, list):
                    item_type = item_type[0] if item_type else ''
                
                if 'article' in item_type.lower() or 'newsarticle' in item_type.lower():
                    article_info.update({
                        'title': item.get('headline', ''),
                        'author': item.get('author', ''),
                        'publish_date': item.get('datePublished', ''),
                        'modified_date': item.get('dateModified', ''),
                        'description': item.get('description', ''),
                        'publisher': item.get('publisher', {}).get('name', '') if isinstance(item.get('publisher'), dict) else '',
                        'image': item.get('image', {}).get('url', '') if isinstance(item.get('image'), dict) else item.get('image', ''),
                    })
                    break
        
        # Check Open Graph for article data
        og_data = structured_data.get('opengraph', {})
        if not article_info.get('title') and og_data.get('og:title'):
            article_info['title'] = og_data['og:title']
        
        if not article_info.get('description') and og_data.get('og:description'):
            article_info['description'] = og_data['og:description']
        
        if not article_info.get('image') and og_data.get('og:image'):
            article_info['image'] = og_data['og:image']
        
        if not article_info.get('publish_date') and og_data.get('article:published_time'):
            article_info['publish_date'] = og_data['article:published_time']
        
        if not article_info.get('modified_date') and og_data.get('article:modified_time'):
            article_info['modified_date'] = og_data['article:modified_time']
        
        # Check Twitter Cards
        twitter_data = structured_data.get('twitter_cards', {})
        if not article_info.get('title') and twitter_data.get('twitter:title'):
            article_info['title'] = twitter_data['twitter:title']
        
        if not article_info.get('description') and twitter_data.get('twitter:description'):
            article_info['description'] = twitter_data['twitter:description']
        
        if not article_info.get('image') and twitter_data.get('twitter:image'):
            article_info['image'] = twitter_data['twitter:image']
        
        return article_info
    
    def get_product_info(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product-specific information from structured data"""
        product_info = {}
        
        # Check JSON-LD for product data
        for item in structured_data.get('json_ld', []):
            if isinstance(item, dict):
                item_type = item.get('@type', '')
                if isinstance(item_type, list):
                    item_type = item_type[0] if item_type else ''
                
                if 'product' in item_type.lower():
                    product_info.update({
                        'name': item.get('name', ''),
                        'description': item.get('description', ''),
                        'price': item.get('offers', {}).get('price', '') if isinstance(item.get('offers'), dict) else '',
                        'currency': item.get('offers', {}).get('priceCurrency', '') if isinstance(item.get('offers'), dict) else '',
                        'availability': item.get('offers', {}).get('availability', '') if isinstance(item.get('offers'), dict) else '',
                        'brand': item.get('brand', {}).get('name', '') if isinstance(item.get('brand'), dict) else item.get('brand', ''),
                        'image': item.get('image', {}).get('url', '') if isinstance(item.get('image'), dict) else item.get('image', ''),
                    })
                    break
        
        return product_info
    
    def get_organization_info(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract organization-specific information from structured data"""
        org_info = {}
        
        # Check JSON-LD for organization data
        for item in structured_data.get('json_ld', []):
            if isinstance(item, dict):
                item_type = item.get('@type', '')
                if isinstance(item_type, list):
                    item_type = item_type[0] if item_type else ''
                
                if 'organization' in item_type.lower() or 'corporation' in item_type.lower():
                    org_info.update({
                        'name': item.get('name', ''),
                        'description': item.get('description', ''),
                        'url': item.get('url', ''),
                        'logo': item.get('logo', {}).get('url', '') if isinstance(item.get('logo'), dict) else item.get('logo', ''),
                        'contact_point': item.get('contactPoint', {}),
                        'address': item.get('address', {}),
                        'same_as': item.get('sameAs', []),
                    })
                    break
        
        return org_info
