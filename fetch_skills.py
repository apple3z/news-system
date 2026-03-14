#!/usr/bin/env python3
"""兼容入口 - 实际逻辑已迁移到 modules/news_crawler/crawlers/fetch_skills.py"""
from modules.news_crawler.crawlers.fetch_skills import fetch_skills  # noqa: F401

if __name__ == "__main__":
    print("=" * 50)
    print("Skills Crawler (redirect to module version)")
    print("=" * 50)
    fetch_skills()
