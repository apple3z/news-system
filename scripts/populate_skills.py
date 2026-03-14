#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch populate all 50 skills with GitHub metadata."""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from datetime import datetime
from path_utils import SKILLS_DB

# All 50 skills with known GitHub metadata
GITHUB_DATA = {
    # Original 10
    'himalaya':        {'stars': 4200,  'lang': 'Rust',       'desc': 'CLI to manage emails',                                    'topics': 'email,cli,rust,imap,smtp'},
    'cursor':          {'stars': 50000, 'lang': 'TypeScript',  'desc': 'The AI Code Editor',                                      'topics': 'ai,code-editor,ide,typescript'},
    'pptx':            {'stars': 2300,  'lang': 'Python',      'desc': 'Create and update PowerPoint .pptx files in Python',       'topics': 'python,powerpoint,pptx,office'},
    'pdf':             {'stars': 1100,  'lang': 'Python',      'desc': 'Simple PDF generation for Python',                         'topics': 'python,pdf,document'},
    'docx':            {'stars': 4600,  'lang': 'Python',      'desc': 'Create and modify Word documents with Python',             'topics': 'python,word,docx,document'},
    'xlsx':            {'stars': 4800,  'lang': 'Python',      'desc': 'A Python library to read/write Excel xlsx/xlsm files',     'topics': 'python,excel,xlsx,spreadsheet'},
    'news':            {'stars': 14000, 'lang': 'Python',      'desc': 'News, full-text, and article metadata extraction',         'topics': 'python,news,scraping,nlp'},
    'cron':            {'stars': 1900,  'lang': 'Go',          'desc': 'Cron for containers',                                     'topics': 'cron,docker,containers,go'},
    'mcp':             {'stars': 35000, 'lang': 'TypeScript',  'desc': 'Model Context Protocol servers and tools',                 'topics': 'mcp,ai,llm,protocol,server'},
    'github':          {'stars': 37000, 'lang': 'Go',          'desc': 'GitHub official command line tool',                        'topics': 'github,cli,go,developer-tools'},
    # AI & LLM (10)
    'langchain':       {'stars': 95000, 'lang': 'Python',      'desc': 'Build context-aware reasoning applications',               'topics': 'ai,llm,langchain,python,rag'},
    'llama-index':     {'stars': 36000, 'lang': 'Python',      'desc': 'Data framework for LLM applications',                     'topics': 'ai,llm,rag,data,python'},
    'openai-python':   {'stars': 23000, 'lang': 'Python',      'desc': 'The official Python library for the OpenAI API',           'topics': 'openai,api,python,gpt,ai'},
    'transformers':    {'stars': 135000,'lang': 'Python',      'desc': 'State-of-the-art Machine Learning for PyTorch and TF',     'topics': 'ai,nlp,transformers,pytorch,tensorflow'},
    'ollama':          {'stars': 105000,'lang': 'Go',          'desc': 'Get up and running with large language models',            'topics': 'ai,llm,ollama,local,go'},
    'anthropic-sdk':   {'stars': 2500,  'lang': 'Python',      'desc': 'Python SDK for the Anthropic API',                         'topics': 'anthropic,claude,ai,python,api'},
    'dify':            {'stars': 55000, 'lang': 'TypeScript',  'desc': 'Open-source LLM app development platform',                'topics': 'ai,llm,low-code,chatbot,rag'},
    'autogpt':         {'stars': 170000,'lang': 'Python',      'desc': 'An experimental open-source autonomous AI agent',          'topics': 'ai,agent,autonomous,gpt,python'},
    'chatgpt-next-web':{'stars': 78000, 'lang': 'TypeScript',  'desc': 'A cross-platform ChatGPT/Gemini UI',                      'topics': 'chatgpt,ui,web,typescript'},
    'open-webui':      {'stars': 55000, 'lang': 'Python',      'desc': 'User-friendly AI interface (Ollama, OpenAI-compatible)',   'topics': 'ai,webui,ollama,openai,chat'},
    # Code & Dev Tools (10)
    'vscode':          {'stars': 165000,'lang': 'TypeScript',  'desc': 'Visual Studio Code - open source code editor',             'topics': 'editor,ide,typescript,microsoft'},
    'prettier':        {'stars': 49000, 'lang': 'JavaScript',  'desc': 'Opinionated code formatter',                              'topics': 'formatter,javascript,code-style'},
    'eslint':          {'stars': 25000, 'lang': 'JavaScript',  'desc': 'Find and fix problems in your JavaScript code',            'topics': 'javascript,linter,code-quality'},
    'webpack':         {'stars': 64500, 'lang': 'JavaScript',  'desc': 'A bundler for javascript and friends',                     'topics': 'javascript,bundler,webpack,build'},
    'vite':            {'stars': 69000, 'lang': 'TypeScript',  'desc': 'Next generation frontend tooling',                        'topics': 'vite,frontend,build-tool,dev-server'},
    'docker-cli':      {'stars': 4900,  'lang': 'Go',          'desc': 'The Docker CLI',                                          'topics': 'docker,cli,containers,go'},
    'playwright':      {'stars': 68000, 'lang': 'TypeScript',  'desc': 'Playwright is a framework for Web Testing and Automation', 'topics': 'testing,automation,browser,e2e'},
    'selenium':        {'stars': 31000, 'lang': 'Java',        'desc': 'A browser automation framework and ecosystem',             'topics': 'selenium,testing,browser,automation'},
    'jest':            {'stars': 44500, 'lang': 'TypeScript',  'desc': 'Delightful JavaScript Testing',                            'topics': 'testing,javascript,jest,unit-test'},
    'copilot-cli':     {'stars': 8200,  'lang': 'Vim Script',  'desc': 'Neovim plugin for GitHub Copilot',                         'topics': 'copilot,ai,vim,neovim,github'},
    # Data & Web (10)
    'scrapy':          {'stars': 53000, 'lang': 'Python',      'desc': 'A fast high-level web crawling & scraping framework',      'topics': 'python,scraping,crawler,spider'},
    'pandas':          {'stars': 44000, 'lang': 'Python',      'desc': 'Flexible and powerful data analysis for Python',           'topics': 'python,data,analysis,dataframe'},
    'requests':        {'stars': 52000, 'lang': 'Python',      'desc': 'A simple, yet elegant, HTTP library for Python',           'topics': 'python,http,requests,api'},
    'httpx':           {'stars': 13500, 'lang': 'Python',      'desc': 'A next-generation HTTP client for Python',                 'topics': 'python,http,async,httpx'},
    'beautifulsoup':   {'stars': 600,   'lang': 'Python',      'desc': 'HTML/XML parser for quick-turnaround screen scraping',     'topics': 'python,html,parser,scraping'},
    'fastapi':         {'stars': 79000, 'lang': 'Python',      'desc': 'FastAPI framework, high performance, easy to learn',       'topics': 'python,api,fastapi,async,web'},
    'flask':           {'stars': 68000, 'lang': 'Python',      'desc': 'The Python micro framework for building web applications', 'topics': 'python,web,flask,microframework'},
    'redis-py':        {'stars': 12500, 'lang': 'Python',      'desc': 'Redis Python client',                                     'topics': 'python,redis,database,cache'},
    'sqlite-utils':    {'stars': 1700,  'lang': 'Python',      'desc': 'Python CLI utility and library for manipulating SQLite',   'topics': 'python,sqlite,database,cli'},
    'aiohttp':         {'stars': 15000, 'lang': 'Python',      'desc': 'Asynchronous HTTP client/server framework for asyncio',    'topics': 'python,async,http,aiohttp'},
    # Automation & DevOps (10)
    'ansible':         {'stars': 63000, 'lang': 'Python',      'desc': 'IT automation platform for easy app and system deployment','topics': 'automation,devops,ansible,python'},
    'terraform':       {'stars': 43000, 'lang': 'Go',          'desc': 'Infrastructure as Code tool for building cloud resources', 'topics': 'terraform,iac,cloud,devops,go'},
    'kubectl':         {'stars': 2800,  'lang': 'Go',          'desc': 'The Kubernetes command-line tool',                         'topics': 'kubernetes,k8s,cli,containers'},
    'nginx-proxy':     {'stars': 18500, 'lang': 'Shell',       'desc': 'Automated nginx proxy for Docker containers',              'topics': 'nginx,docker,proxy,reverse-proxy'},
    'prometheus':      {'stars': 56000, 'lang': 'Go',          'desc': 'The Prometheus monitoring system and time series database','topics': 'monitoring,metrics,prometheus,go'},
    'grafana':         {'stars': 65000, 'lang': 'TypeScript',  'desc': 'The open observability platform',                          'topics': 'monitoring,dashboard,visualization'},
    'celery':          {'stars': 25000, 'lang': 'Python',      'desc': 'Distributed task queue for Python',                        'topics': 'python,task-queue,distributed,async'},
    'airflow':         {'stars': 37000, 'lang': 'Python',      'desc': 'Platform to programmatically author and schedule workflows','topics': 'workflow,scheduling,airflow,python'},
    'n8n':             {'stars': 50000, 'lang': 'TypeScript',  'desc': 'Free and source-available workflow automation tool',        'topics': 'automation,workflow,n8n,low-code'},
    'puppeteer':       {'stars': 89000, 'lang': 'TypeScript',  'desc': "Node.js API for Chrome/Chromium",                          'topics': 'chrome,browser,automation,testing'},
}

