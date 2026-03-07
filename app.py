#!/usr/bin/env python3
"""
Web服务 - 完整版 (v2.2)
包含: 新闻/Skills/订阅管理/研发Wiki
"""

import json, os, re
from flask import Flask, render_template, render_template_string, jsonify, request
import sqlite3
import subprocess

app = Flask(__name__, static_folder='static', static_url_path='/static')

# 静态文件路由
@app.route('/static/<path:filename>')
def serve_static(filename):
    from flask import send_from_directory
    return send_from_directory(app.static_folder, filename)

NEWS_DB = "/home/zhang/news_system/data/news.db"
SKILLS_DB = "/home/zhang/news_system/data/skills.db"
SUBSCRIBE_DB = "/home/zhang/news_system/data/subscribe.db"
# 旧文档目录（兼容）
DOCS_DIR = "/home/zhang/news_system/docs/"
# 新版本文档目录（新版 - 使用中文目录名）
VERSION_DOCS_DIR = "/home/zhang/news_system/doc/"
# 新目录结构
VERSION_HISTORY_DIR = "/home/zhang/news_system/版本历史/"
DOCS_CENTER_DIR = "/home/zhang/news_system/文档中心/"
# ★ 版本文档管理目录（v2.4 新增）
VERSION_MANAGE_DIR = "/home/zhang/news_system/版本管理/"
# 研发规范目录（v2.5 新增）
RESEARCH_SPEC_DIR = "/home/zhang/news_system/研发规范/"
# 版本文件记录
VERSION_FILE = os.path.join(VERSION_DOCS_DIR, ".versions.json")

# 导入统一版本管理函数
import sys
sys.path.insert(0, '/home/zhang/news_system')
from utils.version_manager import (
    get_sorted_versions, 
    scan_version_docs,
    get_doc_version,
    save_doc_with_version,
    validate_doc_path
)

# 确保目录存在
os.makedirs(VERSION_HISTORY_DIR, exist_ok=True)
os.makedirs(DOCS_CENTER_DIR, exist_ok=True)

# ========== 封面图配置 ==========
DEFAULT_COVERS = [
    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800',
    'https://images.unsplash.com/photo-1677442136019-21785ec2d986?w=800',
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800',
]

def get_cover(news_image):
    """获取封面图"""
    if news_image and 'http' in news_image:
        return news_image
    import random
    return random.choice(DEFAULT_COVERS)

