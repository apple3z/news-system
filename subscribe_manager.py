#!/usr/bin/env python3
"""
订阅管理模块 - 简化版
"""

import sqlite3
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser

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


def parse_rss_feed(url):
    """使用 feedparser 解析 RSS feed，返回结构化数据列表
    v2.6.2: 修复 summary 截断、content 缺失、author/thumbnail 提取
    v2.6.4: 增加 requests 预取，解决部分 RSS 源需要 User-Agent 的问题
    """
    try:
        # 先尝试用 requests 获取（带 User-Agent）
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception as e:
            # fallback: 直接解析
            feed = feedparser.parse(url)
        
        items = []
        for entry in feed.entries:
            title = entry.get('title', '').strip()

            link = entry.get('link', '')
            if link:
                # 保留查询参数中有意义的部分，只移除 f=rss/f=feed 追踪参数
                import re
                link = re.sub(r'[?&]f=(rss|feed)$', '', link)

            # 获取摘要（不截断，多种 fallback）
            summary = ''
            if hasattr(entry, 'summary') and entry.summary:
                summary = entry.summary
            elif hasattr(entry, 'description') and entry.description:
                summary = entry.description
            elif hasattr(entry, 'content') and entry.content:
                # 如果 summary 为空，尝试从 content 提取前 500 字符作为 summary
                content_val = entry.content[0].get('value', '')
                if content_val:
                    summary = content_val[:500]

            # 获取完整内容（content 优先于 summary）
            content = summary
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].get('value', summary)
            
            # 最后的 fallback：如果 summary 和 content 都为空，尝试从 title 生成
            if not summary and not content:
                # 尝试从 content_encoded 获取
                if hasattr(entry, 'content_encoded') and entry.content_encoded:
                    content = entry.content_encoded
                    summary = content[:500]
                # 尝试从 description 获取（某些 RSS 用这个字段）
                elif hasattr(entry, 'description') and entry.description:
                    summary = entry.description
                    content = summary

            pub_date = entry.get('published', '') or entry.get('updated', '')

            # 提取作者（REQ-016）
            author = entry.get('author', '') or entry.get('dc_creator', '')

            # 提取缩略图（REQ-016）
            thumbnail = None
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                thumbnail = entry.media_thumbnail[0].get('url')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                for enc in entry.enclosures:
                    if enc.get('type', '').startswith('image/'):
                        thumbnail = enc.get('href')
                        break
            # 回退：从 content/summary 中提取第一张 img
            if not thumbnail and (content or summary):
                img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content or summary)
                if img_match:
                    thumbnail = img_match.group(1)
            
            # 提取评论数（v2.6.5 新增）
            comments = 0
            if hasattr(entry, 'comments') and entry.comments:
                # Hacker News 等返回评论链接
                comments_url = entry.comments
                # 尝试从 URL 中提取评论 ID 作为评论数的近似
                if 'item?id=' in comments_url:
                    # Hacker News 格式，暂时无法直接获取评论数，标记为有评论
                    comments = 1  # 表示有评论区
                elif 'comments' in comments_url or 'discussion' in comments_url:
                    comments = 1  # 表示有评论区
            elif hasattr(entry, 'comment_count') and entry.comment_count:
                # 直接有评论数字段
                try:
                    comments = int(entry.comment_count)
                except:
                    comments = 0
            elif hasattr(entry, 'num_comments') and entry.num_comments:
                try:
                    comments = int(entry.num_comments)
                except:
                    comments = 0
            elif hasattr(entry, 'replies') and entry.replies:
                try:
                    comments = len(entry.replies) if isinstance(entry.replies, list) else int(entry.replies)
                except:
                    comments = 0

            items.append({
                'title': title,
                'link': link,
                'summary': summary,
                'content': content,
                'pub_date': pub_date,
                'author': author,
                'thumbnail': thumbnail,
                'comments': comments  # v2.6.5 新增
            })
        return items
    except Exception as e:
        print(f"RSS parsing failed: {url} - {e}")
        return None


