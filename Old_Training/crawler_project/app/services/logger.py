import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_dir: str = "logs", level: int = logging.DEBUG) -> logging.Logger:
    """Setup comprehensive logging for the crawler"""
    
    # Create logs directory
    os.makedirs(log_dir, exist_ok=True)
    
    # Create timestamp for log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Main logger
    logger = logging.getLogger("crawler")
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"crawler_{timestamp}.log")
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Error log file
    error_handler = logging.FileHandler(
        os.path.join(log_dir, f"errors_{timestamp}.log")
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    logger.addHandler(error_handler)
    
    # Stats log file
    stats_handler = logging.FileHandler(
        os.path.join(log_dir, f"stats_{timestamp}.log")
    )
    stats_handler.setLevel(logging.INFO)
    stats_format = logging.Formatter('%(asctime)s - STATS - %(message)s')
    stats_handler.setFormatter(stats_format)
    logger.addHandler(stats_handler)
    
    return logger


def get_logger(name: str = "crawler") -> logging.Logger:
    """Get configured logger instance"""
    return logging.getLogger(name)
