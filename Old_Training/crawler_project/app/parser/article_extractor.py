import re
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class ArticleExtractor:
    """Extracts main article content from web pages"""
    
    def __init__(self):
        # Common content selectors in order of preference
        self.content_selectors = [
            'article',
            '[role="main"]',
            'main',
            '.content',
            '#content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.story-content',
            '.post-body',
            '.entry-body',
            '.article-body',
            '.post',
            '.entry',
            '.story',
            '.article',
            '.main-content',
            '#main-content',
            '.page-content',
            '#page-content',
            '.post-content-wrapper',
            '.entry-content-wrapper',
            '.article-content-wrapper',
        ]
        
        # Title selectors
        self.title_selectors = [
            'h1',
            '.title',
            '#title',
            '.post-title',
            '#post-title',
            '.entry-title',
            '#entry-title',
            '.article-title',
            '#article-title',
            '.headline',
            '#headline',
            '[property="og:title"]',
            '[name="twitter:title"]',
        ]
        
        # Author selectors
        self.author_selectors = [
            '.author',
            '#author',
            '.by-author',
            '.post-author',
            '.entry-author',
            '.article-author',
            '.byline',
            '.writer',
            '[rel="author"]',
            '[property="article:author"]',
            '[name="author"]',
        ]
        
        # Date selectors
        self.date_selectors = [
            '.date',
            '#date',
            '.published',
            '.post-date',
            '.entry-date',
            '.article-date',
            '.publish-date',
            '.timestamp',
            'time[datetime]',
            '[property="article:published_time"]',
            '[name="date"]',
            '[name="publication-date"]',
        ]
        
        # Elements to remove from content
        self.remove_selectors = [
            'nav',
            'header',
            'footer',
            'aside',
            '.sidebar',
            '#sidebar',
            '.navigation',
            '#navigation',
            '.menu',
            '#menu',
            '.comments',
            '#comments',
            '.comment-form',
            '#comment-form',
            '.related-posts',
            '#related-posts',
            '.social-share',
            '#social-share',
            '.advertisement',
            '.ads',
            '.popup',
            '.modal',
            'script',
            'style',
            'noscript',
            '.hidden',
            '[style*="display:none"]',
            '[style*="display: none"]',
        ]
        
        # Low-quality content indicators
        self.low_quality_patterns = [
            r'^\s*$',
            r'^\d+\s*(words|characters)\s*$',
            r'^\s*\d{1,2}\s*words\s*$',
            r'^\s*\d{1,2}\s*chars\s*$',
            r'^\s*continue reading\s*$',
            r'^\s*read more\s*$',
            r'^\s*click here\s*$',
        ]
    
    async def extract_article(self, html_content: str, url: str = None) -> Dict[str, Any]:
        """Extract article content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract author
            author = self._extract_author(soup)
            
            # Extract publish date
            publish_date = self._extract_date(soup)
            
            # Extract main content
            content, content_element = self._extract_main_content(soup)
            
            # Extract summary/lead paragraph
            summary = self._extract_summary(content_element)
            
            # Extract images from content
            images = self._extract_content_images(content_element, url)
            
            # Extract links from content
            links = self._extract_content_links(content_element, url)
            
            # Calculate content quality metrics
            quality_metrics = self._calculate_quality_metrics(content, content_element)
            
            result = {
                'title': title,
                'author': author,
                'publish_date': publish_date,
                'content': content,
                'summary': summary,
                'images': images,
                'links': links,
                'quality_metrics': quality_metrics,
                'extractor': 'article_extractor',
            }
            
            logger.debug(f"Extracted article from {url}: {len(content)} chars, quality: {quality_metrics.get('score', 0)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {e}")
            return {
                'error': str(e),
                'extractor': 'article_extractor',
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try specific selectors first
        for selector in self.title_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '')
                else:
                    title = element.get_text().strip()
                
                if title and len(title) > 5:  # Reasonable title length
                    return title
        
        # Fallback to title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        return ""
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        for selector in self.author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    author = element.get('content', '')
                else:
                    author = element.get_text().strip()
                
                if author and len(author) > 2:
                    return author
        
        return ""
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract publish date"""
        for selector in self.date_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    date = element.get('content', '')
                elif element.name == 'time':
                    date = element.get('datetime', '') or element.get_text().strip()
                else:
                    date = element.get_text().strip()
                
                if date:
                    return date
        
        return ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> tuple[str, Optional[Tag]]:
        """Extract main content using various heuristics"""
        # Remove unwanted elements first
        for selector in self.remove_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Try specific content selectors
        for selector in self.content_selectors:
            element = soup.select_one(selector)
            if element:
                content = self._clean_content(element.get_text())
                if self._is_good_content(content):
                    return content, element
        
        # Fallback: find the element with most text
        best_element = None
        best_content = ""
        best_score = 0
        
        for element in soup.find_all(['div', 'section', 'article']):
            content = self._clean_content(element.get_text())
            score = self._score_content(content, element)
            
            if score > best_score:
                best_score = score
                best_content = content
                best_element = element
        
        if best_content and self._is_good_content(best_content):
            return best_content, best_element
        
        # Last resort: use body
        body = soup.find('body')
        if body:
            content = self._clean_content(body.get_text())
            return content, body
        
        return "", None
    
    def _extract_summary(self, content_element: Optional[Tag]) -> str:
        """Extract summary/lead paragraph"""
        if not content_element:
            return ""
        
        # Try to find first paragraph
        first_p = content_element.find('p')
        if first_p:
            summary = first_p.get_text().strip()
            if len(summary) > 20 and len(summary) < 300:  # Reasonable summary length
                return summary
        
        # Try to find any text before first heading
        text_parts = []
        for element in content_element.children:
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                break
            if hasattr(element, 'get_text'):
                text = element.get_text().strip()
                if text:
                    text_parts.append(text)
        
        summary = ' '.join(text_parts)
        if len(summary) > 20 and len(summary) < 300:
            return summary
        
        return ""
    
    def _extract_content_images(self, content_element: Optional[Tag], base_url: str = None) -> List[Dict[str, Any]]:
        """Extract images from content"""
        if not content_element:
            return []
        
        images = []
        img_tags = content_element.find_all('img')
        
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
            }
            images.append(image_data)
        
        return images
    
    def _extract_content_links(self, content_element: Optional[Tag], base_url: str = None) -> List[str]:
        """Extract links from content"""
        if not content_element:
            return []
        
        links = []
        a_tags = content_element.find_all('a', href=True)
        
        for a_tag in a_tags:
            href = a_tag['href']
            
            # Skip certain types of links
            if href.startswith(('javascript:', 'mailto:', 'tel:')):
                continue
            
            # Resolve relative URLs
            if base_url and not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            links.append(href)
        
        return links
    
    def _clean_content(self, content: str) -> str:
        """Clean content text"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common boilerplate
        boilerplate_patterns = [
            r'\bclick here\b',
            r'\bread more\b',
            r'\bcontinue reading\b',
            r'\bsubscribe\b',
            r'\bnewsletter\b',
            r'\badvertisement\b',
            r'\bsponsored\b',
        ]
        
        for pattern in boilerplate_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def _score_content(self, content: str, element: Tag) -> float:
        """Score content quality"""
        if not content:
            return 0
        
        score = 0
        
        # Length score
        length = len(content)
        if length > 200:
            score += min(length / 100, 10)
        
        # Paragraph count
        paragraphs = element.find_all('p')
        score += len(paragraphs) * 2
        
        # Contains headings
        headings = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        score += len(headings) * 3
        
        # Contains lists
        lists = element.find_all(['ul', 'ol'])
        score += len(lists) * 1.5
        
        # Penalize short paragraphs
        short_paragraphs = sum(1 for p in paragraphs if len(p.get_text()) < 50)
        score -= short_paragraphs * 0.5
        
        # Bonus for common content indicators
        content_classes = element.get('class', [])
        if any(cls in content_classes for cls in ['content', 'article', 'post', 'entry', 'story']):
            score += 5
        
        return score
    
    def _is_good_content(self, content: str) -> bool:
        """Check if content is good quality"""
        if not content or len(content) < 100:
            return False
        
        # Check against low-quality patterns
        for pattern in self.low_quality_patterns:
            if re.match(pattern, content, re.IGNORECASE):
                return False
        
        # Check word count
        words = content.split()
        if len(words) < 20:
            return False
        
        # Check character-to-word ratio (should be reasonable)
        if len(content) / len(words) < 3:  # Average word length too short
            return False
        
        return True
    
    def _calculate_quality_metrics(self, content: str, element: Optional[Tag]) -> Dict[str, Any]:
        """Calculate content quality metrics"""
        if not content:
            return {'score': 0, 'word_count': 0, 'paragraph_count': 0}
        
        words = content.split()
        paragraphs = content.split('\n\n') if element else []
        
        # Calculate quality score (0-100)
        score = 0
        
        # Base score for length
        if len(words) > 50:
            score += 20
        if len(words) > 200:
            score += 20
        if len(words) > 500:
            score += 10
        
        # Paragraph structure
        if len(paragraphs) > 2:
            score += 10
        
        # Readability approximation
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        if 4 <= avg_word_length <= 7:
            score += 10
        
        # Content diversity (unique words ratio)
        unique_words = set(word.lower() for word in words)
        if words:
            diversity = len(unique_words) / len(words)
            if diversity > 0.3:
                score += 10
        
        return {
            'score': min(score, 100),
            'word_count': len(words),
            'character_count': len(content),
            'paragraph_count': len(paragraphs),
            'avg_word_length': avg_word_length,
            'vocabulary_diversity': len(unique_words) / len(words) if words else 0,
        }
