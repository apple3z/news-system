#!/usr/bin/env python3
"""
兼容入口 - 实际逻辑已迁移到 modules/news_crawler/crawlers/fetch_news.py

根目录保留此文件是为了兼容直接运行 `python fetch_news.py` 的场景。
crawler_service.py 已改为直接导入模块版本。
"""

from modules.news_crawler.crawlers.fetch_news import *  # noqa: F401,F403

if __name__ == "__main__":
    print("=" * 50)
    print("新闻采集与分析系统")
    print("=" * 50)
    fetch_news()