# ========== 首页模板 ==========
INDEX_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI科技热点</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }
        h1 {
            font-size: 2.5em;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav { display: flex; justify-content: center; gap: 15px; margin-top: 20px; }
        .nav a {
            padding: 12px 25px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 25px;
            color: #fff;
            text-decoration: none;
            transition: all 0.3s;
        }
        .nav a:hover, .nav a.active {
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            border-color: transparent;
        }
        .stats { text-align: center; color: #888; margin-bottom: 25px; }
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }
        .news-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s;
        }
        .news-card:hover {
            transform: translateY(-5px);
            border-color: rgba(0,210,255,0.5);
        }
        .card-img {
            width: 100%;
            height: 160px;
            background: linear-gradient(135deg, #1a1a2e, #2d2d5a);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5em;
            color: rgba(255,255,255,0.2);
            overflow: hidden;
        }
        .card-img img { width: 100%; height: 100%; object-fit: cover; }
        .card-body { padding: 15px; }
        .card-tags { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 8px; }
        .card-tag {
            padding: 3px 10px;
            background: linear-gradient(90deg, #ff6b6b, #feca57);
            border-radius: 10px;
            font-size: 0.7em;
        }
        .card-title {
            font-size: 1em;
            color: #fff;
            line-height: 1.4;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .card-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.8em;
            color: #666;
        }
        .card-hot { color: #ff6b6b; font-weight: bold; }
        footer { text-align: center; padding: 40px; color: #555; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 AI科技热点</h1>
            <div class="nav">
                <a href="/">科技热点</a>
                <a href="/skills">Skills工具</a>
                <a href="/subscribe">📥 订阅管理</a>
                <a href="/sys">⚙️ 系统管理</a>
            </div>
        </header>
        
        <div class="stats">
            📰 {{ news|length }} 条新闻 | 🕐 {{ update_time }}
        </div>
        
        <div class="news-grid">
{% for item in news %}
            <div class="news-card" onclick="location.href='/news/{{ item.id }}'">
                <div class="card-img">
                    <img src="{{ item.image or get_cover(item.image) }}" alt="" onerror="this.style.display='none'">
                </div>
                <div class="card-body">
                    <div class="card-tags">
                        <span class="card-tag">{{ item.category }}</span>
                    </div>
                    <h3 class="card-title">{{ item.title }}</h3>
                    <div class="card-meta">
                        <span>{{ item.source }}</span>
                        <span class="card-hot">🔥 {{ item.hot_score }}</span>
                    </div>
                </div>
            </div>
{% endfor %}
        </div>
        
        <footer>AI科技热点</footer>
    </div>
</body>
</html>
'''

# ========== 订阅管理页面 ==========
SUBSCRIBE_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>订阅管理</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }
        h1 { font-size: 2em; margin-bottom: 20px; }
        .nav { display: flex; justify-content: center; gap: 15px; margin-top: 20px; }
        .nav a {
            padding: 12px 25px;
            background: rgba(255,255,255,0.1);
            border-radius: 25px;
            color: #fff;
            text-decoration: none;
        }
        .nav a:hover, .nav a.active {
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        }
        .add-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 25px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            border: none;
            border-radius: 25px;
            color: #fff;
            font-size: 1em;
            cursor: pointer;
            margin-bottom: 30px;
        }
        .sub-list { display: flex; flex-direction: column; gap: 15px; }
        .sub-item {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .sub-info h3 { color: #00d2ff; margin-bottom: 5px; }
        .sub-info p { color: #888; font-size: 0.9em; }
        .sub-actions { display: flex; gap: 10px; }
        .sub-btn {
            padding: 8px 15px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 15px;
            color: #aaa;
            cursor: pointer;
        }
        .sub-btn:hover { background: rgba(255,255,255,0.2); color: #fff; }
        .sub-btn.delete:hover { background: #ff6b6b; color: #fff; }
        .empty { text-align: center; color: #666; padding: 40px; }
        .form-popup {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.8);
            align-items: center;
            justify-content: center;
        }
        .form-popup.show { display: flex; }
        .form-box {
            background: linear-gradient(135deg, #1a1a2e, #2d2d5a);
            border-radius: 20px;
            padding: 30px;
            width: 400px;
        }
        .form-box h2 { margin-bottom: 20px; }
        .form-box input, .form-box select {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #fff;
        }
        .form-box button {
            padding: 12px 25px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
        .btn-cancel { background: rgba(255,255,255,0.1); color: #aaa; margin-right: 10px; }
        .btn-submit { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📥 订阅管理</h1>
            <div class="nav">
                <a href="/">科技热点</a>
                <a href="/skills">Skills工具</a>
                <a href="/subscribe" class="active">订阅管理</a>
                <a href="/dev">🔧 研发管理</a>
            </div>
        </header>
        
        <button class="add-btn" onclick="showForm()">+ 添加订阅</button>
        
        <div class="sub-list">
{% if subs %}
{% for sub in subs %}
            <div class="sub-item">
                <div class="sub-info">
                    <h3>{{ sub[1] }}</h3>
                    <p>{{ sub[2] }} | {{ sub[3] }}</p>
                </div>
                <div class="sub-actions">
                    <button class="sub-btn delete" onclick="deleteSub({{ sub[0] }})">删除</button>
                </div>
            </div>
{% endfor %}
{% else %}
            <div class="empty">暂无订阅，点击上方添加</div>
{% endif %}
        </div>
    </div>
    
    <div class="form-popup" id="popup">
        <div class="form-box">
            <h2>添加订阅</h2>
            <input type="text" id="subName" placeholder="名称（如：知乎AI）">
            <input type="text" id="subUrl" placeholder="URL地址">
            <select id="subType">
                <option value="website">网站</option>
                <option value="rss">RSS</option>
                <option value="video">视频</option>
                <option value="forum">论坛</option>
            </select>
            <button class="btn-cancel" onclick="hideForm()">取消</button>
            <button class="btn-submit" onclick="addSub()">添加</button>
        </div>
    </div>
    
    <script>
        function showForm() { document.getElementById('popup').classList.add('show'); }
        function hideForm() { document.getElementById('popup').classList.remove('show'); }
        
        function addSub() {
            const name = document.getElementById('subName').value;
            const url = document.getElementById('subUrl').value;
            const type = document.getElementById('subType').value;
            
            fetch('/api/subscribe', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, url, type})
            }).then(r => r.json()).then(d => {
                if(d.code === 200) location.reload();
            });
        }
        
        function deleteSub(id) {
            if(confirm('确认删除?')) {
                fetch('/api/subscribe/' + id, {method: 'DELETE'}).then(r => r.json()).then(d => {
                    if(d.code === 200) location.reload();
                });
            }
        }
    </script>
</body>
</html>
'''

# ========== Skills模板 ==========
SKILLS_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Skills工具</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }
        h1 { font-size: 2.5em; background: linear-gradient(90deg, #a8edea, #fed6e3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav { display: flex; justify-content: center; gap: 15px; margin-top: 20px; }
        .nav a {
            padding: 12px 25px;
            background: rgba(255,255,255,0.1);
            border-radius: 25px;
            color: #fff;
            text-decoration: none;
        }
        .nav a:first-child { background: linear-gradient(90deg, #00d2ff, #3a7bd5); }
        
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .skill-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .skill-card:hover { transform: translateY(-5px); border-color: rgba(168,237,234,0.5); }
        .skill-icon {
            width: 60px; height: 60px;
            background: linear-gradient(135deg, #a8edea, #fed6e3);
            border-radius: 15px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5em; margin-bottom: 15px;
        }
        .skill-name { font-size: 1.3em; color: #a8edea; margin-bottom: 8px; }
        .skill-level {
            display: inline-block;
            padding: 4px 12px;
            background: linear-gradient(90deg, #a8edea, #fed6e3);
            border-radius: 12px;
            font-size: 0.75em; color: #333; margin-bottom: 12px;
        }
        .skill-intro {
            font-size: 0.9em; color: #aaa; line-height: 1.5;
            margin-bottom: 15px;
            display: -webkit-box; -webkit-line-clamp: 2;
            -webkit-box-orient: vertical; overflow: hidden;
        }
        .skill-features { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 15px; }
        .skill-feature {
            padding: 3px 10px;
            background: rgba(168,237,234,0.15);
            border-radius: 10px;
            font-size: 0.75em; color: #a8edea;
        }
        .skill-links { display: flex; gap: 10px; }
        .skill-link {
            padding: 6px 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            font-size: 0.8em; color: #aaa;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛠️ Skills工具</h1>
            <div class="nav">
                <a href="/">科技热点</a>
                <a href="/skills" class="active">Skills工具</a>
                <a href="/subscribe">📥 订阅管理</a>
                <a href="/dev">🔧 研发管理</a>
            </div>
        </header>
        
        <div class="skills-grid">
{% for s in skills %}
            <div class="skill-card" onclick="location.href='/skill/{{ s.id }}'">
                <div class="skill-icon">🛠️</div>
                <h3 class="skill-name">{{ s.name }}</h3>
                <span class="skill-level">{{ s.skill_level }}</span>
                <p class="skill-intro">{{ s.chinese_intro }}</p>
                <div class="skill-features">
{% for f in (s.features or '').split('|')[:4] %}
                    <span class="skill-feature">{{ f }}</span>
{% endfor %}
                </div>
                <div class="skill-links">
                    <a href="{{ s.github_url }}" target="_blank" class="skill-link">GitHub</a>
                    <a href="{{ s.download_url }}" target="_blank" class="skill-link">⬇️ 下载</a>
                </div>
            </div>
{% endfor %}
        </div>
    </div>
</body>
</html>
'''

# ========== 详情页模板 ==========
NEWS_DETAIL_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{ news.title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh; color: #e0e0e0;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        .back-bar { display: flex; justify-content: space-between; margin-bottom: 30px; }
        .back-link {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 25px; color: #fff; text-decoration: none;
        }
        .hero-img {
            width: 100%; height: 300px;
            background: linear-gradient(135deg, #1a1a2e, #2d2d5a);
            border-radius: 20px; overflow: hidden;
            margin-bottom: 25px;
            display: flex; align-items: center; justify-content: center;
            font-size: 4em; color: rgba(255,255,255,0.1);
        }
        .hero-img img { width: 100%; height: 100%; object-fit: cover; }
        
        .section {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px; padding: 25px; margin-bottom: 20px;
        }
        .title-main { font-size: 1.8em; color: #fff; line-height: 1.4; margin-bottom: 15px; }
        .meta-row { display: flex; gap: 20px; font-size: 0.9em; color: #888; margin-bottom: 20px; }
        .hot-badge {
            padding: 5px 15px;
            background: linear-gradient(90deg, #ff6b6b, #feca57);
            border-radius: 15px; color: #fff; font-weight: bold;
        }
        .keywords { display: flex; gap: 8px; flex-wrap: wrap; }
        .keyword {
            padding: 5px 15px;
            background: rgba(0,210,255,0.15);
            border: 1px solid rgba(0,210,255,0.3);
            border-radius: 15px; font-size: 0.85em; color: #00d2ff;
        }
        .summary-text { font-size: 1.05em; line-height: 1.8; color: #ccc; }
        .content-text { font-size: 1em; line-height: 1.9; color: #bbb; white-space: pre-wrap; }
        
        .original-link {
            display: inline-flex; gap: 8px;
            padding: 15px 30px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 30px; color: #fff; text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="back-bar">
            <a href="/" class="back-link">← 返回</a>
        </div>
        
        <div class="hero-img">
            <img src="{{ news.image or get_cover(news.image) }}" alt="" onerror="this.style.display='none'">
        </div>
        
        <div class="section">
            <h1 class="title-main">{{ news.title }}</h1>
            <div class="meta-row">
                <span>📰 {{ news.source }}</span>
                <span>🕐 {{ news.time }}</span>
                <span class="hot-badge">🔥 热度 {{ news.hot_score }}</span>
            </div>
        </div>
        
        {% if news.keywords %}
        <div class="section">
            <h3 style="color:#00d2ff;margin-bottom:15px">🏷️ 关键词</h3>
            <div class="keywords">
                {% for kw in (news.keywords_list or []) %}
                <span class="keyword">{{ kw }}</span>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if news.summary %}
        <div class="section">
            <h3 style="color:#00d2ff;margin-bottom:15px">📝 新闻摘要</h3>
            <p class="summary-text">{{ news.summary }}</p>
        </div>
        {% endif %}
        
        {% if news.content %}
        <div class="section">
            <h3 style="color:#00d2ff;margin-bottom:15px">📰 新闻正文</h3>
            <p class="content-text">{{ news.content }}</p>
        </div>
        {% endif %}
        
        <div style="text-align:center;padding:30px">
            <a href="{{ news.link }}" target="_blank" class="original-link">🔗 查看原文</a>
        </div>
    </div>
</body>
</html>
'''

SKILL_DETAIL_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{ skill.name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh; color: #e0e0e0;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        .back-bar { margin-bottom: 30px; }
        .back-link { padding: 10px 20px; background: rgba(255,255,255,0.1); border-radius: 25px; color: #fff; text-decoration: none; }
        
        .header-section {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px; padding: 30px; text-align: center; margin-bottom: 20px;
        }
        .skill-icon {
            width: 100px; height: 100px;
            background: linear-gradient(135deg, #a8edea, #fed6e3);
            border-radius: 25px;
            display: flex; align-items: center; justify-content: center;
            font-size: 2.5em; margin: 0 auto 20px;
        }
        .skill-title { font-size: 2em; color: #a8edea; margin-bottom: 10px; }
        .skill-owner { color: #888; margin-bottom: 15px; }
        .skill-level {
            display: inline-block;
            padding: 8px 20px;
            background: linear-gradient(90deg, #a8edea, #fed6e3);
            border-radius: 20px; color: #333; font-weight: bold;
        }
        
        .section {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px; padding: 25px; margin-bottom: 20px;
        }
        .section-title { font-size: 1.1em; color: #a8edea; margin-bottom: 15px; }
        .features { display: flex; gap: 8px; flex-wrap: wrap; }
        .feature {
            padding: 6px 15px;
            background: rgba(168,237,234,0.15);
            border: 1px solid rgba(168,237,234,0.3);
            border-radius: 15px; font-size: 0.9em; color: #a8edea;
        }
        .intro-text { font-size: 1.05em; line-height: 1.8; color: #ccc; }
        .readme-content {
            font-size: 0.9em; line-height: 1.8; color: #aaa;
            white-space: pre-wrap;
            max-height: 400px; overflow-y: auto;
            background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px;
        }
        
        .download-btn {
            display: inline-flex; gap: 8px;
            padding: 15px 30px;
            background: linear-gradient(90deg, #a8edea, #fed6e3);
            border-radius: 30px; color: #333; text-decoration: none; font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="back-bar">
            <a href="/skills" class="back-link">← 返回</a>
        </div>
        
        <div class="header-section">
            <div class="skill-icon">🛠️</div>
            <h1 class="skill-title">{{ skill.name }}</h1>
            <p class="skill-owner">by {{ skill.owner }}</p>
            <span class="skill-level">{{ skill.skill_level }}</span>
        </div>
        
        <div class="section">
            <h3 class="section-title">📌 技能标签</h3>
            <div class="features">
                {% for f in (skill.features or '').split('|') %}
                <span class="feature">{{ f }}</span>
                {% endfor %}
            </div>
        </div>
        
        <div class="section">
            <h3 class="section-title">💡 能力介绍</h3>
            <p class="intro-text">{{ skill.chinese_intro }}</p>
        </div>
        
        {% if skill.readme_content %}
        <div class="section">
            <h3 class="section-title">📖 Skill说明</h3>
            <div class="readme-content">{{ skill.readme_content[:2000] }}</div>
        </div>
        {% endif %}
        
        <div style="text-align:center;padding:30px">
            <a href="{{ skill.download_url }}" target="_blank" class="download-btn">⬇️ 下载Skill</a>
            <a href="{{ skill.github_url }}" target="_blank" class="download-btn" style="margin-left:15px;background:rgba(255,255,255,0.1);color:#fff">🔗 GitHub</a>
        </div>
    </div>
</body>
</html>
'''

# ========== 数据库操作 ==========
def get_db_news(limit=50):
    if not os.path.exists(NEWS_DB): return []
    conn = sqlite3.connect(NEWS_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY hot_score DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_news_detail(news_id):
    if not os.path.exists(NEWS_DB): return None
    conn = sqlite3.connect(NEWS_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM news WHERE id = ?", (news_id,))
    row = c.fetchone()
    conn.close()
    if row:
        d = dict(row)
        try: d['keywords_list'] = json.loads(d.get('keywords','[]'))
        except: d['keywords_list'] = []
        return d
    return None

def get_skills(limit=50):
    if not os.path.exists(SKILLS_DB): return []
    conn = sqlite3.connect(SKILLS_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM skills LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_skill_detail(skill_id):
    if not os.path.exists(SKILLS_DB): return None
    conn = sqlite3.connect(SKILLS_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM skills WHERE id = ?", (skill_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_subs():
    if not os.path.exists(SUBSCRIBE_DB): return []
    conn = sqlite3.connect(SUBSCRIBE_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM subscription ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_sub(name, url, sub_type):
    conn = sqlite3.connect(SUBSCRIBE_DB)
    c = conn.cursor()
    from datetime import datetime
    c.execute("INSERT INTO subscription (name, url, sub_type, created_at) VALUES (?,?,?,?)",
              (name, url, sub_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def del_sub(sub_id):
    conn = sqlite3.connect(SUBSCRIBE_DB)
    c = conn.cursor()
    c.execute("DELETE FROM subscription WHERE id = ?", (sub_id,))
    conn.commit()
    conn.close()

def get_update_time():
    if not os.path.exists(NEWS_DB): return "暂无"
    conn = sqlite3.connect(NEWS_DB)
    c = conn.cursor()
    c.execute("SELECT created_at FROM news ORDER BY created_at DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else "暂无"

# ========== 系统管理模块 (v2.3) ==========

# 版本数据 - 每个版本独立的文档
VERSIONS = {
    'v2.5': {
        'name': 'v2.5',
        'date': '2026-03-03',
        'status': 'developing',
        'description': '研发管理规范流程重构',
        'update_intro': '''# v2.5 版本更新介绍

## 版本目标
建立规范的研发管理流程，涵盖项目管理全生命周期

## 更新内容 ✅ 已完成
1. 文档锁定功能 - 锁定文档内容只能添加不能删减
2. 版本号自动管理 - 格式XX.XX.XX，每次保存自动递增
3. 版本信息显示 - 预览页面和编辑页面顶部显示版本/时间
4. 前端字体规范 - 一级18px/二级14px/三级12px
5. 树形菜单优化 - 默认收起，取消默认选中

## 开发状态
✅ 功能开发完成 - 待用户测试确认
''',
        'features': '''# v2.5 版本功能介绍

## 已实现功能 ✅
1. 文档锁定功能
   - 预览页面顶部显示锁定按钮
   - 编辑页面顶部显示锁定按钮
   - 锁定后内容只能添加不能删减
   
2. 版本号自动管理
   - 语义化版本格式：XX.XX.XX
   - 每次保存自动递增修订号
   - 界面实时显示当前版本

3. 版本信息显示
   - 预览页面顶部：版本号(24px) + 更新时间(18px) + 锁定状态
   - 编辑页面顶部：版本号 + 更新时间 + 锁定按钮
   - 更新时间显示完整时分秒

4. 前端UI字体规范
   - 一级菜单（版本标题）：18px，白色
   - 二级菜单（功能分类）：14px，灰色
   - 三级菜单（具体文档）：12px，深灰色

5. 树形菜单交互优化
   - 默认收起状态
   - 无默认选中项
   - 点击才展开/选中
''',
        'bug_fix': '''# v2.5 BUG修复/测试报告

## 待测试
- 开发完成后进行测试
''',
        'source_code': '''# v2.5 源代码

## 开发版本
v2.5-developing

## 待发布
- 技术研发完成后生成release版本
''',
        'test_cases': '''# v2.5 测试用例

## 测试计划
1. 功能测试
2. 界面测试
3. 性能测试
4. 安全测试

## 测试用例
| ID | 用例名称 | 预期结果 | 状态 |
|----|----------|----------|------|
| TCv2.5-001 | 版本列表展示 | 显示6个版本 | ⬜ |
| TCv2.5-002 | 研发文档展示 | 显示完整文档列表 | ⬜ |
''',
        'test_report': '''# v2.5 测试报告

## 测试状态
🔄 待执行
''',
        'ops_report': '''# v2.5 运维发布报告

## 发布状态
🔄 待发布
''',
        # 研发项目管理文档
        'prd': '''# v2.5 需求文档 (PRD)

## 一、版本目标
建立规范的研发管理流程

## 二、功能需求
见系统管理 - 文档中心 - 研发管理规划
''',
        'arch': '''# v2.5 架构设计文档 (ARCH)

## 一、系统架构
见系统管理 - 文档中心 - 研发管理规划
''',
        'coding_design': '''# v2.5 代码设计文档

## 一、编码规范
## 二、接口设计
## 三、模块设计
''',
        'db_design': '''# v2.5 数据库设计文档

## 一、数据库结构
## 二、表设计
## 三、索引设计
''',
        'test_plan': '''# v2.5 测试计划

## 一、测试范围
## 二、测试策略
## 三、测试环境
''',
        # 研发计划
        'dev_plan': '''# v2.5 研发计划

## 一、项目概述
- 项目名称：研发管理流程规范化
- 项目目标：建立完整的研发项目管理流程

## 二、里程碑
| 阶段 | 计划日期 | 状态 |
|------|----------|------|
| 需求分析 | 2026-03-03 | ✅ |
| 架构设计 | 2026-03-03 | ✅ |
| 技术研发 | 待定 | ⬜ |
| 测试执行 | 待定 | ⬜ |
| 发布上线 | 待定 | ⬜ |

## 三、资源分配
- 开发人员：1
- 测试人员：1

## 四、风险评估
- 无重大风险
''',
    },
    'v2.4': {
        'name': 'v2.4',
        'date': '2026-03-03',
        'status': 'developing',
        'description': '版本管理增强、测试中心、发布管理',
        'update_intro': '''# v2.4 版本更新介绍

## 更新内容
1. 版本管理增强 - 版本对比、时间线展示、标签管理
2. 文档管理增强 - 版本历史、标签分类、搜索功能
3. 测试中心 - 测试计划、测试用例、测试报告
4. 发布管理 - 发布流程、记录追踪、回滚方案

## 开发状态
🔄 开发中 - 需求文档已确认，等待技术研发
''',
        'features': '''# v2.4 版本功能介绍

## 主要功能
1. 版本管理增强
   - 版本对比功能
   - 版本时间线展示
   - 版本标签管理

2. 文档管理增强
   - 文档版本历史
   - 文档标签分类
   - 文档搜索功能

3. 测试中心（新增）
   - 测试计划管理
   - 测试用例库
   - 测试报告生成

4. 发布管理（新增）
   - 发布流程配置
   - 发布记录追踪
   - 回滚方案管理
''',
        'bug_fix': '''# v2.4 BUG修复/测试报告

## 待测试
- 开发完成后进行测试
''',
        'source_code': '''# v2.4 源代码

## 开发版本
v2.4-developing-20260303

## 待发布
- 技术研发完成后生成release版本
''',
        'test_cases': '''# v2.4 测试用例

## 测试计划
1. 功能测试
2. 界面测试
3. 性能测试
4. 安全测试

## 测试用例
| ID | 用例名称 | 预期结果 | 状态 |
|----|----------|----------|------|
| TCv2.4-001 | 版本列表展示 | 显示6个版本 | ⬜ |
| TCv2.4-002 | 版本展开 | 展开显示7类文档 | ⬜ |
| TCv2.4-003 | 文档加载 | 加载文档内容 | ⬜ |
| TCv2.4-004 | 文档保存 | 提示保存成功 | ⬜ |
''',
        'test_report': '''# v2.4 测试报告

## 测试状态
🔄 待执行
''',
        'ops_report': '''# v2.4 运维发布报告

## 发布状态
🔄 待发布
''',
    },
    'v2.3': {
        'name': 'v2.3',
        'date': '2024-03-03',
        'status': 'current',
        'description': '系统管理全面升级',
        'update_intro': '''# v2.3 版本更新介绍

## 更新内容
1. 系统管理模块全新上线
2. 版本历史精细化展示
3. Wiki文档树形结构
4. 富文本编辑器支持

## 适用用户
- 需要管理项目版本的团队
- 需要在线编辑文档的用户
''',
        'features': '''# v2.3 版本功能介绍

## 主要功能
1. 系统管理 - 替代原研发管理
2. 版本历史 - 展示所有版本及详细功能说明
3. Wiki文档 - 树形结构直接预览
4. 富文本编辑 - 支持Markdown语法

## 技术实现
- 前后端分离架构
- Flask + Jinja2模板
- SQLite数据库
''',
        'bug_fix': '''# v2.3 BUG修复/测试报告

## 修复的问题
1. 数据库连接关闭过早问题
2. 页面布局CSS问题
3. Wiki保存功能验证

## 测试结果
- ✅ 版本切换功能正常
- ✅ 文档加载功能正常
- ✅ 文档保存功能正常
''',
        'source_code': '''# v2.3 源代码

## 发布版本
v2.3-release-20240303

## 核心文件
- app.py (主应用)
- fetch_news.py (新闻采集)
- subscribe_manager.py (订阅管理)
- cover_manager.py (封面管理)

## 代码仓库
/path/to/news_system/v2.3/
''',
        'test_cases': '''# v2.3 测试用例

## 测试计划
1. 功能测试
2. 界面测试
3. 性能测试
4. 安全测试

## 测试用例
| ID | 用例名称 | 预期结果 | 状态 |
|----|----------|----------|------|
| TC001 | 版本列表显示 | 正确显示5个版本 | ✅ |
| TC002 | 文档加载 | 点击加载对应文档内容 | ✅ |
| TC003 | 文档保存 | 编辑后成功保存到文件 | ✅ |
| TC004 | 树形菜单折叠 | 点击展开/收起正常 | ✅ |
''',
        'test_report': '''# v2.3 测试报告

## 测试概要
- 测试日期: 2024-03-03
- 测试人员: 开发团队
- 测试用例数: 15
- 通过数: 15
- 失败数: 0

## 测试结果
| 模块 | 测试项 | 结果 |
|------|--------|------|
| 版本管理 | 版本列表展示 | ✅ PASS |
| 版本管理 | 版本详情加载 | ✅ PASS |
| 文档管理 | 文档预览 | ✅ PASS |
| 文档管理 | 文档编辑保存 | ✅ PASS |
| 界面 | 树形菜单 | ✅ PASS |
| 界面 | 富文本编辑器 | ✅ PASS |
''',
        'ops_report': '''# v2.3 运维发布报告

## 发布信息
- 发布时间: 2024-03-03 14:00
- 发布人员: 开发团队
- 发布方式: 手动部署
- 回滚方案: 回退到v2.2版本

## 发布步骤
1. 备份数据库
2. 停止服务
3. 更新代码
4. 重启服务
5. 验证功能

## 发布结果
✅ 发布成功
✅ 功能验证通过
✅ 用户反馈正常
''',
    },
    'v2.2': {
        'name': 'v2.2',
        'date': '2024-03-03',
        'status': 'past',
        'description': '研发Wiki模块上线',
        'update_intro': '''# v2.2 版本更新介绍

## 更新内容
1. 研发Wiki文档管理上线
2. 版本历史展示
3. 支持Markdown文档预览和编辑
''',
        'features': '''# v2.2 版本功能介绍

## 主要功能
1. 研发Wiki文档管理
2. 版本历史展示
3. Markdown文档预览
4. 文档在线编辑
''',
        'bug_fix': '''# v2.2 BUG修复/测试报告

## 修复的问题
- 初始版本，无BUG
''',
        'source_code': '''# v2.2 源代码

## 发布版本
v2.2-release-20240303

## 核心文件
- app.py (主应用)
- docs/ (Wiki文档)
''',
        'test_cases': '''# v2.2 测试用例

## 测试用例
| ID | 用例名称 | 预期结果 | 状态 |
|----|----------|----------|------|
| TC001 | Wiki文档预览 | 显示文档内容 | ✅ |
| TC002 | Wiki文档编辑 | 可编辑保存 | ✅ |
''',
        'test_report': '''# v2.2 测试报告

## 测试结果
- 测试用例数: 8
- 通过数: 8
''',
        'ops_report': '''# v2.2 运维发布报告

## 发布结果
✅ 发布成功
''',
    },
    'v2.1': {
        'name': 'v2.1',
        'date': '2024-03-02',
        'status': 'past',
        'description': '订阅功能上线',
        'update_intro': '''# v2.1 版本更新介绍

## 更新内容
1. 文档完善
2. 订阅管理基础功能
3. 封面图管理
''',
        'features': '''# v2.1 版本功能介绍

## 主要功能
1. PRD/ARCH/TDD文档更新
2. 订阅管理增删改查
3. 新闻源手动刷新
4. 封面图获取策略优化
''',
        'bug_fix': '''# v2.1 BUG修复/测试报告

## 修复的问题
- 初始版本，无重大BUG
''',
        'source_code': '''# v2.1 源代码

## 发布版本
v2.1-release-20240302
''',
        'test_cases': '''# v2.1 测试用例

## 测试用例
| ID | 用例名称 | 预期结果 | 状态 |
|----|----------|----------|------|
| TC001 | 订阅添加 | 成功添加订阅 | ✅ |
| TC002 | 订阅删除 | 成功删除订阅 | ✅ |
''',
        'test_report': '''# v2.1 测试报告

## 测试结果
- 测试用例数: 5
- 通过数: 5
''',
        'ops_report': '''# v2.1 运维发布报告

## 发布结果
✅ 发布成功
''',
    },
    'v2.0': {
        'name': 'v2.0',
        'date': '2024-03-01',
        'status': 'past',
        'description': '核心重构',
        'update_intro': '''# v2.0 版本更新介绍

## 更新内容
1. 三大数据源采集
2. AI分析功能
3. Skills模块集成
4. 订阅管理
''',
        'features': '''# v2.0 版本功能介绍

## 主要功能
1. 新闻采集：163网易/新浪科技/凤凰网科技
2. AI分析：关键词提取/实体识别/热度计算
3. Skills模块：clawhub 10个Skills
4. 订阅管理：网站/RSS/视频/论坛
''',
        'bug_fix': '''# v2.0 BUG修复/测试报告

## 修复的问题
- 初始版本，无BUG
''',
        'source_code': '''# v2.0 源代码

## 发布版本
v2.0-release-20240301
''',
        'test_cases': '''# v2.0 测试用例

## 测试用例
| ID | 用例名称 | 预期结果 | 状态 |
|----|----------|----------|------|
| TC001 | 新闻采集 | 成功采集数据 | ✅ |
''',
        'test_report': '''# v2.0 测试报告

## 测试结果
- 测试用例数: 3
- 通过数: 3
''',
        'ops_report': '''# v2.0 运维发布报告

## 发布结果
✅ 发布成功
''',
    },
    'v1.0': {
        'name': 'v1.0',
        'date': '2024-02-28',
        'status': 'past',
        'description': '初始版本',
        'update_intro': '''# v1.0 版本更新介绍

## 更新内容
初始版本发布
''',
        'features': '''# v1.0 版本功能介绍

## 主要功能
1. 基础新闻采集
2. 卡片式新闻展示
3. SQLite数据存储
''',
        'bug_fix': '''# v1.0 BUG修复/测试报告

## 修复的问题
- 初始版本，无BUG
''',
        'source_code': '''# v1.0 源代码

## 发布版本
v1.0-release-20240228
''',
        'test_cases': '''# v1.0 测试用例

## 测试用例
| ID | 用例名称 | 预期结果 | 状态 |
|----|----------|----------|------|
| TC001 | 首页展示 | 显示新闻列表 | ✅ |
''',
        'test_report': '''# v1.0 测试报告

## 测试结果
- 测试用例数: 1
- 通过数: 1
''',
        'ops_report': '''# v1.0 运维发布报告

## 发布结果
✅ 首发成功
''',
    },
}

# 文档中心 - 总文档
DOCS_CENTER = [
    {'id': 'dev_manual', 'name': '研发管理规范.md', 'title': '📘 研发管理规范', 'category': '规范'},
    {'id': 'doc_spec', 'name': '文档撰写规范.md', 'title': '📝 文档撰写规范', 'category': '规范'},
    {'id': 'prd', 'name': 'PRD.md', 'title': '📋 需求文档 (v2.4)', 'category': '产品'},
    {'id': 'arch', 'name': 'ARCH.md', 'title': '📐 架构文档 (v2.4)', 'category': '设计'},
    {'id': 'tdd', 'name': 'TDD.md', 'title': '📝 技术文档 (v2.4)', 'category': '技术'},
    {'id': 'dev', 'name': 'DEVELOPMENT.md', 'title': '🔧 开发文档 (v2.4)', 'category': '技术'},
    {'id': 'test_plan', 'name': 'TEST_PLAN.md', 'title': '📋 测试计划 (v2.4)', 'category': '测试'},
    {'id': 'test_case', 'name': 'TEST_CASE.md', 'title': '📝 测试用例 (v2.4)', 'category': '测试'},
]

def list_docs():
    """获取文档列表 - 从文档中心和版本历史扫描"""
    docs = []
    
    # 新的文档中心目录（优先）
    if os.path.exists(DOCS_CENTER_DIR):
        for fname in os.listdir(DOCS_CENTER_DIR):
            if fname.endswith('.md'):
                title = fname.replace('.md', '')
                docs.append({
                    'id': fname.replace('.md', ''),
                    'name': fname,
                    'title': title,
                    'category': '文档中心',
                    'version': 'current'
                })
    
    # 旧版文档中心目录（兼容）
    docs_center_dir = os.path.join(VERSION_DOCS_DIR, 'docs')
    if os.path.exists(docs_center_dir):
        for fname in os.listdir(docs_center_dir):
            if fname.endswith('.md'):
                title = fname.replace('.md', '')
                # 避免重复
                if not any(d['name'] == fname for d in docs):
                    docs.append({
                        'id': fname.replace('.md', ''),
                        'name': fname,
                        'title': title,
                        'category': '文档中心(旧)',
                        'version': 'current'
                    })
    
    # 如果文档中心为空，使用旧文档目录
    if not docs:
        return DOCS_CENTER
    
    return docs

# 版本列表（用于模板）
def get_versions_list():
    return VERSIONS

def get_version_files():
    """获取所有版本目录下的文件 - 用于动态生成版本树"""
    version_files = {}
    
    # ★ 1. 优先扫描版本管理目录（v2.4 新增）
    if os.path.exists(VERSION_MANAGE_DIR):
        for version_dir in os.listdir(VERSION_MANAGE_DIR):
            version_path = os.path.join(VERSION_MANAGE_DIR, version_dir)
            if os.path.isdir(version_path):
                files = []
                for f in os.listdir(version_path):
                    if f.endswith('.md'):
                        files.append(f)
                if files:
                    def sort_key(filename):
                        match = re.match(r'^(\d+)', filename)
                        return int(match.group(1)) if match else 999
                    version_files[version_dir] = sorted(files, key=sort_key)
    
    # 2. 扫描新版本历史目录
    if os.path.exists(VERSION_HISTORY_DIR):
        for version_dir in os.listdir(VERSION_HISTORY_DIR):
            version_path = os.path.join(VERSION_HISTORY_DIR, version_dir)
            if os.path.isdir(version_path):
                files = []
                for f in os.listdir(version_path):
                    if f.endswith('.md'):
                        files.append(f)
                if files:
                    # 按数字前缀排序（如 01-xxx.md, 02-xxx.md）
                    def sort_key(filename):
                        match = re.match(r'^(\d+)', filename)
                        return int(match.group(1)) if match else 999
                    version_files[version_dir] = sorted(files, key=sort_key)
    
    # 2. 扫描旧版本目录（兼容）
    if os.path.exists(VERSION_DOCS_DIR):
        for version_dir in os.listdir(VERSION_DOCS_DIR):
            if version_dir == 'docs':
                continue
            version_path = os.path.join(VERSION_DOCS_DIR, version_dir)
            if os.path.isdir(version_path) and version_dir.startswith('v'):
                if version_dir not in version_files:
                    files = []
                    for f in os.listdir(version_path):
                        if f.endswith('.md'):
                            files.append(f)
                    if files:
                        version_files[version_dir] = sorted(files)
    
    # 按版本号排序（倒序，最新的在前）
    def version_key(v):
        """提取版本号用于排序，如 v2.4.0 -> (2, 4, 0)"""
        import re
        match = re.match(r'v(\d+)\.(\d+)(?:\.(\d+))?', v)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3)) if match.group(3) else 0
            return (major, minor, patch)
        return (0, 0, 0)
    
    sorted_versions = dict(sorted(version_files.items(), key=lambda x: version_key(x[0]), reverse=True))
    return sorted_versions

def get_doc(filename):
    """读取文档内容 - 支持文档中心和版本目录"""
    if not filename.endswith('.md'):
        return None
    
    # 如果filename包含版本前缀（如v2.4/PRD.md），提取出来
    version_prefix = None
    filename_only = filename
    if '/' in filename:
        parts = filename.split('/')
        if len(parts) == 2 and parts[0].startswith('v'):
            version_prefix = parts[0]
            filename_only = parts[1]
    
    # 1. 如果有版本前缀，直接在对应版本目录查找
    if version_prefix:
        # ★ 优先查找版本管理目录（v2.4 新增）
        test_path = os.path.join(VERSION_MANAGE_DIR, version_prefix, filename_only)
        if os.path.exists(test_path):
            try:
                with open(test_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
        # 新版本历史目录
        test_path = os.path.join(VERSION_HISTORY_DIR, version_prefix, filename_only)
        if os.path.exists(test_path):
            try:
                with open(test_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
        # 旧版本目录
        test_path = os.path.join(VERSION_DOCS_DIR, version_prefix, filename_only)
        if os.path.exists(test_path):
            try:
                with open(test_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
    
    # 2. 优先从新的文档中心读取
    if os.path.exists(DOCS_CENTER_DIR):
        filepath = os.path.join(DOCS_CENTER_DIR, filename_only)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
    
    # 3. 尝试在新的版本历史目录中查找
    if os.path.exists(VERSION_HISTORY_DIR):
        for version_dir in os.listdir(VERSION_HISTORY_DIR):
            version_path = os.path.join(VERSION_HISTORY_DIR, version_dir)
            if os.path.isdir(version_path):
                filepath = os.path.join(version_path, filename_only)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            return f.read()
                    except:
                        pass
    
    # 4. 兼容旧的文档中心目录
    docs_center_dir = os.path.join(VERSION_DOCS_DIR, 'docs')
    filepath = os.path.join(docs_center_dir, filename_only)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            pass
    
    # 5. 尝试在旧版本子目录中查找
    if os.path.exists(VERSION_DOCS_DIR):
        for version_dir in os.listdir(VERSION_DOCS_DIR):
            version_path = os.path.join(VERSION_DOCS_DIR, version_dir)
            if os.path.isdir(version_path) and version_dir.startswith('v'):
                filepath = os.path.join(version_path, filename_only)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            return f.read()
                    except:
                        return None
    
    # 6. 兼容旧目录
    filepath = os.path.join(DOCS_DIR, filename_only)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    return None

def save_doc(filename, content, locked=False, version_dir=None):
    """
    保存文档内容，自动记录修改时间和版本
    
    技术方案：
    1. 验证filename是.md文件
    2. 查找文档实际路径（优先级：指定目录 > 文档中心 > 版本目录 > 旧目录）
    3. 确定doc_version（用于生成版本key）
    4. 保存文档内容到文件
    5. 读取/初始化版本数据库
    6. 更新版本号（自动+1）
    7. 更新锁定状态
    8. 记录更新时间
    9. 保存版本数据库
    """
    # Step 1: 验证文件类型
    if not filename.endswith('.md'):
        return False
    
    import json
    from datetime import datetime
    
    filepath = None
    doc_version = None
    
    # Step 2: 查找文档路径
    # 优先级：指定目录 > 新文档中心 > 新版本历史 > 旧文档中心 > 旧版本目录 > 旧目录
    
    # 2.1 指定版本目录（如v2.5）- 优先新目录
    if version_dir:
        version_path = os.path.join(VERSION_HISTORY_DIR, version_dir)
        if os.path.isdir(version_path):
            test_path = os.path.join(version_path, filename)
            if os.path.exists(test_path):
                filepath = test_path
                doc_version = version_dir
    
    # 2.2 新文档中心
    if not filepath:
        test_path = os.path.join(DOCS_CENTER_DIR, filename)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = 'current'
    
    # 2.3 新版本子目录
    if not filepath and os.path.exists(VERSION_HISTORY_DIR):
        for vdir in os.listdir(VERSION_HISTORY_DIR):
            if vdir in ['docs', version_dir]:
                continue
            vpath = os.path.join(VERSION_HISTORY_DIR, vdir)
            if os.path.isdir(vpath):
                test_path = os.path.join(vpath, filename)
                if os.path.exists(test_path):
                    filepath = test_path
                    doc_version = vdir
                    break
    
    # 2.4 旧版文档中心
    if not filepath:
        docs_center = os.path.join(VERSION_DOCS_DIR, 'docs')
        test_path = os.path.join(docs_center, filename)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = 'current'
    
    # 2.5 旧版本子目录
    if not filepath and os.path.exists(VERSION_DOCS_DIR):
        for vdir in os.listdir(VERSION_DOCS_DIR):
            if vdir in ['docs', version_dir]:
                continue
            vpath = os.path.join(VERSION_DOCS_DIR, vdir)
            if os.path.isdir(vpath) and vdir.startswith('v'):
                test_path = os.path.join(vpath, filename)
                if os.path.exists(test_path):
                    filepath = test_path
                    doc_version = vdir
                    break
    
    # 2.6 旧目录
    if not filepath:
        filepath = os.path.join(DOCS_DIR, filename)
    
    # 如果文件不存在但目录存在，创建它
    filepath_dir = os.path.dirname(filepath)
    if not os.path.exists(filepath_dir):
        os.makedirs(filepath_dir, exist_ok=True)
    
    # Step 3: 保存文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False
    
    # Step 4: 更新版本数据库
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # 读取数据库
    version_data = {}
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
        except:
            pass
    
    # 构建key
    doc_key = f"{doc_version}/{filename}"
    
    # 初始化或更新
    if doc_key not in version_data:
        version_data[doc_key] = {
            'major': 1, 'minor': 0, 'patch': 0, 
            'history': [], 'locked': False
        }
    
    # 递增版本号
    version_data[doc_key]['patch'] += 1
    patch = version_data[doc_key]['patch']
    major = version_data[doc_key]['major']
    minor = version_data[doc_key]['minor']
    current_version = f"{major}.{minor}.{patch}"
    
    # 更新字段
    version_data[doc_key]['last_update'] = now_str
    version_data[doc_key]['locked'] = locked
    version_data[doc_key]['history'].append({
        'version': current_version,
        'time': now_str,
        'action': '更新'
    })
    # 只保留最近10条
    version_data[doc_key]['history'] = version_data[doc_key]['history'][-10:]
    
    # 保存数据库
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存数据库失败: {e}")
        return False
    
    return True

# ========== 系统管理模板 ==========
SYS_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系统管理</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            color: #e0e0e0;
        }
        
        .header-bar {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header-bar h1 { font-size: 1.5em; margin: 0; }
        
        .nav { display: flex; gap: 10px; }
        .nav a {
            padding: 8px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            color: #aaa;
            text-decoration: none;
            font-size: 0.9em;
        }
        .nav a:hover, .nav a.active {
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            color: #fff;
        }
        
        .container { 
            display: flex; 
            height: calc(100vh - 70px); 
            overflow: hidden;
        }
        
        /* 左侧导航 - 树形结构 */
        .sidebar {
            width: 240px;
            min-width: 200px;
            background: rgba(0,0,0,0.3);
            border-right: 1px solid rgba(255,255,255,0.1);
            flex-shrink: 0;
            overflow-y: auto;
            padding: 15px;
        }
        
        /* 右侧内容区 */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-width: 0;
            background: rgba(0,0,0,0.15);
            padding: 20px;
        }
        
        .sidebar-section { margin-bottom: 15px; }
        .sidebar-title {
            font-size: 0.75em;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 8px;
            padding-bottom: 5px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        /* 树形结构 */
        .tree-item {
            margin-bottom: 3px;
        }
        .tree-folder {
            padding: 8px 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            /* 字体规范 - 一级菜单（版本标题） */
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            transition: all 0.2s;
        }
        .tree-folder:hover { background: rgba(255,255,255,0.1); color: #fff; }
        .tree-folder.open { background: rgba(0,210,255,0.1); color: #00d2ff; }
        
        .tree-children {
            display: none;
            padding-left: 15px;
            margin-top: 3px;
        }
        .tree-children.show { display: block; }
        
        .tree-node {
            padding: 8px 10px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            /* 字体规范 - 二级菜单（功能分类） */
            font-size: 14px;
            color: #aaa;
            transition: all 0.2s;
        }
        .tree-node:hover { background: rgba(255,255,255,0.1); color: #ccc; }
        .tree-node.active { background: rgba(0,210,255,0.2); color: #00d2ff; }
        
        /* 字体规范 - 三级菜单（具体文档） */
        .tree-label {
            font-size: 12px;
            color: #888;
        }
        
        .tree-icon { font-size: 1em; }
        
        /* 右侧内容区 */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .content-header {
            padding: 15px 25px;
            background: rgba(0,0,0,0.2);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .content-title { font-size: 1.2em; color: #00d2ff; }
        
        .content-body {
            flex: 1;
            overflow-y: auto;
            padding: 25px;
        }
        
        /* 富文本编辑器 */
        .editor-container { height: 100%; display: flex; flex-direction: column; }
        .editor-toolbar {
            padding: 10px;
            background: rgba(0,0,0,0.3);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        .toolbar-btn {
            padding: 6px 12px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 6px;
            color: #aaa;
            cursor: pointer;
            font-size: 0.85em;
        }
        .toolbar-btn:hover { background: rgba(255,255,255,0.2); color: #fff; }
        .toolbar-btn.active { background: #00d2ff; color: #fff; }
        
        .editor-textarea {
            flex: 1;
            width: 100%;
            background: rgba(255,255,255,0.03);
            border: none;
            padding: 20px;
            color: #e0e0e0;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 0.95em;
            line-height: 1.8;
            resize: none;
        }
        .editor-textarea:focus { outline: none; }
        
        .editor-header {
            padding: 15px 20px;
            background: rgba(0,0,0,0.3);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .editor-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .editor-doc-name {
            font-size: 1.1em;
            color: #00d2ff;
            font-weight: bold;
        }
        .editor-meta {
            font-size: 0.8em;
            color: #888;
        }
        
        .editor-footer {
            padding: 15px 25px;
            background: rgba(0,0,0,0.2);
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .btn {
            padding: 10px 25px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
        }
        .btn-cancel { background: rgba(255,255,255,0.1); color: #aaa; margin-right: 10px; }
        .btn-save { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: #fff; }
        .btn:hover { opacity: 0.9; }
        
        /* 版本详情 */
        .version-detail { display: none; }
        .version-detail.active { display: block; }
        .detail-header {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .detail-title { font-size: 1.5em; margin-bottom: 10px; }
        .detail-desc { color: #aaa; margin-bottom: 15px; }
        
        .detail-section { margin-bottom: 20px; }
        .detail-section h3 { 
            font-size: 1em; 
            color: #00d2ff; 
            margin-bottom: 12px; 
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .detail-list { list-style: none; padding: 0; }
        .detail-list li { 
            padding: 10px 0; 
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }
        .detail-list li:before { content: "✓"; color: #00d2ff; }
        
        /* 默认显示 */
        #versionDetail0 { display: block; }
    </style>
</head>
<body>
    <div class="header-bar">
        <h1>⚙️ 系统管理</h1>
        <div class="nav">
            <a href="/" class="nav-tab">🏠 首页</a>
            <a href="/skills" class="nav-tab">🛠️ Skills</a>
            <a href="/subscribe" class="nav-tab">📥 订阅</a>
        </div>
    </div>
    
    <div class="container">
        <!-- 左侧树形导航 -->
        <div class="sidebar">
            <!-- 版本树 - 动态生成 -->
            <div class="sidebar-section">
                <div class="sidebar-title">📋 版本历史</div>
                {% if version_files %}
                {% for version_id, files in version_files.items() %}
                <div class="tree-item">
                    <div class="tree-folder" onclick="toggleTree(this)">
                        <span>📦</span> <span>{{ version_id }}</span>
                    </div>
                    <div class="tree-children">
                        {% for file in files %}
                        <div class="tree-node" onclick="loadVersionFile('{{ version_id }}', '{{ file }}', this)">
                            <span class="tree-icon">📄</span> <span class="tree-label">{{ file.replace('.md', '') }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
                {% else %}
                <!-- 兼容旧版本：如果没有version_files，显示默认版本 -->
                <div class="tree-item">
                    <div class="tree-folder" onclick="toggleTree(this)">
                        <span>🔄</span> <span>v2.5 - 研发管理规范</span>
                    </div>
                    <div class="tree-children">
                        <div class="tree-node" onclick="loadVersionDoc('v2.5', 'update_intro', this)"><span class="tree-icon">📝</span> <span class="tree-label">更新介绍</span></div>
                        <div class="tree-node" onclick="loadVersionDoc('v2.5', 'prd', this)"><span class="tree-icon">📋</span> <span class="tree-label">需求文档</span></div>
                        <div class="tree-node" onclick="loadVersionDoc('v2.5', 'arch', this)"><span class="tree-icon">🏗️</span> <span class="tree-label">架构设计</span></div>
                        <div class="tree-node" onclick="loadVersionDoc('v2.5', 'tdd', this)"><span class="tree-icon">💻</span> <span class="tree-label">技术设计</span></div>
                    </div>
                </div>
                {% endif %}
            </div>
            
            <!-- 文档树 -->
            <div class="sidebar-section">
                <div class="sidebar-title">📚 文档中心</div>
                {% for doc in docs %}
                <div class="tree-item">
                    <div class="tree-node" onclick="loadDoc('{{ doc.name }}', this)">
                        <span class="tree-icon">📄</span> <span class="tree-label">{{ doc.name }} - {{ doc.title }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- 右侧内容区 -->
        <div class="main-content">
            <!-- 版本信息面板 -->
            <div id="versionPanel" style="color:#ccc; padding:20px; overflow-y:auto;">
                <h2 style="color:#00d2ff;margin-bottom:20px;">📋 版本详情</h2>
                <p style="color:#888;margin-bottom:20px;">点击左侧版本查看详情，或选择文档进行编辑</p>
                {% for v in versions %}
                <div id="versionDetail{{ loop.index0 }}" style="margin-bottom:30px;display:none;">
                    <h3 style="color:#fff;margin-bottom:10px;">{{ v.name }} {% if v.status == 'current' %}<span style="color:#ff6b6b">(当前版本)</span>{% endif %}</h3>
                    <p style="color:#888;margin-bottom:15px;">📅 {{ v.date }}</p>
                </div>
                {% endfor %}
            </div>
            
            <!-- Wiki编辑器 -->
            <div id="wikiPanel" class="editor-container" style="display:none;">
                <!-- 版本信息栏 - 放大显示 -->
                <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(0,210,255,0.3); border-radius: 12px; padding: 15px 20px; margin-bottom: 15px; display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                    <span style="font-size: 24px; font-weight: bold; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📋 版本: {{ doc_version }}</span>
                    <span style="font-size: 18px; color: #aaa;">🕐 更新时间: {{ doc_mtime }}</span>
                    {% if doc_locked %}
                    <span style="font-size: 18px; background: #ff6b6b; color: #fff; padding: 6px 15px; border-radius: 15px; font-weight: bold;">🔒 已锁定</span>
                    {% endif %}
                    <button id="sysLockBtn" style="font-size: 16px; background: {% if doc_locked %}#4CAF50{% else %}#ff6b6b{% endif %}; color: #fff; padding: 6px 15px; border-radius: 15px; cursor: pointer; border: none; font-weight: bold;" onclick="toggleSysLock()">
                        {% if doc_locked %}🔓 解锁{% else %}🔒 锁定{% endif %}
                    </button>
                </div>
                
                <div class="editor-header">
                    <div class="editor-info">
                        <span class="editor-doc-name">{{ current_doc }}</span>
                        <span class="editor-meta">修改时间: {{ doc_mtime }} | 版本: {{ doc_version }}</span>
                    </div>
                </div>
                <div class="editor-toolbar">
                    <button class="toolbar-btn" onclick="formatText('**', '**')" title="粗体">B</button>
                    <button class="toolbar-btn" onclick="formatText('*', '*')" title="斜体">I</button>
                    <button class="toolbar-btn" onclick="formatText('# ', '')" title="标题">H</button>
                    <button class="toolbar-btn" onclick="formatText('- ', '')" title="列表">•</button>
                    <button class="toolbar-btn" onclick="formatText('```', '```')" title="代码">&lt;/&gt;</button>
                    <button class="toolbar-btn" onclick="formatText('[', '](url)')" title="链接">🔗</button>
                    <button class="toolbar-btn" onclick="formatText('| ', ' | ')" title="表格">⊞</button>
                </div>
                <textarea id="docEditor" class="editor-textarea" placeholder="选择左侧文档开始编辑...">{{ doc_content }}</textarea>
                <div class="editor-footer">
                    <span id="docStatus" style="color:#666;font-size:0.85em">已加载: {{ current_doc }}</span>
                    <div>
                        <button class="btn btn-cancel" onclick="cancelEdit()">取消</button>
                        <button class="btn btn-save" onclick="saveDoc()">💾 保存</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- V2.5新版JavaScript（修复版本管理BUG） -->
    <script src="/static/sys_v2.js"></script>
    
    <!-- 内联变量初始化 -->
    <script>
        currentDoc = '{{ current_doc }}';
        isSysLocked = {{ 'true' if doc_locked else 'false' }};
        
        // 默认加载第一个文档
        {% if doc_content %}
        document.getElementById('versionPanel').style.display = 'none';
        document.getElementById('wikiPanel').style.display = 'flex';
        {% endif %}
    </script>
</body>
</html>
'''

# ========== Wiki预览模板 ==========
WIKI_VIEW_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{ filename }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header-left { display: flex; gap: 15px; align-items: center; }
        .back-link, .dev-link {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 25px;
            color: #fff;
            text-decoration: none;
        }
        .back-link:hover, .dev-link:hover { background: rgba(255,255,255,0.2); }
        
        .edit-btn {
            padding: 10px 20px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            border-radius: 25px;
            color: #fff;
            text-decoration: none;
        }
        
        /* 版本信息栏 - 放大显示 */
        .version-bar {
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(0,210,255,0.3);
            border-radius: 16px;
            padding: 20px 30px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 25px;
            flex-wrap: wrap;
        }
        .version-bar .version-badge {
            font-size: 28px;
            font-weight: bold;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .version-bar .time-badge {
            font-size: 20px;
            color: #aaa;
        }
        .version-bar .locked-badge {
            font-size: 20px;
            background: #ff6b6b;
            color: #fff;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
        }
        .version-bar .lock-btn {
            font-size: 18px;
            background: #ff6b6b;
            color: #fff;
            padding: 8px 20px;
            border-radius: 20px;
            cursor: pointer;
            border: none;
            font-weight: bold;
        }
        .version-bar .lock-btn.unlocked {
            background: #4CAF50;
        }
        
        .content {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 30px;
            white-space: pre-wrap;
            line-height: 1.8;
            font-size: 0.95em;
            max-height: 80vh;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 版本信息栏 - 预览页面也显示 -->
        <div class="version-bar">
            <span class="version-badge">📋 版本: {{ version }}</span>
            <span class="time-badge">🕐 更新时间: {{ mtime }}</span>
            {% if locked %}
            <span class="locked-badge">🔒 已锁定</span>
            {% endif %}
            <button class="lock-btn {% if not locked %}unlocked{% endif %}" onclick="toggleLock()">
                {% if locked %}🔓 解锁{% else %}🔒 锁定{% endif %}
            </button>
        </div>
        
        <div class="header">
            <div class="header-left">
                <a href="/dev?tab=wiki" class="dev-link">📚 文档列表</a>
                <a href="/dev" class="back-link">← 研发管理</a>
            </div>
            <a href="/wiki/{{ filename }}/edit" class="edit-btn">✏️ 编辑</a>
        </div>
        <div class="content">{{ content }}</div>
    
    <script>
        let isLocked = {{ 'true' if locked else 'false' }};
        
        function toggleLock() {
            isLocked = !isLocked;
            
            // 更新按钮显示
            const btn = document.querySelector('.lock-btn');
            if (isLocked) {
                btn.innerHTML = '🔓 解锁';
                btn.classList.remove('unlocked');
            } else {
                btn.innerHTML = '🔒 锁定';
                btn.classList.add('unlocked');
            }
            
            // 更新锁定标记显示
            const lockedBadge = document.querySelector('.locked-badge');
            if (lockedBadge) {
                lockedBadge.remove();
            }
            if (isLocked) {
                const versionBar = document.querySelector('.version-bar');
                const badge = document.createElement('span');
                badge.className = 'locked-badge';
                badge.innerHTML = '🔒 已锁定';
                versionBar.insertBefore(badge, btn);
            }
            
            alert(isLocked ? '文档已锁定：内容只能添加不能删减' : '文档已解锁：可以自由编辑');
            
            // 保存锁定状态
            fetch('/api/wiki/{{ filename }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: '{{ content|replace("'", "\\'")|replace("\\n", "\\\\n") }}', locked: isLocked})
            }).then(r => r.json()).then(data => {
                if (data.code === 200) {
                    location.reload();
                } else {
                    alert(data.msg || '保存失败');
                }
            });
        }
    </script>
    </div>
</body>
</html>
'''

# ========== Wiki编辑模板 ==========
WIKI_EDIT_TPL = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>编辑 {{ filename }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header h2 { color: #00d2ff; }
        .btn-group { display: flex; gap: 10px; }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            text-decoration: none;
        }
        .btn-cancel { background: rgba(255,255,255,0.1); color: #aaa; }
        .btn-cancel:hover { background: rgba(255,255,255,0.2); color: #fff; }
        .btn-save { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: #fff; }
        
        textarea {
            width: 100%;
            min-height: 70vh;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0e0e0;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 0.95em;
            line-height: 1.6;
            resize: vertical;
        }
        textarea:focus { outline: none; border-color: #00d2ff; }
        
        .version-info {
            margin-top: 10px;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }
        .version-badge {
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            color: #fff;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 24px;
            font-weight: bold;
        }
        .time-badge {
            color: #aaa;
            font-size: 18px;
        }
        .locked-badge {
            background: #ff6b6b;
            color: #fff;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 20px;
            font-weight: bold;
        }
        .lock-btn {
            background: #ff6b6b;
            color: #fff;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 18px;
            cursor: pointer;
            border: none;
            font-weight: bold;
        }
        .lock-btn.unlocked {
            background: #4CAF50;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h2>📝 编辑: {{ filename }}</h2>
                <div class="version-info">
                    <span class="version-badge">📋 版本: {{ version }}</span>
                    <span class="time-badge">🕐 更新时间: {{ mtime }}</span>
                    {% if locked %}
                    <span class="locked-badge">🔒 已锁定</span>
                    {% endif %}
                    <button class="lock-btn {% if not locked %}unlocked{% endif %}" onclick="toggleLock()">
                        {% if locked %}🔓 解锁{% else %}🔒 锁定{% endif %}
                    </button>
                </div>
            </div>
            <div class="btn-group">
                <a href="/wiki/{{ filename }}" class="btn btn-cancel">← 取消</a>
                <button onclick="saveDoc()" class="btn btn-save">💾 保存</button>
            </div>
        </div>
        <textarea id="editor">{{ content }}</textarea>
    </div>
    
    <script>
        let isLocked = {{ 'true' if locked else 'false' }};
        
        function toggleLock() {
            // 切换锁定状态
            isLocked = !isLocked;
            
            // 更新按钮显示
            const btn = document.querySelector('.lock-btn');
            if (isLocked) {
                btn.innerHTML = '🔓 解锁';
                btn.classList.remove('unlocked');
            } else {
                btn.innerHTML = '🔒 锁定';
                btn.classList.add('unlocked');
            }
            
            // 更新锁定标记显示
            const lockedBadge = document.querySelector('.locked-badge');
            if (lockedBadge) {
                lockedBadge.remove();
            }
            if (isLocked) {
                const infoDiv = document.querySelector('.version-info');
                const badge = document.createElement('span');
                badge.className = 'locked-badge';
                badge.innerHTML = '🔒 已锁定';
                infoDiv.appendChild(badge);
            }
            
            alert(isLocked ? '文档已锁定：内容只能添加不能删减' : '文档已解锁：可以自由编辑');
        }
        
        function saveDoc() {
            const content = document.getElementById('editor').value;
            
            // 如果是锁定状态，检查是否删减了内容
            if (isLocked) {
                // 获取原始内容进行比较
                fetch('/api/wiki/raw/{{ filename }}')
                    .then(r => r.json())
                    .then(data => {
                        if (data.content && content.length < data.content.length - 50) {
                            alert('⚠️ 此文档已锁定，内容只能添加不能删减！');
                            return;
                        }
                        doSave(content);
                    });
            } else {
                doSave(content);
            }
        }
        
        function doSave(content) {
            fetch('/api/wiki/{{ filename }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content, locked: isLocked})
            }).then(r => r.json()).then(d => {
                if(d.code === 200) {
                    alert('保存成功');
                    location.href = '/wiki/{{ filename }}';
                } else {
                    alert('保存失败: ' + d.msg);
                }
            }).catch(e => {
                alert('保存失败: ' + e);
            });
        }
    </script>
</body>
</html>
'''

# ========== 路由 ==========
@app.route('/')
def index():
    news = get_db_news()
    return render_template_string(INDEX_TPL, news=news, update_time=get_update_time(), get_cover=get_cover)

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news = get_news_detail(news_id)
    if not news: return "新闻不存在", 404
    return render_template_string(NEWS_DETAIL_TPL, news=news, get_cover=get_cover)

@app.route('/skills')
def skills():
    skills_list = get_skills()
    return render_template_string(SKILLS_TPL, skills=skills_list)

@app.route('/skill/<int:skill_id>')
def skill_detail(skill_id):
    skill = get_skill_detail(skill_id)
    if not skill: return "Skill不存在", 404
    return render_template_string(SKILL_DETAIL_TPL, skill=skill)

@app.route('/subscribe')
def subscribe():
    subs = get_subs()
    return render_template_string(SUBSCRIBE_TPL, subs=subs)

@app.route('/api/subscribe', methods=['POST'])
def api_add_sub():
    data = request.json
    try:
        add_sub(data.get('name'), data.get('url'), data.get('type', 'website'))
        return jsonify({'code': 200, 'msg': 'success'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})

@app.route('/api/subscribe/<int:sub_id>', methods=['DELETE'])
def api_del_sub(sub_id):
    try:
        del_sub(sub_id)
        return jsonify({'code': 200, 'msg': 'success'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})

@app.route('/api/refresh')
def refresh():
    try:
        subprocess.run(['python3', '/home/zhang/news_system/fetch_news.py'], 
                      capture_output=True, timeout=120)
        return '<script>location.href="/"</script>'
    except Exception as e:
        return f'错误: {e}'

# ========== 系统管理路由 ==========
@app.route('/sys')
def sys_page():
    """系统管理首页"""
    docs = list_docs()
    version_files = get_version_files()
    # 默认显示版本信息，不加载文档
    return render_template_string(SYS_TPL, versions=list(VERSIONS.values()), docs=docs, 
                                 current_doc='', doc_content='', doc_mtime='',
                                 version_files=version_files)

@app.route('/sys/version/<version_id>/<doc_type>')
def sys_version_doc(version_id, doc_type):
    """系统管理-版本详情文档"""
    if version_id not in VERSIONS:
        return "版本不存在", 404
    
    # 文档类型映射
    doc_map = {
        'update_intro': '📝 更新介绍',
        'features': '✨ 功能介绍', 
        'bug_fix': '🐛 BUG修复',
        'source_code': '💻 源代码',
        'test_cases': '📋 测试用例',
        'test_report': '📊 测试报告',
        'ops_report': '🚀 运维发布报告',
        # 研发项目管理
        'dev_plan': '📅 研发计划',
        'prd': '📋 需求文档',
        'arch': '🏗️ 架构设计',
        'coding_design': '💻 代码设计',
        'db_design': '🗄️ 数据库设计',
        'test_plan': '🧪 测试文档',
    }
    
    if doc_type not in doc_map:
        return "文档类型不存在", 404
    
    version = VERSIONS[version_id]
    content = version.get(doc_type, '')
    doc_title = doc_map[doc_type]
    
    docs = list_docs()
    version_files = get_version_files()
    return render_template_string(SYS_TPL, versions=list(VERSIONS.values()), docs=docs,
                                 current_doc=f'{version_id}/{doc_type}', doc_content=content, 
                                 doc_mtime=version.get('date', ''), doc_title=doc_title,
                                 version_id=version_id, doc_type=doc_type,
                                 version_files=version_files)

@app.route('/sys/wiki/<path:filename>')
def sys_wiki(filename):
    """系统管理-Wiki编辑"""
    if not filename.endswith('.md'):
        return "不支持的文件类型", 400
    
    docs = list_docs()
    content = get_doc(filename)
    if content is None:
        return "文档不存在", 404
    
    # 从版本数据库读取版本、时间、锁定状态
    import json
    import time
    
    # 如果filename包含版本前缀（如v2.4/PRD.md），提取出来
    version_prefix = None
    filename_only = filename
    if '/' in filename:
        parts = filename.split('/')
        if len(parts) == 2 and parts[0].startswith('v'):
            version_prefix = parts[0]
            filename_only = parts[1]
    
    # 查找文档所在的目录
    doc_version = "current"
    filepath = None
    
    # 1. 如果有版本前缀，直接在对应版本目录查找
    if version_prefix:
        # 新版本历史目录
        test_path = os.path.join(VERSION_HISTORY_DIR, version_prefix, filename_only)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = version_prefix
        else:
            # 旧版本目录
            test_path = os.path.join(VERSION_DOCS_DIR, version_prefix, filename_only)
            if os.path.exists(test_path):
                filepath = test_path
                doc_version = version_prefix
    
    # 2. 新文档中心
    if not filepath:
        test_path = os.path.join(DOCS_CENTER_DIR, filename_only)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = "current"
    
    # 3. 新版本历史目录（无前缀）
    if not filepath and os.path.exists(VERSION_HISTORY_DIR):
        for version_dir in os.listdir(VERSION_HISTORY_DIR):
            version_path = os.path.join(VERSION_HISTORY_DIR, version_dir)
            if os.path.isdir(version_path):
                test_path = os.path.join(version_path, filename_only)
                if os.path.exists(test_path):
                    filepath = test_path
                    doc_version = version_dir
                    break
    
    # 4. 旧版文档中心
    if not filepath:
        docs_center_dir = os.path.join(VERSION_DOCS_DIR, 'docs')
        test_path = os.path.join(docs_center_dir, filename_only)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = "current"
    
    # 5. 旧版本子目录
    if not filepath and os.path.exists(VERSION_DOCS_DIR):
        for version_dir in os.listdir(VERSION_DOCS_DIR):
            if version_dir == 'docs':
                continue
            version_path = os.path.join(VERSION_DOCS_DIR, version_dir)
            if os.path.isdir(version_path) and version_dir.startswith('v'):
                test_path = os.path.join(version_path, filename_only)
                if os.path.exists(test_path):
                    filepath = test_path
                    doc_version = version_dir
                    break
    
    if not filepath:
        filepath = os.path.join(DOCS_DIR, filename_only)
    
    mtime = ""
    version = "1.0.0"
    locked = False
    
    # 从版本记录文件读取
    version_data = {}
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
    
    # 使用文件名+版本作为key - 需要用filename_only
    doc_key = f"{doc_version}/{filename_only}" if doc_version else filename_only
    
    if doc_key in version_data:
        # 获取版本号
        major = version_data[doc_key].get('major', 1)
        minor = version_data[doc_key].get('minor', 0)
        patch = version_data[doc_key].get('patch', 0)
        version = f"{major}.{minor}.{patch}"
        
        # 获取更新时间
        mtime = version_data[doc_key].get('last_update', '')
        
        # 获取锁定状态
        locked = version_data[doc_key].get('locked', False)
    else:
        # 尝试其他可能的key格式
        found = False
        for key in version_data.keys():
            if key.endswith(f"/{filename_only}") or key == filename_only:
                vd = version_data[key]
                major = vd.get('major', 1)
                minor = vd.get('minor', 0)
                patch = vd.get('patch', 0)
                version = f"{major}.{minor}.{patch}"
                mtime = vd.get('last_update', '')
                locked = vd.get('locked', False)
                found = True
                break
        
        if not found:
            # 新文档，初始化版本
            version_data[doc_key] = {'major': 1, 'minor': 0, 'patch': 0, 'history': [], 'locked': False}
            with open(VERSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, ensure_ascii=False, indent=2)
    
    # 如果数据库没有时间，使用文件修改时间
    if not mtime and os.path.exists(filepath):
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filepath)))
    
    version_files = get_version_files()
    return render_template_string(SYS_TPL, versions=list(VERSIONS.values()), docs=docs,
                                 current_doc=filename, doc_content=content, 
                                 doc_mtime=mtime, doc_version=version, doc_locked=locked,
                                 version_files=version_files)

# ========== 旧路由兼容 ==========
@app.route('/dev')
def dev_page():
    """旧路由，重定向到系统管理"""
    return '<script>location.href="/sys"</script>'

@app.route('/wiki/<path:filename>')
def wiki_view(filename):
    """Wiki文档预览"""
    if not filename.endswith('.md'):
        return "不支持的文件类型", 400
    content = get_doc(filename)
    if content is None:
        return "文档不存在", 404
    
    # 提取版本和时间
    import re
    version = "1"
    mtime = ""
    locked = False
    
    # 从文档内容中提取版本号（支持 v1 或 1.0.0 格式）
    match = re.search(r'\*文档版本: (v?\d+(?:\.\d+\.\d+)?)\*', content)
    if match:
        version = match.group(1)
        # 如果是纯数字，添加 v 前缀
        if not version.startswith('v'):
            version = 'v' + version
    
    # 从文档内容中提取时间（支持日期和时间两种格式）
    match = re.search(r'\*最后更新: (\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2})?)\*', content)
    if match:
        mtime = match.group(1)
    
    # 从文档内容中检测锁定状态
    if '*锁定状态: 锁定' in content or '*锁定状态:锁定' in content:
        locked = True
    
    return render_template_string(WIKI_VIEW_TPL, filename=filename, content=content, 
                                 version=version, mtime=mtime, locked=locked)

@app.route('/api/wiki/raw/<path:filename>')
def api_wiki_raw(filename):
    """获取文档原始内容（用于锁定比对）"""
    if not filename.endswith('.md'):
        return jsonify({'code': 400})
    content = get_doc(filename)
    if content is None:
        return jsonify({'code': 404})
    return jsonify({'code': 200, 'content': content})

@app.route('/api/wiki/meta/<path:filename>')
def api_wiki_meta(filename):
    """获取文档元数据（版本、时间、锁定状态）"""
    if not filename.endswith('.md'):
        return jsonify({'code': 400})
    
    import json
    import time
    
    # 如果filename包含版本前缀（如v2.4/PRD.md），提取出来
    version_prefix = None
    if '/' in filename:
        parts = filename.split('/')
        if len(parts) == 2 and parts[0].startswith('v'):
            version_prefix = parts[0]
            filename = parts[1]  # 只保留PRD.md
    
    # 查找文档位置 - 支持多个目录
    doc_version = None
    filepath = None
    mtime = ""
    version = "1.0.0"
    locked = False
    
    # 1. 如果有版本前缀，直接在对应版本目录查找
    if version_prefix:
        # 新版本历史目录
        test_path = os.path.join(VERSION_HISTORY_DIR, version_prefix, filename)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = version_prefix
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filepath)))
        else:
            # 旧版本目录
            test_path = os.path.join(VERSION_DOCS_DIR, version_prefix, filename)
            if os.path.exists(test_path):
                filepath = test_path
                doc_version = version_prefix
                mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filepath)))
    
    # 2. 新文档中心（如果没有指定版本前缀）
    if not filepath and not version_prefix:
        test_path = os.path.join(DOCS_CENTER_DIR, filename)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = "current"
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filepath)))
    
    # 3. 新版本历史目录（如果没有指定版本前缀）
    if not filepath and not version_prefix:
        for vdir in os.listdir(VERSION_HISTORY_DIR):
            vpath = os.path.join(VERSION_HISTORY_DIR, vdir)
            if os.path.isdir(vpath):
                test_path = os.path.join(vpath, filename)
                if os.path.exists(test_path):
                    filepath = test_path
                    doc_version = vdir
                    mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filepath)))
                    break
    
    # 4. 旧文档中心（兼容）
    if not filepath:
        docs_center_dir = os.path.join(VERSION_DOCS_DIR, 'docs')
        test_path = os.path.join(docs_center_dir, filename)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = "current"
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filepath)))
    
    # 5. 旧版本目录（兼容）
    if not filepath and not version_prefix:
        for version_dir in os.listdir(VERSION_DOCS_DIR):
            if version_dir == 'docs':
                continue
            version_path = os.path.join(VERSION_DOCS_DIR, version_dir)
            if os.path.isdir(version_path) and version_dir.startswith('v'):
                test_path = os.path.join(version_path, filename)
                if os.path.exists(test_path):
                    filepath = test_path
                    doc_version = version_dir
                    mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filepath)))
                    break
    
    if not filepath:
        return jsonify({'code': 404})
    
    # 读取版本数据
    version_data = {}
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
    
    # 构建key来查找 - 优先使用带版本的key
    if doc_version:
        search_keys = [f"{doc_version}/{filename}", filename]
    else:
        search_keys = [filename, f"current/{filename}"]
    
    found_key = None
    for key in search_keys:
        if key in version_data:
            found_key = key
            break
    
    # 如果还没找到，遍历所有key模糊匹配
    if not found_key:
        for key in version_data.keys():
            if key.endswith(f"/{filename}") or key == filename:
                found_key = key
                break
    
    if found_key:
        vd = version_data[found_key]
        version = f"{vd.get('major',1)}.{vd.get('minor',0)}.{vd.get('patch',0)}"
        mtime = vd.get('last_update', mtime)
        locked = vd.get('locked', False)
    
    return jsonify({
        'code': 200,
        'version': version,
        'mtime': mtime,
        'locked': locked
    })

@app.route('/wiki/<path:filename>/edit')
def wiki_edit(filename):
    """Wiki文档编辑"""
    if not filename.endswith('.md'):
        return "不支持的文件类型", 400
    content = get_doc(filename)
    if content is None:
        return "文档不存在", 404
    
    # 获取版本和时间
    import re
    version = "1"
    mtime = ""
    locked = False
    
    # 从文档内容中提取版本号（支持 v1 或 1.0.0 格式）
    match = re.search(r'\*文档版本: (v?\d+(?:\.\d+\.\d+)?)\*', content)
    if match:
        version = match.group(1)
        # 如果是纯数字，添加 v 前缀
        if not version.startswith('v'):
            version = 'v' + version
    
    # 从文档内容中提取时间（支持日期和时间两种格式）
    match = re.search(r'\*最后更新: (\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2})?)\*', content)
    if match:
        mtime = match.group(1)
    
    # 从文档内容中检测锁定状态
    if '*锁定状态: 锁定' in content or '*锁定状态:锁定' in content:
        locked = True
    
    return render_template_string(WIKI_EDIT_TPL, filename=filename, content=content, 
                                 version=version, mtime=mtime, locked=locked)

@app.route('/api/wiki/<path:filename>', methods=['POST'])
def api_wiki_save(filename):
    """Wiki文档保存API"""
    if not filename.endswith('.md'):
        return jsonify({'code': 400, 'msg': '不支持的文件类型'})
    
    content = request.json.get('content', '')
    locked = request.json.get('locked', False)
    version_dir = request.json.get('version', None)
    
    # 查找文档路径和版本
    docs_center_dir = os.path.join(VERSION_DOCS_DIR, 'docs')
    doc_version = None
    filepath = None
    
    # 1. 指定版本目录
    if version_dir:
        version_path = os.path.join(VERSION_DOCS_DIR, version_dir)
        if os.path.isdir(version_path):
            test_path = os.path.join(version_path, filename)
            if os.path.exists(test_path):
                filepath = test_path
                doc_version = version_dir
    
    # 2. 文档中心
    if not filepath:
        test_path = os.path.join(docs_center_dir, filename)
        if os.path.exists(test_path):
            filepath = test_path
            doc_version = 'current'
    
    # 3. 版本子目录
    if not filepath and os.path.exists(VERSION_DOCS_DIR):
        for vdir in os.listdir(VERSION_DOCS_DIR):
            if vdir in ['docs', version_dir]:
                continue
            vpath = os.path.join(VERSION_DOCS_DIR, vdir)
            if os.path.isdir(vpath) and vdir.startswith('v'):
                test_path = os.path.join(vpath, filename)
                if os.path.exists(test_path):
                    filepath = test_path
                    doc_version = vdir
                    break
    
    # 4. 旧目录
    if not filepath:
        filepath = os.path.join(DOCS_DIR, filename)
    
    # 锁定检查 - 从数据库检查，而不是从文件内容
    import json
    if filepath and os.path.exists(filepath):
        version_data = {}
        if os.path.exists(VERSION_FILE):
            try:
                with open(VERSION_FILE, 'r') as f:
                    version_data = json.load(f)
            except:
                pass
        
        doc_key = f"{doc_version}/{filename}" if doc_version else filename
        
        # 检查数据库中的锁定状态
        old_locked = False
        if doc_key in version_data:
            old_locked = version_data[doc_key].get('locked', False)
        
        # 如果文档原本锁定，检查是否删减了内容
        if old_locked:
            try:
                with open(filepath, 'r') as f:
                    old_content = f.read()
            except:
                old_content = ""
            
            if len(content) < len(old_content) - 50:
                return jsonify({'code': 403, 'msg': '此文档为锁定文档，内容只能添加不能删减！'})
    
    try:
        save_doc(filename, content, locked, version_dir)
        return jsonify({'code': 200, 'msg': '保存成功'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})

@app.route('/api/wiki/list')
def api_wiki_list():
    """Wiki文档列表API"""
    docs = list_docs()
    return jsonify({'code': 200, 'data': docs})

# ========== 版本文档管理 ==========
VERSIONS_FILE = "/home/zhang/news_system/data/versions.json"

def load_versions_from_file():
    """从文件加载版本数据"""
    if os.path.exists(VERSIONS_FILE):
        try:
            with open(VERSIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None

def save_versions_to_file(versions):
    """保存版本数据到文件"""
    try:
        with open(VERSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存版本数据失败: {e}")
        return False

@app.route('/api/version/<version_id>/<doc_type>', methods=['POST'])
def api_version_doc_save(version_id, doc_type):
    """保存版本文档API"""
    if version_id not in VERSIONS:
        return jsonify({'code': 404, 'msg': '版本不存在'})
    
    doc_map = {'update_intro': '更新介绍', 'features': '功能介绍', 'bug_fix': 'BUG修复'}
    if doc_type not in doc_map:
        return jsonify({'code': 404, 'msg': '文档类型不存在'})
    
    content = request.json.get('content', '')
    
    # 更新内存中的数据
    VERSIONS[version_id][doc_type] = content
    
    # 保存到文件
    save_versions_to_file(VERSIONS)
    
    return jsonify({'code': 200, 'msg': '保存成功'})

# 尝试从文件加载版本数据
saved_versions = load_versions_from_file()
if saved_versions:
    VERSIONS.update(saved_versions)

# ========== V2.5 新增：统一版本管理API ==========

@app.route('/api/v2/versions')
def api_v2_versions():
    """
    V2.5新版：获取版本列表（使用统一版本管理函数）
    
    Response:
    {
        "code": 200,
        "data": [
            {"version": "v2.5.0", "path": "版本管理/v2.5.0", "docs": [...]},
            {"version": "v2.4.0", "path": "版本管理/v2.4.0", "docs": [...]}
        ]
    }
    """
    try:
        versions = get_sorted_versions(VERSION_MANAGE_DIR)
        
        data = []
        for v in versions:
            docs = scan_version_docs(v, VERSION_MANAGE_DIR)
            data.append({
                'version': v,
                'path': f'版本管理/{v}',
                'docs': docs
            })
        
        return jsonify({'code': 200, 'data': data})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})

@app.route('/api/v2/wiki/read/<path:filepath>')
def api_v2_wiki_read(filepath):
    """
    V2.5新版：读取文档内容和版本信息
    
    Response:
    {
        "code": 200,
        "content": "# 文档内容...",
        "version": "1.0.5",
        "mtime": "2026-03-06 14:30:00",
        "locked": false
    }
    """
    # 验证路径
    is_valid, error_msg = validate_doc_path(filepath)
    if not is_valid:
        return jsonify({'code': 400, 'msg': error_msg}), 400
    
    # 构建完整路径
    base_dir = '/home/zhang/news_system'
    full_path = os.path.join(base_dir, filepath)
    
    if not os.path.exists(full_path):
        return jsonify({'code': 404, 'msg': '文件不存在'}), 404
    
    try:
        # 读取内容
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 获取版本信息
        version_info = get_doc_version(filepath, base_dir)
        
        return jsonify({
            'code': 200,
            'content': content,
            'version': version_info['version'],
            'mtime': version_info['mtime'],
            'locked': version_info['locked']
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)}), 500