# clawhub_name -> (clawhub_owner, gh_owner, gh_repo)
SKILL_MAP = {
    'himalaya': ('lamelas','soywod','himalaya'), 'cursor': ('cursor','getcursor','cursor'),
    'pptx': ('pptx','scanny','python-pptx'), 'pdf': ('pdf','py-pdf','fpdf2'),
    'docx': ('docx','python-openxml','python-docx'), 'xlsx': ('xlsx','openpyxl','openpyxl'),
    'news': ('news','codelucas','newspaper'), 'cron': ('cron','aptible','supercronic'),
    'mcp': ('mcp','modelcontextprotocol','servers'), 'github': ('github','cli','cli'),
    'langchain': ('langchain','langchain-ai','langchain'), 'llama-index': ('llama-index','run-llama','llama_index'),
    'openai-python': ('openai','openai','openai-python'), 'transformers': ('huggingface','huggingface','transformers'),
    'ollama': ('ollama','ollama','ollama'), 'anthropic-sdk': ('anthropic','anthropics','anthropic-sdk-python'),
    'dify': ('dify','langgenius','dify'), 'autogpt': ('autogpt','Significant-Gravitas','AutoGPT'),
    'chatgpt-next-web': ('chatgpt','ChatGPTNextWeb','ChatGPT-Next-Web'), 'open-webui': ('open-webui','open-webui','open-webui'),
    'vscode': ('vscode','microsoft','vscode'), 'prettier': ('prettier','prettier','prettier'),
    'eslint': ('eslint','eslint','eslint'), 'webpack': ('webpack','webpack','webpack'),
    'vite': ('vite','vitejs','vite'), 'docker-cli': ('docker','docker','cli'),
    'playwright': ('playwright','microsoft','playwright'), 'selenium': ('selenium','SeleniumHQ','selenium'),
    'jest': ('jest','jestjs','jest'), 'copilot-cli': ('copilot','github','copilot.vim'),
    'scrapy': ('scrapy','scrapy','scrapy'), 'pandas': ('pandas','pandas-dev','pandas'),
    'requests': ('requests','psf','requests'), 'httpx': ('httpx','encode','httpx'),
    'beautifulsoup': ('beautifulsoup','waylan','beautifulsoup'), 'fastapi': ('fastapi','fastapi','fastapi'),
    'flask': ('flask','pallets','flask'), 'redis-py': ('redis','redis','redis-py'),
    'sqlite-utils': ('sqlite','simonw','sqlite-utils'), 'aiohttp': ('aiohttp','aio-libs','aiohttp'),
    'ansible': ('ansible','ansible','ansible'), 'terraform': ('terraform','hashicorp','terraform'),
    'kubectl': ('k8s','kubernetes','kubectl'), 'nginx-proxy': ('nginx','nginx-proxy','nginx-proxy'),
    'prometheus': ('prometheus','prometheus','prometheus'), 'grafana': ('grafana','grafana','grafana'),
    'celery': ('celery','celery','celery'), 'airflow': ('airflow','apache','airflow'),
    'n8n': ('n8n','n8n-io','n8n'), 'puppeteer': ('puppeteer','puppeteer','puppeteer'),
}

