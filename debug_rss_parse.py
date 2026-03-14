#!/usr/bin/env python3
"""
调试 RSS 解析，查看实际返回的数据
"""
import feedparser

test_urls = [
    "https://www.leiphone.com/category/ai",  # AI 科技评论
    "https://www.jiqizhixin.com/rss",  # 机器之心
    "https://www.deeptechchina.com/feed",  # DeepTech
]

for url in test_urls:
    print(f"\n{'=' * 80}")
    print(f"测试：{url}")
    print(f"{'=' * 80}")
    
    try:
        feed = feedparser.parse(url)
        print(f"Entries: {len(feed.entries)}")
        
        if feed.entries:
            first = feed.entries[0]
            print(f"\n第一篇文章字段:")
            print(f"  title: {first.get('title', 'N/A')[:50]}")
            print(f"  link: {first.get('link', 'N/A')[:80]}")
            print(f"  summary: {first.get('summary', 'N/A')[:100] if first.get('summary') else 'N/A'}")
            print(f"  content: {first.content[0].get('value', 'N/A')[:100] if hasattr(first, 'content') and first.content else 'N/A'}")
            print(f"  description: {first.get('description', 'N/A')[:100] if first.get('description') else 'N/A'}")
            print(f"  content_encoded: {first.get('content_encoded', 'N/A')[:100] if first.get('content_encoded') else 'N/A'}")
            print(f"  keys: {list(first.keys())}")
    except Exception as e:
        print(f"Error: {e}")