def fetch_url_content(url):
    """获取 URL 内容 - 用于非RSS类型的网站订阅（v2.6.0）"""
    try:
        resp = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=15)
        resp.encoding = resp.apparent_encoding

        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        content = soup.get_text(separator='\n', strip=True)
        if len(content) > 50000:
            content = content[:50000] + "..."

        return content
    except Exception as e:
        print(f"获取失败：{url} - {e}")
        return None


def check_for_updates(sub_id):
    """检查单个订阅的更新（v2.6.2: RSS用feedparser，其他用原逻辑）"""
    conn = init_db()
    c = conn.cursor()

    c.execute("SELECT * FROM subscription WHERE id = ?", (sub_id,))
    sub = c.fetchone()

    if not sub:
        conn.close()
        return False

    sub_id, name, url, sub_type, check_interval, last_check, last_content, is_active, created_at = sub

    print(f"检查订阅：{name} ({url}) [类型: {sub_type}]")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # RSS 类型：用 feedparser 解析结构化数据
    if sub_type == 'rss':
        items = parse_rss_feed(url)
        if items is None or len(items) == 0:
            print(f"  [WARN] RSS解析无结果")
            conn.close()
            return False

        # 用第一条的标题作为内容指纹
        fingerprint = '|'.join(item['title'] for item in items[:5])
        if fingerprint == (last_content or ''):
            print(f"  [SKIP] 无更新")
            c.execute("UPDATE subscription SET last_check = ? WHERE id = ?", (now, sub_id))
            conn.commit()
            conn.close()
            return False

        print(f"  [OK] 发现 {len(items)} 条更新！")
        c.execute("UPDATE subscription SET last_check = ?, last_content = ? WHERE id = ?",
                  (now, fingerprint, sub_id))
        conn.commit()
        save_update_history(sub_id, name, items)
        conn.close()
        return True

    # 非RSS类型：保持原有的纯文本对比逻辑
    current_content = fetch_url_content(url)
    if current_content is None:
        conn.close()
        return False

    current_hash = hash(current_content)
    last_hash = hash(last_content) if last_content else None

    if current_hash != last_hash:
        print(f"  [OK] 发现更新！")
        c.execute("UPDATE subscription SET last_check = ?, last_content = ? WHERE id = ?",
                  (now, current_content[:10000], sub_id))
        conn.commit()
        # 非RSS：包装成单条item格式以统一save_update_history
        items = [{
            'title': name,
            'link': url,
            'summary': current_content[:500],
            'pub_date': now
        }]
        save_update_history(sub_id, name, items)
        conn.close()
        return True
    else:
        print(f"  [SKIP] no update")
        c.execute("UPDATE subscription SET last_check = ? WHERE id = ?", (now, sub_id))
        conn.commit()
        conn.close()
        return False


def save_update_history(sub_id, name, items):
    """保存更新历史
    v2.6.2 修复: content 存完整内容而非 summary；新增 author/thumbnail 字段
    """
    conn = init_db()
    c = conn.cursor()

    # 创建更新历史表（如果不存在），含 author/thumbnail/comments 字段
    c.execute('''CREATE TABLE IF NOT EXISTS subscription_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_id INTEGER,
        sub_name TEXT,
        title TEXT,
        summary TEXT,
        content TEXT,
        link TEXT,
        pub_date TEXT,
        detected_at TEXT,
        author TEXT,
        thumbnail TEXT,
        comments INTEGER DEFAULT 0
    )''')

    # 兼容旧表：安全添加新字段
    for col in ['author', 'thumbnail', 'comments']:
        try:
            c.execute(f"ALTER TABLE subscription_history ADD COLUMN {col} {'TEXT' if col in ['author', 'thumbnail'] else 'INTEGER DEFAULT 0'}")
        except Exception:
            pass

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in items:
        c.execute('''INSERT INTO subscription_history
                     (sub_id, sub_name, title, summary, content, link, pub_date, detected_at, author, thumbnail, comments)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (sub_id, name,
                   item.get('title', ''),
                   item.get('summary', ''),
                   item.get('content', item.get('summary', '')),
                   item.get('link', ''),
                   item.get('pub_date', ''),
                   now,
                   item.get('author', ''),
                   item.get('thumbnail', ''),
                   item.get('comments', 0)))

    conn.commit()
    conn.close()
    print(f"  [SAVE] {len(items)} records saved")


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
