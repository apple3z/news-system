#!/usr/bin/env python3
"""测试新闻详情获取"""
from fetch_news import get_detail

url = 'https://www.163.com/tech/article/KNJ7LMM900097U7T.html'
print(f'测试获取详情：{url}')
detail = get_detail(url)
print(f'摘要：{detail.get("summary", "无")[:50] if detail.get("summary") else "无"}')
print(f'图片：{detail.get("image", "无")}')
print(f'内容长度：{len(detail.get("content", ""))}')
print(f'详情：{detail}')
