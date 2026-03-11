#!/usr/bin/env python3
import sqlite3, requests, os
from datetime import datetime as dt

# 使用统一的跨平台路径工具
from path_utils import SKILLS_DB, ensure_data_dir

# 确保数据目录存在
ensure_data_dir()

# 连接数据库
conn = sqlite3.connect(SKILLS_DB)

# 创建表（如果不存在）
conn.execute("""CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY, 
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
)""")
conn.commit()

F = {'browser': '网页', 'web': '网页', 'email': '邮件', 'file': '文件', 'api': 'API', 'ai': 'AI', 
     'code': '代码', 'data': '数据', 'schedule': '日程', 'news': '新闻', 'pdf': 'PDF', 
     'pptx': 'PPT', 'dingtalk': '钉钉', 'mcp': 'MCP', 'github': 'GitHub'}

# v2.6.0 新增分类体系
CATEGORY_KEYWORDS = {
    '文本生成': ['gpt', '写作', '文本', '文章', 'chat', 'llm', '语言模型'],
    '图像处理': ['图像', '图片', 'image', '绘图', '绘画', 'diffusion', 'stable'],
    '音频处理': ['音频', '语音', 'audio', 'speech', 'music', '声音', 'tts'],
    '视频处理': ['视频', 'video', '剪辑', '生成视频'],
    '代码助手': ['代码', 'code', '编程', '开发', 'debug', 'review'],
    'GitHub': ['github', '仓库', 'release', 'issue'],
    'MCP': ['mcp', '协议', 'server'],
    '自动化': ['自动化', 'auto', '脚本', 'workflow'],
    '文档处理': ['pdf', 'word', 'excel', '文档', 'office'],
    '日程管理': ['日程', '日历', 'calendar', '提醒', 'schedule'],
    '通讯工具': ['钉钉', '邮件', 'email', '通讯', 'message'],
    '数据分析': ['数据', '分析', '可视化', 'data', 'chart', '统计'],
    '爬虫工具': ['爬虫', '采集', 'spider', 'crawl', 'fetch']
}

def classify_skill(text):
    """智能 Skills 分类（v2.6.0）"""
    text_lower = text.lower()
    scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score
    
    if scores:
        # 返回得分最高的分类
        return max(scores, key=scores.get)
    
    return '其他工具'  # 默认分类

def g(url):
    try: return requests.get(url, headers={'User-Agent':'M'}, timeout=12).text
    except: return ""

L = [("lamelas","himalaya"),("cursor","cursor"),("pptx","pptx"),("pdf","pdf"),("docx","docx"),
     ("xlsx","xlsx"),("news","news"),("cron","cron"),("mcp","mcp"),("github","github")]

for o,n in L:
    h = g(f"https://clawhub.ai/skill/{o}/{n}")
    rd = g(f"https://raw.githubusercontent.com/{o}/{n}/main/SKILL.md") or g(f"https://raw.githubusercontent.com/{o}/{n}/master/README.md")
    t = (h+" "+rd).lower()
    fs = [cn for kw,cn in F.items() if kw in t]
    lv = "全能型" if len(fs)>=5 else "多功能" if len(fs)>=3 else "专业型"
    intro = f"「{n}」是{lv}工具"
    if fs: intro += f"，擅长{fs[0]}等"
    ft = ','.join(fs)
    
    # v2.6.0 自动分类
    category = classify_skill(h + " " + rd)
    
    # Just use one simpler table with essential fields only
    conn.execute("""INSERT INTO skills (name,owner,title,description,source,url,download_url,github_url,category,features,capabilities,skill_level,chinese_intro,readme_content,created_at) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (n, o, n, n[:50], 'clawhub', f"https://clawhub.ai/skill/{o}/{n}",
         f"https://github.com/{o}/{n}/zipball", f"https://github.com/{o}/{n}",
         category, ft, ft, lv, intro, rd[:3000], dt.now().strftime("%Y-%m-%d")))
    print(f"OK {o}/{n} - {category}")

conn.commit()
conn.close()
print("完成")
