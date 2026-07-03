import hashlib
import re
from typing import Set, Dict, Any, Optional, List
from urllib.parse import urlparse
import logging

from app.storage.cache import cache


logger = logging.getLogger(__name__)


class URLDeduper:
    """Deduplicates URLs and detects duplicate content"""
    
    def __init__(self):
        self.url_cache: Set[str] = set()
        self.content_cache: Dict[str, str] = {}  # hash -> url
        self.similarity_threshold = 0.8  # Content similarity threshold
    
    async def is_duplicate_url(self, url: str) -> bool:
        """Check if URL has been processed before"""
        try:
            # Normalize URL first
            normalized_url = self._normalize_url(url)
            
            # Check in-memory cache
            if normalized_url in self.url_cache:
                return True
            
            # Check persistent cache
            cached = await cache.get(f"url_seen:{normalized_url}")
            if cached:
                self.url_cache.add(normalized_url)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking duplicate URL {url}: {e}")
            return False
    
    async def mark_url_seen(self, url: str) -> bool:
        """Mark URL as seen"""
        try:
            normalized_url = self._normalize_url(url)
            
            # Add to in-memory cache
            self.url_cache.add(normalized_url)
            
            # Add to persistent cache (30 days TTL)
            await cache.set(f"url_seen:{normalized_url}", True, ttl=2592000)
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking URL as seen {url}: {e}")
            return False
    
    async def is_duplicate_content(self, content: str, url: str = None) -> tuple[bool, Optional[str]]:
        """Check if content is duplicate"""
        try:
            if not content or len(content.strip()) < 50:
                return False, None
            
            content_hash = self._generate_content_hash(content)
            
            # Check exact hash match
            if content_hash in self.content_cache:
                return True, self.content_cache[content_hash]
            
            # Check cache
            cached_url = await cache.get(f"content_hash:{content_hash}")
            if cached_url:
                self.content_cache[content_hash] = cached_url
                return True, cached_url
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking duplicate content: {e}")
            return False, None
    
    async def mark_content_seen(self, content: str, url: str) -> bool:
        """Mark content as seen"""
        try:
            if not content or len(content.strip()) < 50:
                return False
            
            content_hash = self._generate_content_hash(content)
            
            # Add to in-memory cache
            self.content_cache[content_hash] = url
            
            # Add to persistent cache (7 days TTL)
            await cache.set(f"content_hash:{content_hash}", url, ttl=604800)
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking content as seen: {e}")
            return False
    
    async def find_similar_content(self, content: str, url: str = None, 
                                 max_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar content using fuzzy matching"""
        try:
            if not content or len(content.strip()) < 100:
                return []
            
            # Generate content signature
            signature = self._generate_content_signature(content)
            
            # Search for similar signatures in cache
            similar_results = []
            
            # This is a simplified implementation
            # In practice, you might use more sophisticated similarity algorithms
            cache_key = f"similar:{signature[:16]}"  # Use prefix for similarity search
            
            cached_similar = await cache.get(cache_key)
            if cached_similar:
                for item in cached_similar:
                    similarity = self._calculate_similarity(content, item.get('content', ''))
                    if similarity >= self.similarity_threshold:
                        similar_results.append({
                            'url': item.get('url'),
                            'similarity': similarity,
                            'signature': item.get('signature'),
                        })
            
            # Sort by similarity and limit results
            similar_results.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_results[:max_results]
            
        except Exception as e:
            logger.error(f"Error finding similar content: {e}")
            return []
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        try:
            parsed = urlparse(url.lower())
            
            # Remove fragment
            parsed = parsed._replace(fragment='')
            
            # Remove common tracking parameters
            query_params = []
            if parsed.query:
                for param in parsed.query.split('&'):
                    if not any(tracker in param.lower() for tracker in [
                        'utm_', 'fbclid', 'gclid', 'msclkid', '_ga', '_gid',
                        'sessionid', 'csrf', 'token', 'ref', 'source'
                    ]):
                        query_params.append(param)
            
            query = '&'.join(query_params) if query_params else ''
            parsed = parsed._replace(query=query)
            
            return parsed.geturl()
            
        except Exception:
            return url.lower()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content deduplication"""
        # Clean content first
        cleaned_content = self._clean_content_for_hash(content)
        return hashlib.sha256(cleaned_content.encode('utf-8')).hexdigest()
    
    def _clean_content_for_hash(self, content: str) -> str:
        """Clean content for hashing"""
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common dynamic elements
        patterns_to_remove = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # Dates
            r'\b\d{2}:\d{2}:\d{2}\b',  # Times
            r'\b\d+,\d{3}\b',           # Numbers with commas
            r'\b\d+\s*(bytes|KB|MB|GB)\b',  # File sizes
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip().lower()
    
    def _generate_content_signature(self, content: str) -> str:
        """Generate content signature for similarity matching"""
        # Extract first 1000 characters after cleaning
        cleaned = self._clean_content_for_hash(content)
        return hashlib.md5(cleaned[:1000].encode('utf-8')).hexdigest()
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings"""
        try:
            # Simple similarity using common words
            words1 = set(self._clean_content_for_hash(content1).split())
            words2 = set(self._clean_content_for_hash(content2).split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception:
            return 0.0
    
    async def get_deduplication_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        try:
            return {
                'urls_cached': len(self.url_cache),
                'content_hashes_cached': len(self.content_cache),
                'cache_type': 'memory',
            }
        except Exception as e:
            logger.error(f"Error getting deduplication stats: {e}")
            return {}
    
    async def clear_cache(self) -> bool:
        """Clear deduplication cache"""
        try:
            self.url_cache.clear()
            self.content_cache.clear()
            logger.info("Deduplication cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing deduplication cache: {e}")
            return False


class ContentDeduper:
    """Advanced content deduplication with multiple strategies"""
    
    def __init__(self):
        self.url_deduper = URLDeduper()
        self.min_content_length = 100
        self.similarity_strategies = ['hash', 'signature', 'shingle']
    
    async def should_process_content(self, url: str, content: str) -> tuple[bool, Dict[str, Any]]:
        """Determine if content should be processed"""
        try:
            result = {
                'should_process': True,
                'reason': 'new_content',
                'duplicate_url': None,
                'duplicate_content_url': None,
                'similarity_score': 0.0,
            }
            
            # Check URL duplication
            if await self.url_deduper.is_duplicate_url(url):
                result['should_process'] = False
                result['reason'] = 'duplicate_url'
                return False, result
            
            # Check content length
            if len(content.strip()) < self.min_content_length:
                result['reason'] = 'content_too_short'
                return True, result  # Still process short content
            
            # Check content duplication
            is_duplicate, duplicate_url = await self.url_deduper.is_duplicate_content(content, url)
            if is_duplicate:
                result['should_process'] = False
                result['reason'] = 'duplicate_content'
                result['duplicate_content_url'] = duplicate_url
                return False, result
            
            # Check for similar content
            similar_content = await self.url_deduper.find_similar_content(content, url, max_results=3)
            if similar_content:
                result['similar_content'] = similar_content
                result['similarity_score'] = similar_content[0]['similarity']
                
                # If very similar, might skip
                if similar_content[0]['similarity'] > 0.95:
                    result['should_process'] = False
                    result['reason'] = 'very_similar_content'
                    return False, result
            
            return True, result
            
        except Exception as e:
            logger.error(f"Error determining if should process content: {e}")
            return True, {'should_process': True, 'reason': 'error', 'error': str(e)}
    
    async def mark_processed(self, url: str, content: str) -> bool:
        """Mark URL and content as processed"""
        try:
            # Mark URL as seen
            await self.url_deduper.mark_url_seen(url)
            
            # Mark content as seen
            await self.url_deduper.mark_content_seen(content, url)
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking content as processed: {e}")
            return False
    
    async def find_duplicates(self, content: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Find duplicate or similar content"""
        try:
            duplicates = []
            
            # Exact duplicates
            is_duplicate, duplicate_url = await self.url_deduper.is_duplicate_content(content)
            if is_duplicate and duplicate_url:
                duplicates.append({
                    'url': duplicate_url,
                    'type': 'exact',
                    'similarity': 1.0,
                })
            
            # Similar content
            similar_content = await self.url_deduper.find_similar_content(content, max_results=max_results)
            for item in similar_content:
                duplicates.append({
                    'url': item['url'],
                    'type': 'similar',
                    'similarity': item['similarity'],
                })
            
            return duplicates[:max_results]
            
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return []


# Global deduper instances
url_deduper = URLDeduper()
content_deduper = ContentDeduper()
