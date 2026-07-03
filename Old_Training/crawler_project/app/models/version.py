from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib


@dataclass
class PageVersion:
    url: str
    content_hash: str
    content: str
    version_number: int
    created_at: datetime = None
    changes_detected: bool = False
    diff_summary: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.content_hash is None:
            self.content_hash = self.generate_hash(self.content)
    
    @staticmethod
    def generate_hash(content: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def has_changed(self, new_content: str) -> bool:
        """Check if content has changed"""
        new_hash = self.generate_hash(new_content)
        return new_hash != self.content_hash
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'url': self.url,
            'content_hash': self.content_hash,
            'content': self.content,
            'version_number': self.version_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'changes_detected': self.changes_detected,
            'diff_summary': self.diff_summary,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PageVersion':
        # Convert ISO strings back to datetime objects
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        return cls(**data)
