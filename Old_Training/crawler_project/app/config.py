import os
from dataclasses import dataclass, field
from typing import List, Optional


def _get_seed_urls():
    env_urls = os.getenv("SEED_URLS")
    if env_urls:
        return env_urls.split(",")
    return [
        "https://example.com",
        "https://httpbin.org",
    ]


@dataclass
class Config:
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/crawler_db")
    
    # Redis settings (optional, for distributed queue)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Crawler settings
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    request_delay: float = float(os.getenv("REQUEST_DELAY", "1.0"))
    timeout: int = int(os.getenv("TIMEOUT", "30"))
    
    # Storage settings
    data_dir: str = os.getenv("DATA_DIR", "data")
    raw_html_dir: str = os.path.join(data_dir, "raw_html")
    snapshots_dir: str = os.path.join(data_dir, "snapshots")
    logs_dir: str = os.getenv("LOGS_DIR", "logs")
    
    # User agent and headers
    user_agent: str = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; WebCrawler/1.0)")
    
    # Seed URLs (use default_factory for mutable default)
    seed_urls: List[str] = field(default_factory=_get_seed_urls)
    
    # Allowed domains (empty means all domains allowed)
    allowed_domains: List[str] = field(default_factory=list)
    
    # API settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Worker settings
    num_fetch_workers: int = int(os.getenv("NUM_FETCH_WORKERS", "3"))
    num_parse_workers: int = int(os.getenv("NUM_PARSE_WORKERS", "2"))
    
    # Cache settings
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    def __post_init__(self):
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.raw_html_dir, exist_ok=True)
        os.makedirs(self.snapshots_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)


# Global config instance
config = Config()
