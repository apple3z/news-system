#!/usr/bin/env python3
"""
测试 feedparser 解析 RSS，查看所有可用字段
"""
import feedparser
import json

print("=" * 80)
print("测试 feedparser 解析 RSS 源")
print("=" * 80)

# 测试几个RSS源
test_urls = [
    "https://36kr.com/feed",
    "https://www.huxiu.com/rss",
    "https://www.jiqizhixin.com/rss",
    "https://www.qbitai.com/rss"
]

for url in test_urls[:1]:  # 先测试一个
    print(f"\n{'=' * 80}")
    print(f"解析: {url}")
    print(f"{'=' * 80}")
    
    try:
        feed = feedparser.parse(url)
        
        print(f"\nFeed 级别的字段:")
        print(f"  feed keys: {list(feed.keys())}")
        print(f"  feed.feed keys: {list(feed.feed.keys())}")
        print(f"  文章数量: {len(feed.entries)}")
        
        if feed.entries:
            first_entry = feed.entries[0]
            print(f"\n第一篇文章的所有字段:")
            print(f"  entry keys: {list(first_entry.keys())}")
            
            print(f"\n第一篇文章的详细内容:")
            for key, value in first_entry.items():
                if key == 'content' and value:
                    print(f"\n  {key}:")
                    print(f"    类型: {type(value)}")
                    if isinstance(value, list):
                        for i, item in enumerate(value):
                            print(f"    [{i}] type: {item.get('type')}")
                            print(f"    [{i}] value (前300字符): {repr(item.get('value', '')[:300])}")
                elif key in ['summary', 'description']:
                    print(f"\n  {key}:")
                    print(f"    {repr(str(value)[:300])}")
                else:
                    print(f"\n  {key}: {repr(value)[:200]}")
            
            # 看看有没有缩略图
            print(f"\n\n寻找缩略图相关字段:")
            if 'media_thumbnail' in first_entry:
                print(f"  ✓ media_thumbnail: {first_entry.media_thumbnail}")
            if 'enclosures' in first_entry and first_entry.enclosures:
                print(f"  ✓ enclosures:")
                for i, enc in enumerate(first_entry.enclosures):
                    print(f"    [{i}]: {enc}")
            if 'links' in first_entry:
                print(f"  ✓ links:")
                for i, link in enumerate(first_entry.links):
                    print(f"    [{i}]: {link}")
            
            # 测试提取content
            print(f"\n\n测试提取内容:")
            content = ''
            if hasattr(first_entry, 'content') and first_entry.content:
                content = first_entry.content[0].value
            elif hasattr(first_entry, 'summary') and first_entry.summary:
                content = first_entry.summary
            print(f"  提取的内容长度: {len(content)}")
            print(f"  内容前500字符: {repr(content[:500])}")
            
    except Exception as e:
        print(f"  错误: {e}")
        import traceback
        traceback.print_exc()
