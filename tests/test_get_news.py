#!/usr/bin/env python3
"""测试 app.py 的 get_db_news 函数"""
import sys
sys.path.insert(0, '.')

# 导入 app.py 中的函数
exec(open('app.py', encoding='utf-8').read().split('app = Flask')[0])

# 测试 get_db_news
print("测试 get_db_news()...")
news_list = get_db_news(limit=10)
print(f"获取到 {len(news_list)} 条新闻")

if news_list:
    print(f"\n第一条新闻:")
    first = news_list[0]
    for key, value in first.items():
        print(f"  {key}: {str(value)[:50]}")
else:
    print("❌ 没有获取到新闻")
