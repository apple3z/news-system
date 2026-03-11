#!/usr/bin/env python3
"""测试新闻入库"""
import sqlite3
import os
from fetch_news import init_db, fetch_163

# 检查数据库路径
print("检查数据库路径...")
print(f"当前目录：{os.getcwd()}")
print(f"数据库文件：{os.path.abspath('data/news.db')}")
print(f"文件存在：{os.path.exists('data/news.db')}")

# 测试插入一条数据
print("\n测试插入数据...")
conn = init_db()
c = conn.cursor()

# 插入测试数据
test_news = {
    'title': '测试新闻标题',
    'link': 'https://example.com/test',
    'source': '测试来源'
}

try:
    c.execute('''INSERT OR REPLACE INTO news 
        (title, link, source, category, time, summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (test_news['title'], test_news['link'], test_news['source'], 
         'AI/科技', '2026-03-10', '这是测试摘要', '2026-03-10 12:00:00'))
    conn.commit()
    print("✅ 插入成功")
    
    # 验证
    c.execute("SELECT COUNT(*) FROM news")
    count = c.fetchone()[0]
    print(f"数据库新闻总数：{count}")
    
    # 查询刚插入的数据
    c.execute("SELECT title FROM news WHERE link = ?", (test_news['link'],))
    row = c.fetchone()
    if row:
        print(f"✅ 查询成功：{row[0]}")
    else:
        print("❌ 查询失败：找不到刚插入的数据")
        
except Exception as e:
    print(f"❌ 插入失败：{e}")
finally:
    conn.close()