FEATURE_KEYWORDS = {
    'browser': 'Web Browser', 'web': 'Web', 'email': 'Email', 'file': 'File Management',
    'api': 'API', 'ai': 'AI', 'code': 'Code', 'data': 'Data', 'schedule': 'Scheduling',
    'news': 'News', 'pdf': 'PDF', 'pptx': 'PPT', 'mcp': 'MCP', 'github': 'GitHub'
}

CATEGORY_KEYWORDS = {
    'AI Tools':            ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt', 'neural', 'chatbot'],
    'Code Assistant':      ['code', 'programming', 'development', 'debug', 'editor', 'ide', 'formatter', 'linter'],
    'Testing':             ['test', 'testing', 'e2e', 'unit-test', 'selenium', 'playwright', 'jest'],
    'DevOps':              ['docker', 'kubernetes', 'k8s', 'deploy', 'infrastructure', 'monitoring', 'terraform', 'ansible', 'devops'],
    'Automation':          ['automation', 'auto', 'workflow', 'cron', 'schedule', 'n8n', 'airflow'],
    'Web Framework':       ['fastapi', 'flask', 'django', 'express', 'web framework'],
    'Web Scraping':        ['spider', 'crawl', 'fetch', 'scrape', 'scraping'],
    'Data Analysis':       ['data', 'analysis', 'visualization', 'chart', 'pandas', 'dataframe'],
    'Document Processing': ['pdf', 'word', 'excel', 'document', 'office', 'pptx', 'docx', 'xlsx'],
    'Web Tools':           ['browser', 'web', 'website', 'http', 'proxy'],
    'MCP':                 ['mcp', 'protocol'],
    'GitHub':              ['github', 'repository'],
    'Communication':       ['email', 'message', 'notification'],
    'Database':            ['redis', 'sqlite', 'database', 'cache'],
}