@app.route('/api/v2/wiki/save', methods=['POST'])
def api_v2_wiki_save():
    """
    V2.5新版：保存文档并更新版本
    
    Body:
    {
        "filepath": "版本管理/v2.5.0/02-需求.md",
        "content": "# 更新后的内容...",
        "locked": false
    }
    
    Response:
    {
        "code": 200,
        "version": "1.0.6",
        "msg": "保存成功"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'code': 400, 'msg': '请求体为空'}), 400
    
    filepath = data.get('filepath')
    content = data.get('content')
    locked = data.get('locked')
    
    if not filepath or content is None:
        return jsonify({'code': 400, 'msg': '缺少filepath或content'}), 400
    
    # 验证路径
    is_valid, error_msg = validate_doc_path(filepath)
    if not is_valid:
        return jsonify({'code': 400, 'msg': error_msg}), 400
    
    # 保存文档
    base_dir = '/home/zhang/news_system'
    result = save_doc_with_version(filepath, content, base_dir, locked)
    
    return jsonify(result)

# ========== 启动服务 ==========

if __name__ == "__main__":
    print("="*50)
    print("Web服务 v2.5 启动!")
    print("新闻: http://localhost:5000")
    print("Skills: http://localhost:5000/skills")
    print("订阅: http://localhost:5000/subscribe")
    print("系统管理: http://localhost:5000/sys")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
