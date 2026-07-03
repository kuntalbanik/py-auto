# Web Crawler Project

A production-grade web crawler built with Python, featuring async fetching, JavaScript rendering support, structured data extraction, and a REST API.

## Features

- **Async HTTP Fetching**: High-performance concurrent URL fetching using aiohttp
- **JavaScript Rendering**: Playwright support for dynamic content
- **Smart Scheduling**: Priority-based URL frontier with robots.txt compliance
- **Content Parsing**: HTML parsing with BeautifulSoup, article extraction, structured data parsing
- **Change Detection**: Track and detect content changes over time
- **Deduplication**: URL and content deduplication to avoid redundant work
- **Storage**: PostgreSQL for metadata, file system for content snapshots, optional Redis caching
- **REST API**: FastAPI-based API for managing and monitoring the crawler
- **Extensible**: Modular architecture for easy extension

## Project Structure

```
crawler_project/
│
├── app/
│   ├── main.py                  # Main orchestration engine
│   ├── config.py                # Configuration management
│   │
│   ├── scheduler/
│   │   ├── frontier.py          # URL frontier and queue management
│   │   ├── priority.py          # URL priority calculation
│   │   └── robots.py            # robots.txt handling
│   │
│   ├── fetcher/
│   │   ├── http_fetcher.py      # Async HTTP fetching
│   │   ├── playwright_fetcher.py # JavaScript rendering
│   │   └── headers.py           # HTTP header management
│   │
│   ├── parser/
│   │   ├── base.py              # Base parser interface
│   │   ├── html_parser.py       # HTML content parsing
│   │   ├── article_extractor.py # Article content extraction
│   │   ├── structured_data.py   # JSON-LD and microdata parsing
│   │   └── fallback_extractors.py # Fallback extraction methods
│   │
│   ├── storage/
│   │   ├── postgres.py          # PostgreSQL database storage
│   │   ├── file_store.py        # File-based content storage
│   │   └── cache.py             # Cache management (Redis/Memory)
│   │
│   ├── models/
│   │   ├── page.py              # Page data model
│   │   ├── version.py           # Page version tracking
│   │   └── job.py               # Job/task model
│   │
│   ├── services/
│   │   ├── change_detector.py   # Content change detection
│   │   ├── deduper.py           # URL/content deduplication
│   │   ├── canonicalizer.py     # URL normalization
│   │   ├── selector_manager.py  # CSS selector management
│   │   └── logger.py            # Logging setup
│   │
│   └── api/
│       └── server.py            # FastAPI REST endpoints
│
├── workers/
│   ├── fetch_worker.py          # Fetch worker implementation
│   └── parse_worker.py          # Parse worker implementation
│
├── utils/
│   └── helpers.py               # Utility functions
│
├── data/
│   ├── raw_html/                # Raw HTML storage
│   └── snapshots/               # Parsed snapshot storage
│
├── logs/                        # Log files
│
├── tests/                       # Test suite
│
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── run.py                       # Main entry point

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Set environment variables or modify `app/config.py`:

```bash
export DATABASE_URL="postgresql://user:password@localhost/crawler_db"
export REDIS_URL="redis://localhost:6379"
export MAX_CONCURRENT_REQUESTS="10"
export NUM_FETCH_WORKERS="3"
export NUM_PARSE_WORKERS="2"
```

### 3. Run the Crawler

#### Crawl Mode (default)

```bash
python run.py
```

#### With Custom URLs

```bash
python run.py --mode crawl --url "https://example.com" --url "https://example.org" --workers 5
```

#### API Mode

```bash
python run.py --mode api --host 0.0.0.0 --port 8000
```

#### Both Modes (Crawl + API)

```bash
python run.py --mode both --url "https://example.com"
```

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /crawl` - Add URLs to crawl queue
- `POST /crawl/single` - Add single URL
- `GET /pages` - List crawled pages
- `GET /pages/{url}` - Get specific page details
- `GET /stats` - Get crawler statistics
- `GET /queue` - Get queue status
- `DELETE /queue` - Clear crawl queue
- `GET /content/{url}` - Get raw content

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://user:password@localhost/crawler_db` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `MAX_CONCURRENT_REQUESTS` | `10` | Max concurrent HTTP requests |
| `REQUEST_DELAY` | `1.0` | Delay between requests (seconds) |
| `TIMEOUT` | `30` | Request timeout (seconds) |
| `NUM_FETCH_WORKERS` | `3` | Number of fetch workers |
| `NUM_PARSE_WORKERS` | `2` | Number of parse workers |
| `CACHE_TTL` | `3600` | Cache TTL (seconds) |
| `USER_AGENT` | Mozilla/5.0 (compatible; WebCrawler/1.0) | User agent string |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |

## License

MIT License

## Bash Commands

### Install dependencies
pip install -r requirements.txt

### Run crawler
python run.py

### With custom URLs
python run.py --url "https://example.com" --workers 5

### API mode
python run.py --mode api

### Both
python run.py --mode both --url "https://example.com"
