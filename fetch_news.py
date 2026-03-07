#!/usr/bin/env python3
"""
新闻采集与分析系统 - 完整版
包含完整的数据结构和分析功能
"""

import json
import os
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import html

DB_FILE = "/home/zhang/.copaw/news_system/data/news.db"

# ==================== 数据结构定义 ====================

NEWS_SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 基础信息
    title TEXT NOT NULL,           -- 标题
    link TEXT UNIQUE,              -- 原文链接
    source TEXT,                   -- 来源媒体
    author TEXT,                   -- 作者
    category TEXT,                 -- 分类（科技/AI/财经等）
    time TEXT,                     -- 发布时间
    
    -- 内容
    summary TEXT,                  -- 摘要（100字中文）
    image TEXT,                    -- 封面图URL
    content TEXT,                  -- 正文内容（清洗后）
    original_content TEXT,         -- 原始内容
    
    -- 分析结果
    keywords TEXT,                 -- 关键词（JSON数组）
    entities TEXT,                 -- 实体：人名/公司名/产品名
    sentiment TEXT,                -- 情感：positive/negative/neutral
    trend_level TEXT,              -- 热点级别：high/medium/low
    
    -- 热度
    hot_score INTEGER DEFAULT 0,    -- 热度分数
    view_count INTEGER DEFAULT 0,  -- 浏览量（若有）
    
    -- 元数据
    created_at TEXT,
    updated_at TEXT
);
"""

# AI/科技关键词库
AI_KEYWORDS = {
    'AI': 20, '人工智能': 20, '大模型': 18, 'LLM': 18, 'ChatGPT': 15,
    'GPT': 15, 'AIGC': 15, 'Sora': 15, 'OpenAI': 15,
    'Claude': 12, 'Gemini': 12, '文心': 12, '通义': 12, '智谱': 12,
    'Kimi': 12, '豆包': 10, 'DeepSeek': 15, 'MiniMax': 12,
    '英伟达': 15, 'NVIDIA': 15, 'AMD': 10, 'Intel': 10,
    '苹果': 8, '谷歌': 8, '微软': 8, 'Meta': 10,
    '马斯克': 12, '特斯拉': 10, 'xAI': 12,
    '自动驾驶': 12, '智能驾驶': 12, 'Robotaxi': 10,
    '芯片': 10, 'GPU': 12, '算力': 10,
    '算法': 8, '机器学习': 10, '深度学习': 10,
    '字节跳动': 10, '百度': 8, '阿里': 8, '腾讯': 8,
    '商汤': 8, '旷视': 8, '讯飞': 8,
    '机器人': 10, '人形机器人': 12, '具身智能': 12,
}

# 热点词
HOT_WORDS = {
    '重磅': 15, '突破': 12, '首发': 10, '首款': 10,
    '第一': 8, '最强': 10, '颠覆': 12, '革命': 10,
    '爆炸': 15, '爆发': 10, '飙升': 12, '万亿': 10,
    '融资': 10, 'IPO': 10, '收购': 8, '并购': 8,
}

# 公司/人物实体
ENTITY_PATTERNS = {
    '公司': ['英伟达', 'AMD', 'Intel', '苹果', '谷歌', '微软', 'Meta', 'OpenAI', 
             ' Anthropic', '字节跳动', '百度', '阿里', '腾讯', '特斯拉', '小鹏', '蔚来', '理想'],
    '人物': ['马斯克', '黄仁勋', '苏姿丰', '库克', '纳德拉', '扎克伯格', 'Sam Altman'],
    '产品': ['GPT-4', 'GPT-5', 'Sora', 'Gemini', 'Claude', '文心一言', '通义千问', 'Kimi'],
}


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(NEWS_SCHEMA)
    conn.commit()
    return conn


def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    # 解码HTML实体
    text = html.unescape(text)
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def calc_hot_score(title, keywords):
    """计算热度分数"""
    score = 0
    title_upper = title.upper()
    
    # AI关键词加分
    for kw, points in AI_KEYWORDS.items():
        if kw in title_upper:
            score += points
    
    # 热点词加分
    for word, points in HOT_WORDS.items():
        if word in title:
            score += points
    
    # 来源加分
    if '163' in title or '网易' in title:
        score += 5
    
    return score


def extract_keywords(content):
    """提取关键词"""
    keywords = []
    content_upper = content.upper()
    
    for kw, points in AI_KEYWORDS.items():
        if kw.upper() in content_upper:
            keywords.append(kw)
    
    # 去重并返回
    return list(set(keywords))[:10]


def extract_entities(content):
    """提取实体"""
    entities = {'companies': [], 'persons': [], 'products': []}
    
    # 公司
    for company in ENTITY_PATTERNS['公司']:
        if company in content:
            entities['companies'].append(company)
    
    # 人物
    for person in ENTITY_PATTERNS['人物']:
        if person in content:
            entities['persons'].append(person)
    
    # 产品
    for product in ENTITY_PATTERNS['产品']:
        if product in content:
            entities['products'].append(product)
    
    return entities


def generate_summary(content, title):
    """生成摘要"""
    if not content:
        return title[:100]
    
    # 取前300字
    text = content[:300]
    # 找到第一个句号或逗号
    for sep in ['。', '！', '？', '，', '.']:
        idx = text.find(sep)
        if idx > 50:
            text = text[:idx+1]
            break
    
    return clean_text(text)[:100]


def determine_trend_level(score):
    """判断热点级别"""
    if score >= 30:
        return 'high'
    elif score >= 15:
        return 'medium'
    else:
        return 'low'


def get_page(url):
    """获取页面"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=12)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return resp.text
    except:
        return ""


