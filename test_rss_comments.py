#!/usr/bin/env python3
"""
测试 RSS 源中是否有评论数相关字段
"""
import feedparser
import requests

test_urls = [
    "https://news.ycombinator.com/rss",  # Hacker News 有 comments
    "https://www.qbitai.com/rss",  # 量子位
]

for url in test_urls:
    print(f"\n{'=' * 80}")
    print(f"测试：{url}")
    print(f"{'=' * 80}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=15)
        feed = feedparser.parse(resp.content)
        
        print(f"Entries: {len(feed.entries)}")
        
        if feed.entries:
            first = feed.entries[0]
            print(f"\n第一篇文章字段:")
            print(f"  title: {first.get('title', 'N/A')[:50]}")
            
            # 检查所有可能的评论数字段
            possible_comment_fields = [
                'comments', 'comment_count', 'num_comments', 'replies',
                'discussion_count', 'commentCount', 'total_comments'
            ]
            
            for field in possible_comment_fields:
                if hasattr(first, field):
                    value = getattr(first, field)
                    print(f"  ✓ {field}: {value}")
            
            # 检查是否有评论链接
            if hasattr(first, 'links') and first.links:
                for i, link in enumerate(first.links):
                    print(f"  link[{i}]: {link}")
            
            # 检查 media 相关字段
            if hasattr(first, 'media_content') and first.media_content:
                print(f"  media_content: {first.media_content}")
            
            # 打印所有 keys
            print(f"\n  所有字段：{list(first.keys())}")
            
    except Exception as e:
        print(f"Error: {e}")
