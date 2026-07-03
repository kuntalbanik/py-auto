from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class JobType(Enum):
    FETCH = "fetch"
    PARSE = "parse"
    FULL_CRAWL = "full_crawl"


@dataclass
class Job:
    id: str
    url: Optional[str] = None
    job_type: JobType = JobType.FETCH
    status: JobStatus = JobStatus.PENDING
    priority: int = 0
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.result is None:
            self.result = {}
    
    def start(self):
        """Mark job as started"""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def complete(self, result: Optional[Dict[str, Any]] = None):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if result:
            self.result.update(result)
    
    def fail(self, error_message: str):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.retry_count < self.max_retries
    
    def retry(self):
        """Increment retry count and reset status"""
        if self.can_retry():
            self.retry_count += 1
            self.status = JobStatus.PENDING
            self.error_message = None
            self.started_at = None
            self.completed_at = None
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'url': self.url,
            'job_type': self.job_type.value,
            'status': self.status.value,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'result': self.result,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        # Convert string enums back to enum objects
        if 'job_type' in data and isinstance(data['job_type'], str):
            data['job_type'] = JobType(data['job_type'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = JobStatus(data['status'])
        
        # Convert ISO strings back to datetime objects
        for field in ['created_at', 'started_at', 'completed_at']:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)
