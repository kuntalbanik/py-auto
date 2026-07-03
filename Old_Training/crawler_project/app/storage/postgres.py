import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncpg

from app.config import config
from app.models.page import Page, PageStatus
from app.models.version import PageVersion
from app.models.job import Job, JobStatus, JobType


logger = logging.getLogger(__name__)


class PostgreSQLStorage:
    """PostgreSQL storage backend for crawler data"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.connection_string = config.database_url
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            
            await self._create_tables()
            logger.info("PostgreSQL storage initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL storage: {e}")
            raise
    
    async def close(self):
        """Close database connection"""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL storage closed")
    
    async def _create_tables(self):
        """Create database tables"""
        
        # Pages table
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                content TEXT,
                content_type TEXT,
                status_code INTEGER,
                headers JSONB,
                title TEXT,
                description TEXT,
                extracted_links JSONB,
                extracted_data JSONB,
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                fetched_at TIMESTAMP WITH TIME ZONE,
                parsed_at TIMESTAMP WITH TIME ZONE
            )
        """)
        
        # Page versions table
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS page_versions (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                content TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                changes_detected BOOLEAN DEFAULT FALSE,
                diff_summary TEXT,
                UNIQUE (url, version_number)
            )
        """)
        
        # Jobs table
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                url TEXT,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                started_at TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                error_message TEXT,
                result JSONB,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3
            )
        """)
        
        # Create indexes
        await self.pool.execute("CREATE INDEX IF NOT EXISTS idx_pages_status ON pages(status)")
        await self.pool.execute("CREATE INDEX IF NOT EXISTS idx_pages_created_at ON pages(created_at)")
        await self.pool.execute("CREATE INDEX IF NOT EXISTS idx_page_versions_url ON page_versions(url)")
        await self.pool.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
        await self.pool.execute("CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs(priority DESC)")
        await self.pool.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at)")
    
    # Page operations
    async def save_page(self, page: Page) -> bool:
        """Save a page to the database"""
        try:
            await self.pool.execute("""
                INSERT INTO pages (
                    url, status, content, content_type, status_code,
                    headers, title, description, extracted_links,
                    extracted_data, error_message, created_at,
                    updated_at, fetched_at, parsed_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (url) DO UPDATE SET
                    status = EXCLUDED.status,
                    content = EXCLUDED.content,
                    content_type = EXCLUDED.content_type,
                    status_code = EXCLUDED.status_code,
                    headers = EXCLUDED.headers,
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    extracted_links = EXCLUDED.extracted_links,
                    extracted_data = EXCLUDED.extracted_data,
                    error_message = EXCLUDED.error_message,
                    updated_at = EXCLUDED.updated_at,
                    fetched_at = EXCLUDED.fetched_at,
                    parsed_at = EXCLUDED.parsed_at
            """, 
                page.url, page.status.value, page.content, page.content_type,
                page.status_code, json.dumps(page.headers) if page.headers else None,
                page.title, page.description, json.dumps(page.extracted_links) if page.extracted_links else None,
                json.dumps(page.extracted_data) if page.extracted_data else None,
                page.error_message, page.created_at, page.updated_at,
                page.fetched_at, page.parsed_at
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving page {page.url}: {e}")
            return False
    
    async def get_page(self, url: str) -> Optional[Page]:
        """Get a page from the database"""
        try:
            row = await self.pool.fetchrow("SELECT * FROM pages WHERE url = $1", url)
            if row:
                return self._row_to_page(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting page {url}: {e}")
            return None
    
    async def update_page_status(self, url: str, status: PageStatus, error_message: str = None) -> bool:
        """Update page status"""
        try:
            await self.pool.execute("""
                UPDATE pages SET 
                    status = $1, 
                    error_message = $2,
                    updated_at = NOW()
                WHERE url = $3
            """, status.value, error_message, url)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating page status {url}: {e}")
            return False
    
    async def get_pages_by_status(self, status: PageStatus, limit: int = 100) -> List[Page]:
        """Get pages by status"""
        try:
            rows = await self.pool.fetch(
                "SELECT * FROM pages WHERE status = $1 ORDER BY created_at DESC LIMIT $2",
                status.value, limit
            )
            
            return [self._row_to_page(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting pages by status {status}: {e}")
            return []
    
    # Page version operations
    async def save_page_version(self, version: PageVersion) -> bool:
        """Save a page version"""
        try:
            await self.pool.execute("""
                INSERT INTO page_versions (
                    url, content_hash, content, version_number,
                    created_at, changes_detected, diff_summary
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (url, version_number) DO UPDATE SET
                    content_hash = EXCLUDED.content_hash,
                    content = EXCLUDED.content,
                    changes_detected = EXCLUDED.changes_detected,
                    diff_summary = EXCLUDED.diff_summary
            """,
                version.url, version.content_hash, version.content,
                version.version_number, version.created_at,
                version.changes_detected, version.diff_summary
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving page version {version.url}: {e}")
            return False
    
    async def get_latest_version(self, url: str) -> Optional[PageVersion]:
        """Get the latest version of a page"""
        try:
            row = await self.pool.fetchrow("""
                SELECT * FROM page_versions 
                WHERE url = $1 
                ORDER BY version_number DESC 
                LIMIT 1
            """, url)
            
            if row:
                return self._row_to_version(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest version {url}: {e}")
            return None
    
    async def get_version_count(self, url: str) -> int:
        """Get the number of versions for a page"""
        try:
            result = await self.pool.fetchval(
                "SELECT COUNT(*) FROM page_versions WHERE url = $1", url
            )
            return result or 0
            
        except Exception as e:
            logger.error(f"Error getting version count {url}: {e}")
            return 0
    
    # Job operations
    async def save_job(self, job: Job) -> bool:
        """Save a job to the database"""
        try:
            await self.pool.execute("""
                INSERT INTO jobs (
                    id, url, job_type, status, priority,
                    created_at, started_at, completed_at,
                    error_message, result, retry_count, max_retries
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    started_at = EXCLUDED.started_at,
                    completed_at = EXCLUDED.completed_at,
                    error_message = EXCLUDED.error_message,
                    result = EXCLUDED.result,
                    retry_count = EXCLUDED.retry_count
            """,
                job.id, job.url, job.job_type.value, job.status.value,
                job.priority, job.created_at, job.started_at,
                job.completed_at, job.error_message,
                json.dumps(job.result) if job.result else None,
                job.retry_count, job.max_retries
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving job {job.id}: {e}")
            return False
    
    async def get_next_job(self, job_type: JobType = None) -> Optional[Job]:
        """Get the next job to process"""
        try:
            query = """
                SELECT * FROM jobs 
                WHERE status = $1 
            """
            params = [JobStatus.PENDING.value]
            
            if job_type:
                query += " AND job_type = $2"
                params.append(job_type.value)
            
            query += " ORDER BY priority DESC, created_at ASC LIMIT 1"
            
            row = await self.pool.fetchrow(query, *params)
            
            if row:
                return self._row_to_job(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting next job: {e}")
            return None
    
    async def update_job_status(self, job_id: str, status: JobStatus, 
                              error_message: str = None, result: Dict[str, Any] = None) -> bool:
        """Update job status"""
        try:
            query = """
                UPDATE jobs SET 
                    status = $1,
                    error_message = $2,
                    result = $3
            """
            params = [status.value, error_message, json.dumps(result) if result else None]
            
            if status == JobStatus.RUNNING:
                query += ", started_at = NOW()"
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                query += ", completed_at = NOW()"
            
            query += " WHERE id = $" + str(len(params) + 1)
            params.append(job_id)
            
            await self.pool.execute(query, *params)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating job status {job_id}: {e}")
            return False
    
    # Statistics
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            page_stats = await self.pool.fetchrow("""
                SELECT 
                    COUNT(*) as total_pages,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_pages,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_pages,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_pages
                FROM pages
            """)
            
            job_stats = await self.pool.fetchrow("""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_jobs,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_jobs
                FROM jobs
            """)
            
            version_stats = await self.pool.fetchrow("""
                SELECT 
                    COUNT(DISTINCT url) as pages_with_versions,
                    COUNT(*) as total_versions,
                    AVG(version_count) as avg_versions_per_page
                FROM (
                    SELECT url, COUNT(*) as version_count
                    FROM page_versions
                    GROUP BY url
                ) version_counts
            """)
            
            return {
                'pages': dict(page_stats) if page_stats else {},
                'jobs': dict(job_stats) if job_stats else {},
                'versions': dict(version_stats) if version_stats else {},
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    # Helper methods
    def _row_to_page(self, row) -> Page:
        """Convert database row to Page object"""
        return Page(
            url=row['url'],
            status=PageStatus(row['status']),
            content=row['content'],
            content_type=row['content_type'],
            status_code=row['status_code'],
            headers=dict(row['headers']) if row['headers'] else None,
            title=row['title'],
            description=row['description'],
            extracted_links=row['extracted_links'] if row['extracted_links'] else [],
            extracted_data=dict(row['extracted_data']) if row['extracted_data'] else None,
            error_message=row['error_message'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            fetched_at=row['fetched_at'],
            parsed_at=row['parsed_at'],
        )
    
    def _row_to_version(self, row) -> PageVersion:
        """Convert database row to PageVersion object"""
        return PageVersion(
            url=row['url'],
            content_hash=row['content_hash'],
            content=row['content'],
            version_number=row['version_number'],
            created_at=row['created_at'],
            changes_detected=row['changes_detected'],
            diff_summary=row['diff_summary'],
        )
    
    def _row_to_job(self, row) -> Job:
        """Convert database row to Job object"""
        return Job(
            id=row['id'],
            url=row['url'],
            job_type=JobType(row['job_type']),
            status=JobStatus(row['status']),
            priority=row['priority'],
            created_at=row['created_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at'],
            error_message=row['error_message'],
            result=dict(row['result']) if row['result'] else None,
            retry_count=row['retry_count'],
            max_retries=row['max_retries'],
        )
