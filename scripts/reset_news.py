#!/usr/bin/env python3
"""重置新闻数据库并重新采集"""

import sqlite3
import os
from path_utils import NEWS_DB, ensure_data_dir

ensure_data_dir()

print("="*50)
print("重置新闻数据库")
print("="*50)

# 清空新闻表
conn = sqlite3.connect(NEWS_DB)
c = conn.cursor()
c.execute("DELETE FROM news")
c.execute("DELETE FROM sqlite_sequence WHERE name='news'")
conn.commit()
print("✅ 新闻表已清空")
conn.close()

print("\n现在开始采集新闻...")
print("="*50)

# 执行采集
import fetch_news
fetch_news.fetch_news()

print("\n" + "="*50)
print("✅ 重置完成！")
print("="*50)
