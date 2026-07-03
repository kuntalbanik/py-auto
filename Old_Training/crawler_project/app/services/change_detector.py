import hashlib
import difflib
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from app.models.version import PageVersion
from app.storage.cache import cache


logger = logging.getLogger(__name__)


class ChangeDetector:
    """Detects changes in web page content"""
    
    def __init__(self):
        self.min_change_threshold = 10  # Minimum characters changed to consider it a change
        self.significant_change_ratio = 0.1  # 10% of content changed
    
    async def detect_changes(self, url: str, old_content: str, new_content: str) -> Tuple[bool, Dict[str, Any]]:
        """Detect if content has changed significantly"""
        try:
            if not old_content or not new_content:
                return True, {'reason': 'missing_content'}
            
            # Generate hashes
            old_hash = self._generate_hash(old_content)
            new_hash = self._generate_hash(new_content)
            
            # Quick hash comparison
            if old_hash == new_hash:
                return False, {'reason': 'identical_hash', 'change_score': 0.0}
            
            # Detailed comparison
            change_info = self._detailed_compare(old_content, new_content)
            
            # Determine if change is significant
            is_significant = self._is_significant_change(change_info)
            
            change_info.update({
                'old_hash': old_hash,
                'new_hash': new_hash,
                'is_significant': is_significant,
                'detected_at': datetime.utcnow().isoformat(),
            })
            
            return is_significant, change_info
            
        except Exception as e:
            logger.error(f"Error detecting changes for {url}: {e}")
            return True, {'reason': 'error', 'error': str(e)}
    
    def _generate_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _detailed_compare(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Perform detailed content comparison"""
        
        # Basic statistics
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        # Line-based diff
        differ = difflib.unified_diff(
            old_lines, new_lines,
            fromfile='old', tofile='new',
            lineterm='', n=3
        )
        
        diff_lines = list(differ)
        diff_text = '\n'.join(diff_lines)
        
        # Calculate change metrics
        added_lines = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        # Character-level changes
        char_changes = len(new_content) - len(old_content)
        
        # Word-level changes
        old_words = set(old_content.lower().split())
        new_words = set(new_content.lower().split())
        
        added_words = len(new_words - old_words)
        removed_words = len(old_words - new_words)
        total_words = len(old_words.union(new_words))
        
        # Calculate change ratios
        total_lines = max(len(old_lines), len(new_lines))
        line_change_ratio = (added_lines + removed_lines) / total_lines if total_lines > 0 else 0
        
        word_change_ratio = (added_words + removed_words) / total_words if total_words > 0 else 0
        
        # Overall change score (0-1)
        change_score = max(line_change_ratio, word_change_ratio)
        
        # Generate summary
        summary = self._generate_change_summary(added_lines, removed_lines, added_words, removed_words)
        
        return {
            'change_score': change_score,
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'added_words': added_words,
            'removed_words': removed_words,
            'char_changes': char_changes,
            'line_change_ratio': line_change_ratio,
            'word_change_ratio': word_change_ratio,
            'diff_size': len(diff_text),
            'summary': summary,
            'diff_preview': diff_text[:1000] + '...' if len(diff_text) > 1000 else diff_text,
        }
    
    def _is_significant_change(self, change_info: Dict[str, Any]) -> bool:
        """Determine if change is significant"""
        change_score = change_info.get('change_score', 0)
        added_lines = change_info.get('added_lines', 0)
        removed_lines = change_info.get('removed_lines', 0)
        char_changes = abs(change_info.get('char_changes', 0))
        
        # Multiple criteria for significance
        criteria_met = 0
        
        # Change score threshold
        if change_score >= self.significant_change_ratio:
            criteria_met += 1
        
        # Minimum line changes
        if (added_lines + removed_lines) >= 5:
            criteria_met += 1
        
        # Minimum character changes
        if char_changes >= self.min_change_threshold:
            criteria_met += 1
        
        # Consider significant if at least 2 criteria met
        return criteria_met >= 2
    
    def _generate_change_summary(self, added_lines: int, removed_lines: int, 
                              added_words: int, removed_words: int) -> str:
        """Generate human-readable change summary"""
        parts = []
        
        if added_lines > 0 or removed_lines > 0:
            if added_lines > 0 and removed_lines > 0:
                parts.append(f"{added_lines} lines added, {removed_lines} lines removed")
            elif added_lines > 0:
                parts.append(f"{added_lines} lines added")
            else:
                parts.append(f"{removed_lines} lines removed")
        
        if added_words > 0 or removed_words > 0:
            if added_words > 0 and removed_words > 0:
                parts.append(f"{added_words} words added, {removed_words} words removed")
            elif added_words > 0:
                parts.append(f"{added_words} words added")
            else:
                parts.append(f"{removed_words} words removed")
        
        return '; '.join(parts) if parts else 'No significant changes'
    
    async def get_last_hash(self, url: str) -> Optional[str]:
        """Get last known hash for URL from cache"""
        try:
            cached_data = await cache.get(f"last_hash:{url}")
            return cached_data.get('hash') if cached_data else None
        except Exception as e:
            logger.error(f"Error getting last hash for {url}: {e}")
            return None
    
    async def save_last_hash(self, url: str, content_hash: str) -> bool:
        """Save last known hash for URL to cache"""
        try:
            data = {
                'hash': content_hash,
                'saved_at': datetime.utcnow().isoformat(),
            }
            return await cache.set(f"last_hash:{url}", data, ttl=86400)  # 24 hours
        except Exception as e:
            logger.error(f"Error saving last hash for {url}: {e}")
            return False
    
    async def should_process_url(self, url: str, content: str) -> Tuple[bool, Dict[str, Any]]:
        """Determine if URL should be processed based on changes"""
        try:
            # Get last known hash
            last_hash = await self.get_last_hash(url)
            current_hash = self._generate_hash(content)
            
            if not last_hash:
                # First time seeing this URL
                await self.save_last_hash(url, current_hash)
                return True, {'reason': 'first_time', 'hash': current_hash}
            
            if last_hash == current_hash:
                # No changes detected
                return False, {'reason': 'unchanged', 'hash': current_hash}
            
            # Content has changed, get detailed analysis
            # We need the old content for detailed comparison
            old_content_data = await cache.get(f"url:{url}")
            if old_content_data:
                old_content = old_content_data.get('content', '')
                has_changes, change_info = await self.detect_changes(url, old_content, content)
                
                if has_changes:
                    await self.save_last_hash(url, current_hash)
                    return True, change_info
                else:
                    return False, change_info
            else:
                # Old content not available, assume it's changed
                await self.save_last_hash(url, current_hash)
                return True, {'reason': 'old_content_missing', 'hash': current_hash}
                
        except Exception as e:
            logger.error(f"Error determining if should process {url}: {e}")
            return True, {'reason': 'error', 'error': str(e)}
    
    async def create_page_version(self, url: str, content: str, version_number: int = None) -> PageVersion:
        """Create a page version object"""
        try:
            content_hash = self._generate_hash(content)
            
            # Get version number if not provided
            if version_number is None:
                # This would typically come from database
                version_number = 1
            
            return PageVersion(
                url=url,
                content_hash=content_hash,
                content=content,
                version_number=version_number,
                created_at=datetime.utcnow(),
            )
            
        except Exception as e:
            logger.error(f"Error creating page version for {url}: {e}")
            raise
    
    def get_change_statistics(self, change_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get formatted change statistics"""
        return {
            'severity': self._get_change_severity(change_info.get('change_score', 0)),
            'impact': self._get_change_impact(change_info),
            'confidence': self._get_change_confidence(change_info),
            'recommendations': self._get_change_recommendations(change_info),
        }
    
    def _get_change_severity(self, change_score: float) -> str:
        """Get change severity level"""
        if change_score >= 0.5:
            return "major"
        elif change_score >= 0.2:
            return "moderate"
        elif change_score >= 0.1:
            return "minor"
        else:
            return "trivial"
    
    def _get_change_impact(self, change_info: Dict[str, Any]) -> str:
        """Get change impact assessment"""
        added_lines = change_info.get('added_lines', 0)
        removed_lines = change_info.get('removed_lines', 0)
        total_changes = added_lines + removed_lines
        
        if total_changes > 100:
            return "high"
        elif total_changes > 50:
            return "medium"
        elif total_changes > 10:
            return "low"
        else:
            return "minimal"
    
    def _get_change_confidence(self, change_info: Dict[str, Any]) -> str:
        """Get confidence in change detection"""
        change_score = change_info.get('change_score', 0)
        diff_size = change_info.get('diff_size', 0)
        
        if change_score > 0.3 and diff_size > 50:
            return "high"
        elif change_score > 0.1 and diff_size > 20:
            return "medium"
        else:
            return "low"
    
    def _get_change_recommendations(self, change_info: Dict[str, Any]) -> list:
        """Get recommendations based on change analysis"""
        recommendations = []
        
        change_score = change_info.get('change_score', 0)
        added_words = change_info.get('added_words', 0)
        removed_words = change_info.get('removed_words', 0)
        
        if change_score > 0.5:
            recommendations.append("Major content change detected - consider full reprocessing")
        
        if added_words > removed_words * 2:
            recommendations.append("Significant content addition - check for new sections")
        
        if removed_words > added_words * 2:
            recommendations.append("Significant content removal - check for deleted sections")
        
        if change_score < 0.1:
            recommendations.append("Minor change - incremental processing may be sufficient")
        
        return recommendations
