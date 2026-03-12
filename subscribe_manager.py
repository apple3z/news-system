#!/usr/bin/env python3
"""
订阅管理模块 - 简化版
"""

import sqlite3
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup

# 使用统一的跨平台路径工具
from path_utils import SUBSCRIBE_DB, ensure_data_dir

# 确保数据目录存在
ensure_data_dir()

SUB_TYPES = {
    'website': '网站',
    'rss': 'RSS订阅',
    'video': '视频',
    'forum': '论坛'
}

def init_db():
    conn = sqlite3.connect(SUBSCRIBE_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscription (
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
    conn.commit()
    return conn

def add_subscription(name, url, sub_type='website', interval=300):
    conn = init_db()
    c = conn.cursor()
    c.execute('''INSERT INTO subscription (name, url, sub_type, check_interval, created_at)
                 VALUES (?, ?, ?, ?, ?)''',
              (name, url, sub_type, interval, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    sub_id = c.lastrowid
    conn.commit()
    conn.close()
    return sub_id

def remove_subscription(sub_id):
    conn = init_db()
    c = conn.cursor()
    c.execute("DELETE FROM subscription WHERE id = ?", (sub_id,))
    conn.commit()
    conn.close()

def get_subscriptions():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT * FROM subscription WHERE is_active = 1 ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_subs():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT * FROM subscription ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def fetch_url_content(url):
    """获取 URL 内容（v2.6.0）"""
    try:
        resp = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=15)
        resp.encoding = resp.apparent_encoding
        
        # 尝试提取正文内容
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 移除不需要的标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # 获取文本内容
        content = soup.get_text(separator='\n', strip=True)
        
        # 限制长度
        if len(content) > 50000:
            content = content[:50000] + "..."
        
        return content
    except Exception as e:
        print(f"获取失败：{url} - {e}")
        return None


def check_for_updates(sub_id):
    """检查单个订阅的更新（v2.6.0）"""
    conn = init_db()
    c = conn.cursor()
    
    # 获取订阅信息
    c.execute("SELECT * FROM subscription WHERE id = ?", (sub_id,))
    sub = c.fetchone()
    
    if not sub:
        conn.close()
        return False
    
    sub_id, name, url, sub_type, check_interval, last_check, last_content, is_active, created_at = sub
    
    print(f"检查订阅：{name} ({url})")
    
    # 获取当前内容
    current_content = fetch_url_content(url)
    
    if current_content is None:
        conn.close()
        return False
    
    # 计算内容指纹（简单哈希）
    current_hash = hash(current_content)
    last_hash = hash(last_content) if last_content else None
    
    # 检测更新
    if current_hash != last_hash:
        print(f"  ✅ 发现更新！")
        
        # 更新数据库
        c.execute('''UPDATE subscription 
                     SET last_check = ?, last_content = ?
                     WHERE id = ?''',
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   current_content[:10000],  # 保存部分用于对比
                   sub_id))
        conn.commit()
        
        # 保存完整更新历史（可选）
        save_update_history(sub_id, name, current_content)
        
        conn.close()
        return True
    else:
        print(f"  ⏹️  无更新")
        c.execute('''UPDATE subscription 
                     SET last_check = ?
                     WHERE id = ?''',
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sub_id))
        conn.commit()
        conn.close()
        return False


def save_update_history(sub_id, name, content):
    """保存更新历史（v2.6.0）"""
    conn = init_db()
    c = conn.cursor()
    
    # 创建更新历史表（如果不存在）
    c.execute('''CREATE TABLE IF NOT EXISTS subscription_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_id INTEGER,
        sub_name TEXT,
        content TEXT,
        detected_at TEXT
    )''')
    
    # 保存更新
    c.execute('''INSERT INTO subscription_history (sub_id, sub_name, content, detected_at)
                 VALUES (?, ?, ?, ?)''',
              (sub_id, name, content[:50000], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()


def check_all_subscriptions():
    """检查所有订阅的更新（v2.6.0）"""
    subs = get_subscriptions()
    
    print("=" * 50)
    print("开始检查所有订阅...")
    print("=" * 50)
    
    updated_count = 0
    for sub in subs:
        if check_for_updates(sub[0]):
            updated_count += 1
    
    print("=" * 50)
    print(f"检查完成！共检查 {len(subs)} 个订阅，{updated_count} 个有更新")
    print("=" * 50)
    
    return updated_count

# 测试
if __name__ == "__main__":
    print("订阅列表:")
    for sub in get_all_subs():
        print(f"  [{sub[0]}] {sub[1]} - {sub[2]} ({sub[3]})")
