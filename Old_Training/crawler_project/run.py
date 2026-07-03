#!/usr/bin/env python3
"""
Web Crawler - Main Entry Point

This script provides multiple ways to run the crawler:
1. Direct crawl mode (default)
2. API server mode
"""

import asyncio
import argparse
import logging
import sys

from app.config import config
from app.main import CrawlerEngine, main as crawl_main
from app.api.server import run_api_server
from app.scheduler.frontier import URLFrontier
from app.storage.postgres import PostgreSQLStorage
from app.services.logger import setup_logging


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument(
        "--mode",
        choices=["crawl", "api", "both"],
        default="crawl",
        help="Run mode: crawl (default), api, or both",
    )
    parser.add_argument(
        "--url",
        action="append",
        help="Add URL(s) to crawl",
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="Number of fetch workers",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    return parser.parse_args()


async def run_crawl_mode(args):
    """Run in crawl mode"""
    logger = setup_logging(config.logs_dir)
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create engine
    engine = CrawlerEngine()
    
    try:
        # Initialize
        await engine.initialize()
        
        # Add custom URLs if provided
        if args.url:
            for url in args.url:
                await engine.add_url(url)
                logger.info(f"Added custom URL: {url}")
        
        # Update worker count if specified
        if args.workers:
            config.num_fetch_workers = args.workers
        
        # Start crawling
        await engine.start()
        
        # Keep running until interrupted
        logger.info("Crawler is running. Press Ctrl+C to stop.")
        while engine.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error in crawl mode: {e}")
    finally:
        await engine.stop()


def run_api_mode(args):
    """Run in API mode"""
    logger = setup_logging(config.logs_dir)
    logger.info("Starting API server...")
    
    # Setup dependencies
    frontier = URLFrontier()
    db_storage = PostgreSQLStorage()
    
    try:
        # Initialize
        asyncio.get_event_loop().run_until_complete(db_storage.initialize())
        asyncio.get_event_loop().run_until_complete(frontier.clear())
        
        # Add seed URLs
        frontier.add_seed_urls()
        
        # Update config
        config.api_host = args.host
        config.api_port = args.port
        
        # Run API server
        run_api_server(frontier, db_storage)
        
    except Exception as e:
        logger.error(f"Error in API mode: {e}")


async def run_both_modes(args):
    """Run both crawl and API modes"""
    logger = setup_logging(config.logs_dir)
    
    # Create engine
    engine = CrawlerEngine()
    
    try:
        # Initialize
        await engine.initialize()
        
        # Add custom URLs if provided
        if args.url:
            for url in args.url:
                await engine.add_url(url)
        
        # Update worker count if specified
        if args.workers:
            config.num_fetch_workers = args.workers
        
        # Update API config
        config.api_host = args.host
        config.api_port = args.port
        
        # Start crawling in background
        await engine.start()
        
        # Start API server (this will block)
        logger.info("Starting API server in both mode...")
        run_api_server(engine.frontier, engine.db_storage)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error in both modes: {e}")
    finally:
        await engine.stop()


def main():
    """Main entry point"""
    args = parse_args()
    
    if args.mode == "crawl":
        asyncio.run(run_crawl_mode(args))
    elif args.mode == "api":
        run_api_mode(args)
    elif args.mode == "both":
        asyncio.run(run_both_modes(args))
    else:
        print("Invalid mode. Use: crawl, api, or both")
        sys.exit(1)


if __name__ == "__main__":
    main()
