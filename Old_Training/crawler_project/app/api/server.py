import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, HttpUrl
import uvicorn

from app.config import config
from app.models.page import PageStatus
from app.scheduler.frontier import URLFrontier
from app.storage.postgres import PostgreSQLStorage
from app.storage.file_store import FileStore


logger = logging.getLogger(__name__)


# Pydantic models
class URLRequest(BaseModel):
    url: str
    priority: Optional[int] = None


class CrawlRequest(BaseModel):
    urls: List[str]
    priority: Optional[int] = None


class PageResponse(BaseModel):
    url: str
    status: str
    title: Optional[str] = None
    description: Optional[str] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None


class StatsResponse(BaseModel):
    pages: Dict[str, Any]
    jobs: Optional[Dict[str, Any]] = None
    frontier: Optional[Dict[str, Any]] = None


# Create FastAPI app
app = FastAPI(
    title="Web Crawler API",
    description="API for managing and monitoring web crawler",
    version="1.0.0"
)

# Global state
_frontier: Optional[URLFrontier] = None
_db_storage: Optional[PostgreSQLStorage] = None


def set_dependencies(frontier: URLFrontier, db_storage: PostgreSQLStorage = None):
    """Set global dependencies"""
    global _frontier, _db_storage
    _frontier = frontier
    _db_storage = db_storage


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Web Crawler API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "frontier": bool(_frontier),
        "database": bool(_db_storage),
    }


@app.post("/crawl")
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Add URLs to crawl"""
    if not _frontier:
        raise HTTPException(status_code=503, detail="Frontier not available")
    
    added_count = 0
    for url in request.urls:
        success = await _frontier.add_url(url, priority=request.priority)
        if success:
            added_count += 1
    
    return {
        "message": f"Added {added_count} URLs to crawl queue",
        "total_urls": len(request.urls),
        "added": added_count,
    }


@app.post("/crawl/single")
async def crawl_single(request: URLRequest):
    """Add single URL to crawl"""
    if not _frontier:
        raise HTTPException(status_code=503, detail="Frontier not available")
    
    success = await _frontier.add_url(request.url, priority=request.priority)
    
    if success:
        return {"message": "URL added to crawl queue", "url": request.url}
    else:
        raise HTTPException(status_code=400, detail="URL already in queue or invalid")


@app.get("/pages", response_model=List[PageResponse])
async def get_pages(
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get crawled pages"""
    if not _db_storage:
        raise HTTPException(status_code=503, detail="Database not available")
    
    if status:
        try:
            page_status = PageStatus(status)
            pages = await _db_storage.get_pages_by_status(page_status, limit)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    else:
        # Get all pages (simplified, you might want pagination)
        pages = await _db_storage.get_pages_by_status(PageStatus.COMPLETED, limit)
    
    return [
        PageResponse(
            url=page.url,
            status=page.status.value,
            title=page.title,
            description=page.description,
            status_code=page.status_code,
            error_message=page.error_message,
            created_at=page.created_at.isoformat() if page.created_at else None,
        )
        for page in pages
    ]


@app.get("/pages/{url:path}")
async def get_page(url: str):
    """Get specific page details"""
    if not _db_storage:
        raise HTTPException(status_code=503, detail="Database not available")
    
    page = await _db_storage.get_page(url)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {
        "url": page.url,
        "status": page.status.value,
        "title": page.title,
        "description": page.description,
        "content_type": page.content_type,
        "status_code": page.status_code,
        "headers": page.headers,
        "extracted_links": page.extracted_links,
        "extracted_data": page.extracted_data,
        "error_message": page.error_message,
        "created_at": page.created_at.isoformat() if page.created_at else None,
        "fetched_at": page.fetched_at.isoformat() if page.fetched_at else None,
        "parsed_at": page.parsed_at.isoformat() if page.parsed_at else None,
    }


@app.get("/stats")
async def get_stats():
    """Get crawler statistics"""
    stats = {}
    
    if _db_storage:
        try:
            db_stats = await _db_storage.get_stats()
            stats.update(db_stats)
        except Exception as e:
            logger.error(f"Error getting DB stats: {e}")
    
    if _frontier:
        stats['frontier'] = _frontier.get_stats()
    
    return stats


@app.get("/queue")
async def get_queue_status():
    """Get crawl queue status"""
    if not _frontier:
        raise HTTPException(status_code=503, detail="Frontier not available")
    
    return {
        "queue_size": _frontier.get_queue_size(),
        "is_empty": _frontier.is_empty(),
        "stats": _frontier.get_stats(),
    }


@app.delete("/queue")
async def clear_queue():
    """Clear crawl queue"""
    if not _frontier:
        raise HTTPException(status_code=503, detail="Frontier not available")
    
    await _frontier.clear()
    return {"message": "Queue cleared"}


@app.get("/content/{url:path}")
async def get_content(url: str):
    """Get raw content for a URL"""
    file_store = FileStore()
    data = await file_store.load_html(url)
    
    if not data:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {
        "url": data.get('url'),
        "content_length": len(data.get('content', '')),
        "metadata": data.get('metadata'),
        "saved_at": data.get('saved_at'),
    }


def run_api_server(frontier: URLFrontier = None, db_storage: PostgreSQLStorage = None):
    """Run the API server"""
    set_dependencies(frontier, db_storage)
    
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level="info",
    )
