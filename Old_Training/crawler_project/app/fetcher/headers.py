import random
from typing import Dict, List, Optional


class HeaderManager:
    """Manages HTTP headers for web crawling"""
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]
        
        self.accept_languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9,en-US;q=0.8",
            "en;q=0.9",
        ]
        
        self.accept_encodings = [
            "gzip, deflate, br",
            "gzip, deflate",
            "br, gzip, deflate",
        ]
    
    def get_random_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """Generate random headers for a request"""
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(self.accept_languages),
            "Accept-Encoding": random.choice(self.accept_encodings),
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
        
        if referer:
            headers["Referer"] = referer
        
        return headers
    
    def get_api_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": random.choice(self.accept_languages),
            "Accept-Encoding": random.choice(self.accept_encodings),
            "Content-Type": "application/json",
            "DNT": "1",
            "Connection": "keep-alive",
        }
    
    def get_image_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """Get headers for image requests"""
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": random.choice(self.accept_languages),
            "Accept-Encoding": random.choice(self.accept_encodings),
            "DNT": "1",
            "Connection": "keep-alive",
        }
        
        if referer:
            headers["Referer"] = referer
        
        return headers
    
    def add_custom_headers(self, base_headers: Dict[str, str], custom_headers: Dict[str, str]) -> Dict[str, str]:
        """Add custom headers to base headers"""
        headers = base_headers.copy()
        headers.update(custom_headers)
        return headers
    
    def validate_headers(self, headers: Dict[str, str]) -> bool:
        """Validate headers for common issues"""
        required_headers = ["User-Agent", "Accept"]
        
        for header in required_headers:
            if header not in headers:
                return False
        
        # Check User-Agent format
        user_agent = headers.get("User-Agent", "")
        if not user_agent or len(user_agent) < 10:
            return False
        
        return True
