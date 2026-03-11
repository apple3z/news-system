"""
News Crawler & Info module.
Registers cross-module services with the proxy on import.
"""

from proxy.registry import register
from modules.news_crawler.services.news_service import search_by_keywords

# Register services available to other modules
register('news.search_by_keywords', search_by_keywords)
