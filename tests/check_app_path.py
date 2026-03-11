#!/usr/bin/env python3
"""检查 app.py 的数据库路径"""
import os
import sqlite3

# 复制 app.py 的路径逻辑
def get_base_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if os.path.exists(os.path.join(current_dir, '版本历史')) or \
       os.path.exists(os.path.join(current_dir, '文档中心')):
        return current_dir
    
    linux_path = '/home/zhang/news_system'
    if os.path.exists(linux_path):
        return linux_path
    
    return current_dir

BASE_DIR = get_base_dir()
NEWS_DB = os.path.join(BASE_DIR, 'data', 'news.db')

print(f"BASE_DIR: {BASE_DIR}")
print(f"NEWS_DB: {NEWS_DB}")
print(f"文件存在：{os.path.exists(NEWS_DB)}")

# 测试查询
if os.path.exists(NEWS_DB):
    conn = sqlite3.connect(NEWS_DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM news")
    count = c.fetchone()[0]
    print(f"新闻数量：{count}")
    conn.close()
else:
    print("❌ 数据库文件不存在！")
