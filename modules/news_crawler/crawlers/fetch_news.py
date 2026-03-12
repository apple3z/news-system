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

# 使用统一的跨平台路径工具
from path_utils import NEWS_DB, SYSTEM_DB, ensure_data_dir

# 确保数据目录存在
ensure_data_dir()

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

# 爬虫日志表 - 记录每次采集的信息
CRAWL_LOG_SCHEMA = """
CREATE TABLE IF NOT EXISTS crawl_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,       -- 采集开始时间
    end_time TEXT,                  -- 采集结束时间
    total_news_count INTEGER DEFAULT 0,  -- 本次采集的新闻总数
    new_news_count INTEGER DEFAULT 0,    -- 本次新增的新闻数
    updated_news_count INTEGER DEFAULT 0, -- 本次更新的新闻数
    sources TEXT,                   -- 采集的新闻源（JSON数组）
    status TEXT DEFAULT 'running',  -- 状态：running, completed, failed
    error_message TEXT,             -- 错误信息（如果失败）
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);
"""

# 关注新闻表 - 用户关注的新闻内容
FOLLOWED_NEWS_SCHEMA = """
CREATE TABLE IF NOT EXISTS followed_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,           -- 关注的新闻标题/关键词
    keywords TEXT,                  -- 相关关键词（JSON数组）
    description TEXT,               -- 描述
    is_active INTEGER DEFAULT 1,    -- 是否启用：1=启用，0=禁用
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT DEFAULT (datetime('now', 'localtime'))
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
    conn = sqlite3.connect(NEWS_DB)
    conn.execute(NEWS_SCHEMA)
    conn.execute(CRAWL_LOG_SCHEMA)
    conn.execute(FOLLOWED_NEWS_SCHEMA)
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=12)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return resp.text
    except Exception as e:
        print(f"[WARN] 获取页面失败 {url}: {e}")
        return ""


def fetch_from_rss(rss_url, source_name, priority=10):
    """通用RSS采集函数，解析RSS/Atom XML"""
    import xml.etree.ElementTree as ET
    news = []
    raw = get_page(rss_url)
    if not raw:
        return news
    try:
        root = ET.fromstring(raw)
        # 处理命名空间
        ns = {}
        if root.tag.startswith('{'):
            ns_uri = root.tag.split('}')[0] + '}'
            ns['atom'] = ns_uri.strip('{}')

        items = []
        # RSS 2.0: channel/item
        for item in root.findall('.//item'):
            items.append(item)
        # Atom: entry
        if not items:
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                items.append(entry)
            if not items:
                for entry in root.findall('.//entry'):
                    items.append(entry)

        for item in items[:30]:
            title = ''
            link = ''
            pub_time = ''
            summary = ''

            # RSS 2.0 格式
            t = item.find('title')
            if t is not None and t.text:
                title = t.text.strip()
            l = item.find('link')
            if l is not None:
                link = (l.text or l.get('href', '')).strip()
            d = item.find('pubDate')
            if d is not None and d.text:
                pub_time = d.text.strip()
            desc = item.find('description')
            if desc is not None and desc.text:
                summary = clean_text(desc.text)[:200]

            # Atom 格式
            if not title:
                for tag in ['{http://www.w3.org/2005/Atom}title', 'title']:
                    t = item.find(tag)
                    if t is not None and t.text:
                        title = t.text.strip()
                        break
            if not link:
                for tag in ['{http://www.w3.org/2005/Atom}link', 'link']:
                    l = item.find(tag)
                    if l is not None:
                        link = (l.get('href') or l.text or '').strip()
                        break
            if not pub_time:
                for tag in ['{http://www.w3.org/2005/Atom}published', '{http://www.w3.org/2005/Atom}updated', 'published', 'updated']:
                    d = item.find(tag)
                    if d is not None and d.text:
                        pub_time = d.text.strip()
                        break
            if not summary:
                for tag in ['{http://www.w3.org/2005/Atom}summary', '{http://www.w3.org/2005/Atom}content', 'summary', 'content']:
                    s = item.find(tag)
                    if s is not None and s.text:
                        summary = clean_text(s.text)[:200]
                        break

            if title and link and len(title) > 5:
                # 解析时间
                parsed_time = parse_rss_time(pub_time) if pub_time else datetime.now().strftime("%Y-%m-%d")
                news.append({
                    "title": title,
                    "link": link,
                    "source": source_name,
                    "priority": priority,
                    "time": parsed_time,
                    "summary": summary
                })

        print(f"{source_name} (RSS): {len(news)}条")
    except ET.ParseError as e:
        print(f"[WARN] RSS解析失败 {source_name}: {e}")
    except Exception as e:
        print(f"[WARN] RSS采集异常 {source_name}: {e}")
    return news


def parse_rss_time(time_str):
    """解析RSS时间格式"""
    if not time_str:
        return datetime.now().strftime("%Y-%m-%d")

    # ISO 8601: 2026-03-12T10:30:00Z 或 2026-03-12T10:30:00+08:00
    date_patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, time_str)
        if match:
            year, month, day = match.groups()
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"

    # RFC 822: Wed, 12 Mar 2026 10:30:00 +0800
    months = {'jan':'01','feb':'02','mar':'03','apr':'04','may':'05','jun':'06',
              'jul':'07','aug':'08','sep':'09','oct':'10','nov':'11','dec':'12'}
    rfc_match = re.search(r'(\d{1,2})\s+(\w{3})\s+(\d{4})', time_str)
    if rfc_match:
        day, mon, year = rfc_match.groups()
        mon_num = months.get(mon.lower(), '01')
        return f"{int(year):04d}-{mon_num}-{int(day):02d}"

    return datetime.now().strftime("%Y-%m-%d")


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
    
    print(f"凤凰网：{len(news)}条")
    return news


def fetch_36kr():
    """采集36氪（RSS方式）"""
    return fetch_from_rss("https://36kr.com/feed", "36氪", 12)


def fetch_huxiu():
    """采集虎嗅网（RSS方式）"""
    return fetch_from_rss("https://www.huxiu.com/rss/0.xml", "虎嗅网", 10)


def fetch_jqr():
    """采集机器之心（RSS方式）"""
    return fetch_from_rss("https://www.jiqizhixin.com/rss", "机器之心", 15)


def fetch_xz2():
    """采集新智元 — 尝试RSS，失败则HTML"""
    result = fetch_from_rss("https://www.ai-era.com/feed", "新智元", 15)
    if result:
        return result
    # fallback: HTML
    news = []
    page_html = get_page("https://www.ai-era.com/")
    if page_html:
        soup = BeautifulSoup(page_html, 'html.parser')
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            link = a.get('href', '')
            if title and 8 < len(title) < 60:
                if link.startswith('/'):
                    link = "https://www.ai-era.com" + link
                news.append({"title": title, "link": link, "source": "新智元", "priority": 15})
    print(f"新智元 (HTML): {len(news)}条")
    return news


def fetch_qbit():
    """采集量子位 — 尝试RSS，失败则HTML"""
    result = fetch_from_rss("https://www.qbitai.com/feed", "量子位", 15)
    if result:
        return result
    # fallback: HTML
    news = []
    page_html = get_page("https://www.qbitai.com/")
    if page_html:
        soup = BeautifulSoup(page_html, 'html.parser')
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            link = a.get('href', '')
            if title and 8 < len(title) < 60:
                if link.startswith('/'):
                    link = "https://www.qbitai.com" + link
                news.append({"title": title, "link": link, "source": "量子位", "priority": 15})
    print(f"量子位 (HTML): {len(news)}条")
    return news


def fetch_infoq():
    """采集InfoQ（RSS方式）"""
    return fetch_from_rss("https://feed.infoq.com/cn", "InfoQ", 10)


def fetch_csdn():
    """采集CSDN — 尝试RSS，失败则HTML"""
    result = fetch_from_rss("https://blog.csdn.net/rss/hot", "CSDN", 8)
    if result:
        return result
    # fallback: HTML
    news = []
    page_html = get_page("https://www.csdn.net/")
    if page_html:
        soup = BeautifulSoup(page_html, 'html.parser')
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            link = a.get('href', '')
            if title and 8 < len(title) < 60 and any(kw in title.upper() for kw in ['AI', '智能', '大模型', 'GPT', 'PYTHON', '开发', '技术']):
                if link.startswith('/'):
                    link = "https://www.csdn.net" + link
                news.append({"title": title, "link": link, "source": "CSDN", "priority": 8})
    print(f"CSDN (HTML): {len(news)}条")
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
        'time': '',
    }
    
    # 尝试解析发布时间
    time_str = parse_time(soup, url)
    if time_str:
        result['time'] = time_str
    
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


def parse_time(soup, url):
    """从新闻页面解析发布时间"""
    time_str = ''
    
    # 1. 从 meta 标签获取
    for meta in soup.find_all('meta'):
        prop = meta.get('property', '').lower()
        name = meta.get('name', '').lower()
        if 'time' in prop or 'time' in name or 'date' in prop or 'date' in name:
            content = meta.get('content', '')
            if content and len(content) > 5:
                time_str = content
                break
    
    # 2. 从常见的时间标签获取
    time_selectors = [
        'time', '.time', '.date', '.pub-time', '.publish-time', 
        '.article-time', '.post-time', '.meta-time', '.date-time'
    ]
    for sel in time_selectors:
        elem = soup.select_one(sel)
        if elem:
            text = elem.get_text(strip=True)
            if text and len(text) > 5:
                time_str = text
                break
    
    # 3. 根据不同网站的特定选择器
    if '163.com' in url:
        elem = soup.select_one('.post_time_source, .time, .pub_time')
        if elem:
            time_str = elem.get_text(strip=True)
    elif 'sina.com.cn' in url:
        elem = soup.select_one('.date, .time, .pub_date')
        if elem:
            time_str = elem.get_text(strip=True)
    elif 'ifeng.com' in url:
        elem = soup.select_one('.time, .pubTime')
        if elem:
            time_str = elem.get_text(strip=True)
    elif '36kr.com' in url:
        elem = soup.select_one('.time, .article-time')
        if elem:
            time_str = elem.get_text(strip=True)
    elif 'huxiu.com' in url:
        elem = soup.select_one('.time, .article-time')
        if elem:
            time_str = elem.get_text(strip=True)
    elif 'jiqizhixin.com' in url:
        elem = soup.select_one('.time, .date')
        if elem:
            time_str = elem.get_text(strip=True)
    elif 'qbitai.com' in url:
        elem = soup.select_one('.time, .date')
        if elem:
            time_str = elem.get_text(strip=True)
    
    # 4. 正则解析时间字符串
    if time_str:
        # 常见格式：2024-07-25 08:38:02 或 2024年07月25日 08:38
        date_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日]?',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, time_str)
            if match:
                year, month, day = match.groups()
                return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    
    # 如果无法解析，返回当前日期
    return datetime.now().strftime("%Y-%m-%d")


def classify_news(title, content='', keywords=[]):
    """智能新闻分类（v2.6.0）"""
    text = (title + ' ' + content + ' ' + ' '.join(keywords)).upper()
    
    # AI 大模型
    if any(kw in text for kw in ['GPT', 'CLAUDE', 'GEMINI', '大模型', 'LLM', 'LLAMA', 'MISTRAL', 'QWEN', '文心', '通义', '混元', 'KIMI']):
        return 'AI 大模型'
    
    # 芯片硬件
    if any(kw in text for kw in ['芯片', 'GPU', 'CPU', 'NPU', '英伟达', 'AMD', 'INTEL', '华为', '海思', '台积电', '半导体', '硬件']):
        return '芯片硬件'
    
    # 自动驾驶
    if any(kw in text for kw in ['自动驾驶', '无人驾驶', '特斯拉', 'FSD', '智能驾驶', '蔚来', '小鹏', '理想', '汽车', 'ROBOTAXI']):
        return '自动驾驶'
    
    # 机器人
    if any(kw in text for kw in ['机器人', '人形机器人', '波士顿动力', '优必选', '机械臂', 'TELEOPERATION', '具身智能']):
        return '机器人'
    
    # AI 应用
    if any(kw in text for kw in ['应用', '工具', '产品', 'SaaS', '软件', '平台', '服务']):
        return 'AI 应用'
    
    # 科技前沿（默认）
    return '科技前沿'


def fetch_dynamic_rss_sources():
    """从 data_sources 表动态读取RSS新闻源并采集"""
    all_news = []
    # 已有硬编码函数的源名称，避免重复采集
    hardcoded_names = {'网易科技', '新浪科技', '凤凰科技', '36氪', '虎嗅网',
                       '机器之心', '新智元', '量子位', 'InfoQ', 'CSDN'}
    try:
        sys_conn = sqlite3.connect(SYSTEM_DB)
        sys_conn.row_factory = sqlite3.Row
        rows = sys_conn.execute(
            "SELECT name, url, priority, config FROM data_sources "
            "WHERE type IN ('news', 'rss') AND status = 'active'"
        ).fetchall()
        sys_conn.close()

        for row in rows:
            name = row['name']
            if name in hardcoded_names:
                continue
            config = json.loads(row['config']) if row['config'] else {}
            # 只采集标记为RSS的源，或URL明显是feed的源
            is_rss = config.get('rss', False)
            url = row['url']
            if not is_rss and not any(k in url for k in ['/feed', '/rss', '.xml', '.rss']):
                continue
            result = fetch_from_rss(url, name, row['priority'] or 10)
            all_news.extend(result)
    except Exception as e:
        print(f"[WARN] 动态RSS源采集异常: {e}")
    return all_news


def fetch_news():
    """采集并分析新闻"""
    conn = init_db()
    c = conn.cursor()
    
    # 记录采集开始
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sources = ['163', 'sina', 'ifeng', '36kr', 'huxiu', 'jqr', 'xz2', 'qbit', 'infoq', 'csdn']
    c.execute('''INSERT INTO crawl_log 
                 (start_time, sources, status) 
                 VALUES (?, ?, ?)''',
              (start_time, json.dumps(sources, ensure_ascii=False), 'running'))
    crawl_log_id = c.lastrowid
    conn.commit()
    
    all_news = []
    new_count = 0
    updated_count = 0
    
    try:
        # 采集 - 原有 3 个源
        all_news.extend(fetch_163())
        all_news.extend(fetch_sina())
        all_news.extend(fetch_ifeng())
        
        # 采集 - 新增 7 个源（v2.6.0）
        all_news.extend(fetch_36kr())
        all_news.extend(fetch_huxiu())
        all_news.extend(fetch_jqr())
        all_news.extend(fetch_xz2())
        all_news.extend(fetch_qbit())
        all_news.extend(fetch_infoq())
        all_news.extend(fetch_csdn())

        # 采集 - 动态RSS源（v2.6.2，从data_sources表读取）
        print("\n--- 动态RSS源采集 ---")
        all_news.extend(fetch_dynamic_rss_sources())

        # 去重
        seen = set()
        unique = []
        for n in all_news:
            key = n["title"][:30]
            if key not in seen:
                seen.add(key)
                unique.append(n)

        # 均衡选取：每个来源保底10条，剩余按优先级补满
        MAX_TOTAL = 200
        PER_SOURCE = 10
        by_source = {}
        for n in unique:
            by_source.setdefault(n.get('source', ''), []).append(n)

        selected = []
        remainder = []
        for src, items in by_source.items():
            # 每个来源内按优先级排序
            items.sort(key=lambda x: x.get('priority', 0), reverse=True)
            selected.extend(items[:PER_SOURCE])
            remainder.extend(items[PER_SOURCE:])

        # 剩余按优先级排序，补满到MAX_TOTAL
        remainder.sort(key=lambda x: x.get('priority', 0), reverse=True)
        remaining_slots = MAX_TOTAL - len(selected)
        if remaining_slots > 0:
            selected.extend(remainder[:remaining_slots])

        news_detail_list = []  # 记录每条新闻的详细信息（Problem 5）

        for n in selected:
            # 检查存在
            c.execute("SELECT id, summary FROM news WHERE link = ?", (n["link"],))
            row = c.fetchone()

            if row and row[1]:  # 已有完整数据
                continue

            print(f"-> {n['title'][:40]}")

            # RSS源已有time和summary，优先使用
            rss_time = n.get('time', '')
            rss_summary = n.get('summary', '')

            # 获取详情
            detail = get_detail(n["link"])

            # 分析
            content = detail.get('content', '') or n['title']
            keywords = extract_keywords(content)
            entities = extract_entities(content)
            hot_score = calc_hot_score(n['title'], keywords)

            # 优先使用RSS的summary，其次detail的，最后自动生成
            summary = rss_summary or detail.get('summary') or generate_summary(content, n['title'])
            # 优先使用RSS的时间，其次detail的
            news_time = rss_time or detail.get('time', datetime.now().strftime("%Y-%m-%d"))

            # 自动分类（v2.6.0）
            category = classify_news(n['title'], content, keywords)

            # 记录详细信息
            news_detail_list.append({
                'title': n['title'],
                'link': n['link'],
                'source': n.get('source', ''),
                'time': news_time,
                'summary': summary[:100] if summary else ''
            })

            if row:  # 更新
                c.execute('''UPDATE news SET
                    summary=?, image=?, content=?, keywords=?, entities=?,
                    hot_score=?, trend_level=?, category=?, time=?, updated_at=? WHERE link=?''',
                    (summary, detail.get('image'), detail.get('content'),
                     json.dumps(keywords, ensure_ascii=False),
                     json.dumps(entities, ensure_ascii=False),
                     hot_score, determine_trend_level(hot_score),
                     category, news_time,
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"), n['link']))
                updated_count += 1
            else:  # 新增
                c.execute('''INSERT INTO news
                    (title, link, source, category, time, summary, image, content,
                     keywords, entities, hot_score, trend_level, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (n['title'], n['link'], n['source'], category,
                     news_time,
                     summary, detail.get('image'), detail.get('content'),
                     json.dumps(keywords, ensure_ascii=False),
                     json.dumps(entities, ensure_ascii=False),
                     hot_score, determine_trend_level(hot_score),
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                new_count += 1

        conn.commit()

        # 记录采集完成
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        detail_json = json.dumps(news_detail_list, ensure_ascii=False)
        c.execute('''UPDATE crawl_log SET
                     end_time=?, total_news_count=?, new_news_count=?,
                     updated_news_count=?, status=?, error_message=?
                     WHERE id=?''',
                  (end_time, len(selected), new_count, updated_count, 'completed', detail_json, crawl_log_id))
        conn.commit()

        result = {
            'total': len(unique),
            'new': new_count,
            'updated': updated_count,
            'detail': news_detail_list
        }
        print(f"\n处理完成: {new_count}条新增, {updated_count}条更新, 共{len(selected)}条")
        return result

    except Exception as e:
        # 记录失败
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''UPDATE crawl_log SET
                     end_time=?, status=?, error_message=?
                     WHERE id=?''',
                  (end_time, 'failed', str(e), crawl_log_id))
        conn.commit()
        print(f"\n采集失败: {e}")
        return {'total': 0, 'new': 0, 'updated': 0, 'detail': [], 'error': str(e)}
    finally:
        conn.close()


if __name__ == "__main__":
    print("="*50)
    print("新闻采集与分析系统")
    print("="*50)
    fetch_news()
