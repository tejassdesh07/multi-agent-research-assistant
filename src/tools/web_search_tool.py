from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import time
import re


class WebSearchTool:
    def __init__(self, max_results: int = 10, rate_limit: int = 10):
        self.max_results = max_results
        self.rate_limit = rate_limit
        self.request_timestamps = []
        self.blocked_domains = ["spam.com", "malware.com"]
        
    def _check_rate_limit(self) -> bool:
        current_time = time.time()
        self.request_timestamps = [ts for ts in self.request_timestamps if current_time - ts < 60]
        
        if len(self.request_timestamps) >= self.rate_limit:
            return False
            
        self.request_timestamps.append(current_time)
        return True
    
    def _is_safe_url(self, url: str) -> bool:
        for domain in self.blocked_domains:
            if domain in url:
                return False
        return True
    
    def _sanitize_query(self, query: str) -> str:
        query = re.sub(r'[<>\"\'%;()&+]', '', query)
        return query.strip()
    
    def search(self, query: str, num_results: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded. Please wait before making more requests.")
        
        query = self._sanitize_query(query)
        num_results = num_results or self.max_results
        
        results = []
        try:
            with DDGS() as ddgs:
                search_results = ddgs.text(
                    query,
                    max_results=min(num_results, self.max_results)
                )
                
                for result in search_results:
                    url = result.get('href', '')
                    
                    if self._is_safe_url(url):
                        results.append({
                            'title': result.get('title', ''),
                            'url': url,
                            'snippet': result.get('body', ''),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'duckduckgo'
                        })
        
        except Exception as e:
            pass
            
        return results
    
    def fetch_content(self, url: str, max_length: int = 5000) -> Optional[str]:
        if not self._is_safe_url(url):
            return None
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
            
        except Exception as e:
            return None


from crewai_tools import tool


@tool("search_web")
def search_web_tool(query: str) -> str:
    """Search the web for information on a given topic."""
    search_tool = WebSearchTool(max_results=8)
    results = search_tool.search(query)
    return json.dumps(results, indent=2)


@tool("fetch_webpage")
def fetch_webpage_tool(url: str) -> str:
    """Fetch and extract content from a specific webpage URL."""
    search_tool = WebSearchTool()
    content = search_tool.fetch_content(url)
    
    if content:
        return content
    else:
        return "Failed to fetch content from the URL."