def fetch_163():
    """采集163新闻"""
    news = []
    html = get_page("https://tech.163.com/")
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            link = a.get('href', '')
            
            if title and 8 < len(title) < 60 and any(kw in title.upper() for kw in ['AI', '智能', '大模型', 'GPT', '英伟达', '特斯拉', '自动驾驶', '芯片', '科技']):
                if link.startswith('/'):
                    link = "https://tech.163.com" + link
                news.append({"title": title, "link": link, "source": "163网易", "priority": 15})
    
    print(f"163: {len(news)}条")
    return news


def fetch_sina():
    """采集新浪新闻"""
    news = []
    html = get_page("https://tech.sina.com.cn/")
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            link = a.get('href', '')
            
            if title and 8 < len(title) < 60 and any(kw in title.upper() for kw in ['AI', '智能', '大模型', 'GPT', '英伟达', '特斯拉', '自动驾驶', '芯片', '科技']):
                if link.startswith('/'):
                    link = "https://tech.sina.com.cn" + link
                news.append({"title": title, "link": link, "source": "新浪科技", "priority": 10})
    
    print(f"新浪: {len(news)}条")
    return news


def fetch_ifeng():
    """采集凤凰网新闻"""
    news = []
    html = get_page("https://tech.ifeng.com/")
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            link = a.get('href', '')
            
            if title and 8 < len(title) < 60 and any(kw in title.upper() for kw in ['AI', '智能', '大模型', 'GPT', '英伟达', '特斯拉', '自动驾驶', '芯片', '科技']):
                if link.startswith('/'):
                    link = "https://tech.ifeng.com" + link
                news.append({"title": title, "link": link, "source": "凤凰网", "priority": 8})
    
    print(f"凤凰网: {len(news)}条")
    return news


def get_detail(url):
    """获取新闻详情"""
    html = get_page(url)
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'html.parser')
    
    result = {
        'summary': '',
        'image': '',
        'content': '',
        'keywords': [],
        'entities': {'companies': [], 'persons': [], 'products': []},
    }
    
    # 摘要
    for meta in soup.find_all('meta'):
        desc = meta.get('description', '') or meta.get('og:description', '')
        if desc and len(desc) > 30:
            result['summary'] = desc[:120]
            break
    
    # 图片
    for meta in soup.find_all('meta', property='og:image'):
        img = meta.get('content', '')
        if img:
            if img.startswith('//'):
                img = 'https:' + img
            result['image'] = img
            break
    
    if not result['image']:
        for img in soup.find_all('img'):
            src = img.get('src', '') or img.get('data-src', '')
            if src and 'http' in src and 'logo' not in src.lower():
                if src.startswith('//'):
                    src = 'https:' + src
                result['image'] = src
                break
    
    # 正文
    for sel in ['#article_content', '.article_content', '.post_content', '.content', 'article']:
        article = soup.select_one(sel)
        if article:
            for s in article.find_all(['script', 'style', 'iframe']):
                s.decompose()
            texts = article.get_text(separator='\n', strip=True)
            lines = [t for t in texts.split('\n') if len(t) > 20]
            result['content'] = '\n'.join(lines[:50])
            break
    
    return result


def fetch_news():
    """采集并分析新闻"""
    all_news = []
    
    # 采集
    all_news.extend(fetch_163())
    all_news.extend(fetch_sina())
    all_news.extend(fetch_ifeng())
    
    # 去重
    seen = set()
    unique = []
    for n in all_news:
        key = n["title"][:30]
        if key not in seen:
            seen.add(key)
            unique.append(n)
    
    conn = init_db()
    c = conn.cursor()
    saved = 0
    
    for n in unique[:30]:
        # 检查存在
        c.execute("SELECT id, summary FROM news WHERE link = ?", (n["link"],))
        row = c.fetchone()
        
        if row and row[1]:  # 已有完整数据
            continue
        
        print(f"-> {n['title'][:40]}")
        
        # 获取详情
        detail = get_detail(n["link"])
        
        # 分析
        content = detail.get('content', '') or n['title']
        keywords = extract_keywords(content)
        entities = extract_entities(content)
        hot_score = calc_hot_score(n['title'], keywords)
        summary = detail.get('summary') or generate_summary(content, n['title'])
        
        if row:  # 更新
            c.execute('''UPDATE news SET 
                summary=?, image=?, content=?, keywords=?, entities=?,
                hot_score=?, trend_level=?, updated_at=? WHERE link=?''',
                (summary, detail.get('image'), detail.get('content'),
                 json.dumps(keywords, ensure_ascii=False),
                 json.dumps(entities, ensure_ascii=False),
                 hot_score, determine_trend_level(hot_score),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), n['link']))
        else:  # 新增
            c.execute('''INSERT INTO news 
                (title, link, source, category, time, summary, image, content,
                 keywords, entities, hot_score, trend_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (n['title'], n['link'], n['source'], 'AI/科技', 
                 datetime.now().strftime("%Y-%m-%d"),
                 summary, detail.get('image'), detail.get('content'),
                 json.dumps(keywords, ensure_ascii=False),
                 json.dumps(entities, ensure_ascii=False),
                 hot_score, determine_trend_level(hot_score),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        saved += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n处理完成: {saved}条")


if __name__ == "__main__":
    print("="*50)
    print("新闻采集与分析系统")
    print("="*50)
    fetch_news()
