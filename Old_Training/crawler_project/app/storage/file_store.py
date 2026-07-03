import os
import json
import hashlib
import gzip
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from app.config import config


logger = logging.getLogger(__name__)


class FileStore:
    """File-based storage for HTML content and snapshots"""
    
    def __init__(self):
        self.raw_html_dir = Path(config.raw_html_dir)
        self.snapshots_dir = Path(config.snapshots_dir)
        
        # Create directories if they don't exist
        self.raw_html_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, url: str, content_type: str = 'html') -> Path:
        """Generate file path for URL"""
        # Create hash of URL for filename
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        
        # Create subdirectories based on hash prefix
        prefix = url_hash[:2]
        
        if content_type == 'html':
            return self.raw_html_dir / prefix / f"{url_hash}.html.gz"
        elif content_type == 'snapshot':
            return self.snapshots_dir / prefix / f"{url_hash}.json.gz"
        else:
            return self.raw_html_dir / prefix / f"{url_hash}.txt.gz"
    
    async def save_html(self, url: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Save HTML content to file"""
        try:
            file_path = self._get_file_path(url, 'html')
            
            # Create subdirectory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data to save
            data = {
                'url': url,
                'content': content,
                'metadata': metadata or {},
                'saved_at': datetime.utcnow().isoformat(),
            }
            
            # Compress and save
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Saved HTML to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving HTML for {url}: {e}")
            return False
    
    async def load_html(self, url: str) -> Optional[Dict[str, Any]]:
        """Load HTML content from file"""
        try:
            file_path = self._get_file_path(url, 'html')
            
            if not file_path.exists():
                return None
            
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"Loaded HTML from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading HTML for {url}: {e}")
            return None
    
    async def save_snapshot(self, url: str, snapshot_data: Dict[str, Any]) -> bool:
        """Save page snapshot to file"""
        try:
            file_path = self._get_file_path(url, 'snapshot')
            
            # Create subdirectory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data to save
            data = {
                'url': url,
                'snapshot': snapshot_data,
                'saved_at': datetime.utcnow().isoformat(),
            }
            
            # Compress and save
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Saved snapshot to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving snapshot for {url}: {e}")
            return False
    
    async def load_snapshot(self, url: str) -> Optional[Dict[str, Any]]:
        """Load page snapshot from file"""
        try:
            file_path = self._get_file_path(url, 'snapshot')
            
            if not file_path.exists():
                return None
            
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"Loaded snapshot from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading snapshot for {url}: {e}")
            return None
    
    def file_exists(self, url: str, content_type: str = 'html') -> bool:
        """Check if file exists for URL"""
        file_path = self._get_file_path(url, content_type)
        return file_path.exists()
    
    def get_file_size(self, url: str, content_type: str = 'html') -> int:
        """Get file size for URL"""
        file_path = self._get_file_path(url, content_type)
        return file_path.stat().st_size if file_path.exists() else 0
    
    def get_file_modified_time(self, url: str, content_type: str = 'html') -> Optional[datetime]:
        """Get file modification time"""
        file_path = self._get_file_path(url, content_type)
        if file_path.exists():
            timestamp = file_path.stat().st_mtime
            return datetime.fromtimestamp(timestamp)
        return None
    
    async def delete_file(self, url: str, content_type: str = 'html') -> bool:
        """Delete file for URL"""
        try:
            file_path = self._get_file_path(url, content_type)
            
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted file {file_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file for {url}: {e}")
            return False
    
    async def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            # Clean raw HTML files
            for file_path in self.raw_html_dir.rglob('*.gz'):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            
            # Clean snapshot files
            for file_path in self.snapshots_dir.rglob('*.gz'):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {
                'raw_html_files': 0,
                'raw_html_size': 0,
                'snapshot_files': 0,
                'snapshot_size': 0,
                'total_files': 0,
                'total_size': 0,
            }
            
            # Count raw HTML files
            for file_path in self.raw_html_dir.rglob('*.gz'):
                stats['raw_html_files'] += 1
                stats['raw_html_size'] += file_path.stat().st_size
            
            # Count snapshot files
            for file_path in self.snapshots_dir.rglob('*.gz'):
                stats['snapshot_files'] += 1
                stats['snapshot_size'] += file_path.stat().st_size
            
            # Calculate totals
            stats['total_files'] = stats['raw_html_files'] + stats['snapshot_files']
            stats['total_size'] = stats['raw_html_size'] + stats['snapshot_size']
            
            # Convert sizes to human readable format
            for key in ['raw_html_size', 'snapshot_size', 'total_size']:
                stats[key] = self._format_size(stats[key])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    async def export_data(self, export_path: str, include_content: bool = True) -> bool:
        """Export all data to a single file"""
        try:
            export_data = {
                'export_info': {
                    'exported_at': datetime.utcnow().isoformat(),
                    'include_content': include_content,
                    'total_files': 0,
                },
                'files': []
            }
            
            # Export raw HTML files
            for file_path in self.raw_html_dir.rglob('*.gz'):
                try:
                    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                        file_data = json.load(f)
                    
                    if not include_content:
                        file_data['content'] = '[CONTENT_REMOVED]'
                        file_data['metadata'] = '[METADATA_REMOVED]'
                    
                    export_data['files'].append(file_data)
                    export_data['export_info']['total_files'] += 1
                    
                except Exception as e:
                    logger.warning(f"Error exporting file {file_path}: {e}")
            
            # Export snapshot files
            for file_path in self.snapshots_dir.rglob('*.gz'):
                try:
                    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                        file_data = json.load(f)
                    
                    if not include_content:
                        file_data['snapshot'] = '[SNAPSHOT_REMOVED]'
                    
                    export_data['files'].append(file_data)
                    export_data['export_info']['total_files'] += 1
                    
                except Exception as e:
                    logger.warning(f"Error exporting snapshot {file_path}: {e}")
            
            # Save export file
            with gzip.open(export_path, 'wt', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {export_data['export_info']['total_files']} files to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False
