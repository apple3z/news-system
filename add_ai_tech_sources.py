#!/usr/bin/env python3
"""
添加优质 AI 科技类订阅源
"""
import sqlite3
from path_utils import SUBSCRIBE_DB

conn = sqlite3.connect(SUBSCRIBE_DB)
c = conn.cursor()

# 创建表（如果不存在）
c.execute('''CREATE TABLE IF NOT EXISTS subscription (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    sub_type TEXT DEFAULT 'rss',
    check_interval INTEGER DEFAULT 3600,
    last_check TEXT,
    last_content TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT
)''')

# 优质 AI 科技类订阅源列表
new_sources = [
    # AI 类
    ("OpenAI Blog", "https://openai.com/blog/rss"),
    ("DeepMind", "https://deepmind.google/discover/blog/rss"),
    ("Anthropic", "https://www.anthropic.com/rss"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("MIT Technology Review - AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("AI News", "https://artificialintelligence-news.com/feed"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed"),
    
    # 科技类
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("TechCrunch", "https://techcrunch.com/feed"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("CNET", "https://www.cnet.com/rss/news"),
    
    # 国内优质源
    ("新智元", "https://www.jiqizhixin.com/rss"),
    ("AI 科技评论", "https://www.leiphone.com/category/ai"),
    ("机器之心 Pro", "https://www.jiqizhixin.com/pro/rss"),
    ("量子位 QbitAI", "https://www.qbitai.com/rss"),
    ("DeepTech 深科技", "https://www.deeptechchina.com/feed"),
    ("学术头条", "https://www.scipedia.cn/rss"),
    
    # 开发者类
    ("GitHub Blog", "https://github.blog/feed"),
    ("Stack Overflow Blog", "https://stackoverflow.blog/feed"),
    ("InfoQ", "https://www.infoq.com/feed"),
    (" Hacker News", "https://news.ycombinator.com/rss"),
]

# 检查是否已存在
c.execute("SELECT name, url FROM subscription")
existing = {(row[0], row[1]) for row in c.fetchall()}

added = 0
skipped = 0

for name, url in new_sources:
    if (name, url) in existing:
        print(f"⊘ 跳过：{name}")
        skipped += 1
        continue
    
    c.execute('''INSERT INTO subscription 
                 (name, url, sub_type, check_interval, is_active, created_at) 
                 VALUES (?, ?, 'rss', 3600, 1, datetime('now'))''',
              (name, url))
    print(f"✓ 添加：{name} - {url}")
    added += 1

conn.commit()
print(f"\n{'=' * 80}")
print(f"完成：新增 {added} 个订阅源，跳过 {skipped} 个已存在的源")
print(f"{'=' * 80}")

# 显示所有订阅源
c.execute("SELECT COUNT(*) FROM subscription WHERE is_active=1")
total = c.fetchone()[0]
print(f"当前活跃订阅源总数：{total}")

conn.close()
