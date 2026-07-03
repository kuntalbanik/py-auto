from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class PageStatus(Enum):
    PENDING = "pending"
    FETCHING = "fetching"
    FETCHED = "fetched"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


@dataclass
class Page:
    url: str
    status: PageStatus = PageStatus.PENDING
    content: Optional[str] = None
    content_type: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    extracted_links: Optional[list] = None
    extracted_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    fetched_at: Optional[datetime] = None
    parsed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.extracted_links is None:
            self.extracted_links = []
        if self.extracted_data is None:
            self.extracted_data = {}
        if self.headers is None:
            self.headers = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'url': self.url,
            'status': self.status.value,
            'content': self.content,
            'content_type': self.content_type,
            'status_code': self.status_code,
            'headers': self.headers,
            'title': self.title,
            'description': self.description,
            'extracted_links': self.extracted_links,
            'extracted_data': self.extracted_data,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'parsed_at': self.parsed_at.isoformat() if self.parsed_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Page':
        # Convert string status back to enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = PageStatus(data['status'])
        
        # Convert ISO strings back to datetime objects
        for field in ['created_at', 'updated_at', 'fetched_at', 'parsed_at']:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)
