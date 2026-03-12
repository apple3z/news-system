#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有必要的数据库和表结构
"""

import sqlite3
import os
from datetime import datetime

# 创建 data 目录
os.makedirs('data', exist_ok=True)

print("=" * 50)
print("初始化数据库...")
print("=" * 50)

# ========== 1. 新闻数据库 ==========
print("\n[1/3] 初始化 news.db...")
conn = sqlite3.connect('data/news.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    link TEXT UNIQUE,
    source TEXT,
    author TEXT,
    category TEXT,
    time TEXT,
    summary TEXT,
    image TEXT,
    content TEXT,
    original_content TEXT,
    keywords TEXT,
    entities TEXT,
    sentiment TEXT,
    trend_level TEXT,
    hot_score INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS crawl_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    end_time TEXT,
    status TEXT,
    total_news_count INTEGER DEFAULT 0,
    new_news_count INTEGER DEFAULT 0,
    updated_news_count INTEGER DEFAULT 0,
    sources TEXT,
    error_message TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
)''')

conn.commit()
print("✓ news.db 创建成功")

# ========== 2. Skills 数据库 ==========
print("\n[2/3] 初始化 skills.db...")
conn2 = sqlite3.connect('data/skills.db')
c2 = conn2.cursor()

c2.execute('''CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    owner TEXT,
    title TEXT,
    description TEXT,
    source TEXT,
    url TEXT,
    download_url TEXT,
    github_url TEXT,
    category TEXT,
    tags TEXT,
    features TEXT,
    capabilities TEXT,
    skill_level TEXT,
    implementation TEXT,
    tech_stack TEXT,
    languages TEXT,
    frameworks TEXT,
    use_cases TEXT,
    scenarios TEXT,
    chinese_intro TEXT,
    readme_content TEXT,
    stars INTEGER,
    downloads INTEGER,
    created_at TEXT
)''')

conn2.commit()
print("✓ skills.db 创建成功")

# ========== 3. 订阅数据库 ==========
print("\n[3/3] 初始化 subscribe.db...")
conn3 = sqlite3.connect('data/subscribe.db')
c3 = conn3.cursor()

c3.execute('''CREATE TABLE IF NOT EXISTS subscription (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    sub_type TEXT DEFAULT 'website',
    check_interval INTEGER DEFAULT 300,
    last_check TEXT,
    last_content TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT
)''')

conn3.commit()
print("✓ subscribe.db 创建成功")

# ========== 4. 系统数据库 ==========
print("\n[4/4] 初始化 system.db...")
conn4 = sqlite3.connect('data/system.db')
c4 = conn4.cursor()

# 管理员账户表
c4.execute('''CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    display_name TEXT,
    role TEXT DEFAULT 'admin',
    status TEXT DEFAULT 'active',
    last_login TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)''')

# 数据源表
c4.execute('''CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    url TEXT NOT NULL,
    config TEXT DEFAULT '{}',
    status TEXT DEFAULT 'active',
    priority INTEGER DEFAULT 10,
    last_crawl_time TEXT,
    last_crawl_status TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)''')

# 统一采集日志表
c4.execute('''CREATE TABLE IF NOT EXISTS unified_crawl_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    status TEXT DEFAULT 'running',
    total_count INTEGER DEFAULT 0,
    new_count INTEGER DEFAULT 0,
    updated_count INTEGER DEFAULT 0,
    detail TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)''')

# 创建默认超级管理员 (admin / admin123)
import hashlib
salt = 'news-system-default-salt'
password_hash = hashlib.sha256(('admin123' + salt).encode()).hexdigest()
c4.execute('''INSERT OR IGNORE INTO admin_users (username, password_hash, salt, display_name, role, created_at)
    VALUES (?, ?, ?, ?, ?, ?)''',
    ('admin', password_hash, salt, '系统管理员', 'super_admin', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

conn4.commit()
print("✓ system.db 创建成功（含默认管理员 admin/admin123）")

# ========== 完成 ==========
print("\n" + "=" * 50)
print("数据库初始化完成！")
print("=" * 50)
print("\n数据库文件位置:")
print("  - data/news.db")
print("  - data/skills.db")
print("  - data/subscribe.db")
print("  - data/system.db")
print("\n默认管理员账户: admin / admin123")

conn.close()
conn2.close()
conn3.close()
conn4.close()