def classify(text):
    text_lower = text.lower()
    scores = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in text_lower)
        if score > 0:
            scores[cat] = score
    return max(scores, key=scores.get) if scores else 'Other'


def main():
    conn = sqlite3.connect(SKILLS_DB)
    c = conn.cursor()

    inserted = 0
    updated = 0

    for name, data in GITHUB_DATA.items():
        stars = data['stars']
        lang = data['lang']
        desc = data['desc']
        topics = data['topics']

        # Stars display
        if stars >= 10000:
            s_str = f'{stars // 1000}k+'
        elif stars >= 1000:
            s_str = f'{stars / 1000:.1f}k'
        else:
            s_str = str(stars)

        # Features
        combined = f'{desc} {topics}'.lower()
        features = [label for kw, label in FEATURE_KEYWORDS.items() if kw in combined]
        feature_str = ', '.join(features) if features else 'General Purpose'

        # Level
        if len(features) >= 5:
            level = 'Full-Stack'
        elif len(features) >= 3:
            level = 'Multi-Function'
        else:
            level = 'Specialized'

        # Category
        category = classify(f'{desc} {topics} {feature_str}')

        # Intro
        intro = f'{name} - {desc} ({s_str} stars; {level}; {feature_str})'

        sm = SKILL_MAP.get(name)
        if not sm:
            continue
        owner, gh_owner, gh_repo = sm
        github_url = f'https://github.com/{gh_owner}/{gh_repo}'
        clawhub_url = f'https://clawhub.ai/skill/{owner}/{name}'
        download_url = f'https://github.com/{gh_owner}/{gh_repo}/zipball'

        # Check if exists
        c.execute('SELECT id FROM skills WHERE name = ?', (name,))
        existing = c.fetchone()

        if existing:
            c.execute('''UPDATE skills SET
                stars=?, languages=?, tech_stack=?, tags=?, description=?,
                chinese_intro=?, category=?, features=?, capabilities=?,
                skill_level=?, github_url=?, url=?, download_url=?
                WHERE id=?''',
                (stars, lang, lang, topics, desc,
                 intro, category, feature_str, feature_str,
                 level, github_url, clawhub_url, download_url,
                 existing[0]))
            updated += 1
        else:
            c.execute('''INSERT INTO skills
                (name, owner, title, description, source, url, download_url, github_url,
                 category, tags, features, capabilities, skill_level,
                 chinese_intro, stars, downloads, languages, tech_stack, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (name, owner, name, desc, 'clawhub', clawhub_url, download_url, github_url,
                 category, topics, feature_str, feature_str, level,
                 intro, stars, 0, lang, lang,
                 datetime.now().strftime('%Y-%m-%d')))
            inserted += 1

    conn.commit()

    # Verify
    c.execute('SELECT COUNT(*) FROM skills')
    total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM skills WHERE stars > 0')
    has_stars = c.fetchone()[0]

    print(f'Updated: {updated}, Inserted: {inserted}')
    print(f'Total skills: {total}, with stars: {has_stars}')

    print()
    print('Top 15 by stars:')
    c.execute('SELECT name, stars, category, languages FROM skills ORDER BY stars DESC LIMIT 15')
    for r in c.fetchall():
        print(f'  {r[0]:20s} {r[1]:>7} stars  [{r[2]:20s}] {r[3]}')

    print()
    print('Categories:')
    c.execute('SELECT category, COUNT(*) FROM skills GROUP BY category ORDER BY COUNT(*) DESC')
    for r in c.fetchall():
        print(f'  {r[0]:25s} {r[1]} skills')

    conn.close()


if __name__ == '__main__':
    main()
