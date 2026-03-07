#!/usr/bin/env python3
import sqlite3, requests
from datetime import datetime as dt

DB = "/home/zhang/.copaw/news_system/data/skills.db"
conn = sqlite3.connect(DB)
conn.execute("""CREATE TABLE skills (id INTEGER PRIMARY KEY, name TEXT, owner TEXT, title TEXT,
    description TEXT, source TEXT, url TEXT, download_url TEXT, github_url TEXT, category TEXT,
    tags TEXT, features TEXT, capabilities TEXT, skill_level TEXT, implementation TEXT,
    tech_stack TEXT, languages TEXT, frameworks TEXT, use_cases TEXT, scenarios TEXT,
    chinese_intro TEXT, readme_content TEXT, stars INTEGER, downloads INTEGER, created_at TEXT)""")
conn.commit()

F = {'browser': '网页', 'web': '网页', 'email': '邮件', 'file': '文件', 'api': 'API', 'ai': 'AI', 
     'code': '代码', 'data': '数据', 'schedule': '日程', 'news': '新闻', 'pdf': 'PDF', 
     'pptx': 'PPT', 'dingtalk': '钉钉', 'mcp': 'MCP', 'github': 'GitHub'}

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
    
    # Just use one simpler table with essential fields only
    conn.execute("""INSERT INTO skills (name,owner,title,description,source,url,download_url,github_url,category,features,capabilities,skill_level,chinese_intro,readme_content,created_at) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (n, o, n, n[:50], 'clawhub', f"https://clawhub.ai/skill/{o}/{n}",
         f"https://github.com/{o}/{n}/zipball", f"https://github.com/{o}/{n}",
         '工具', ft, ft, lv, intro, rd[:3000], dt.now().strftime("%Y-%m-%d")))
    print(f"OK {o}/{n}")

conn.commit()
conn.close()
print("完成")
