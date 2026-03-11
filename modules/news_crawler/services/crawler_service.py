"""
Crawler service layer.
Manages triggering of news and skills crawlers.
"""

import os
import sys
import subprocess
from threading import Thread
from config import PROJECT_ROOT


def start_news_crawl():
    """Start the news crawler in a background thread."""
    def run_crawl():
        try:
            if PROJECT_ROOT not in sys.path:
                sys.path.insert(0, PROJECT_ROOT)
            from fetch_news import fetch_news
            fetch_news()
        except Exception as e:
            print(f"News crawl failed: {e}")

    thread = Thread(target=run_crawl, daemon=True)
    thread.start()


def start_skills_crawl():
    """Start the skills crawler via subprocess."""
    script_path = os.path.join(PROJECT_ROOT, 'fetch_skills.py')
    subprocess.Popen([sys.executable, script_path], cwd=PROJECT_ROOT)
