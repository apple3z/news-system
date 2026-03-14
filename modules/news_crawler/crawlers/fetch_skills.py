#!/usr/bin/env python3
"""
Skills 采集脚本 v2.6.2
- 从 clawhub.ai 获取工具信息
- 从 GitHub API 获取 stars/description/topics 等元数据
- 从 GitHub 获取 README 内容
- UPSERT 模式：已存在则更新，不存在则插入（按 name+owner 去重）
"""

import sqlite3
import requests
import os
import time
from datetime import datetime as dt

# 数据库路径
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)
SKILLS_DB = os.path.join(data_dir, 'skills.db')

# 功能关键词映射
FEATURE_KEYWORDS = {
    'browser': 'Web Browser', 'web': 'Web', 'email': 'Email', 'file': 'File Management',
    'api': 'API', 'ai': 'AI', 'code': 'Code', 'data': 'Data', 'schedule': 'Scheduling',
    'news': 'News', 'pdf': 'PDF', 'pptx': 'PPT', 'dingtalk': 'DingTalk',
    'mcp': 'MCP', 'github': 'GitHub'
}

# 分类体系
CATEGORY_KEYWORDS = {
    'Text Generation': ['gpt', 'writing', 'text', 'chat', 'llm', 'language model'],
    'Image Processing': ['image', 'picture', 'drawing', 'diffusion', 'stable'],
    'Audio Processing': ['audio', 'speech', 'music', 'sound', 'tts'],
    'Video Processing': ['video', 'editing', 'stream'],
    'Code Assistant': ['code', 'programming', 'development', 'debug', 'review', 'editor', 'ide'],
    'GitHub': ['github', 'repository', 'release', 'issue', 'pull request'],
    'MCP': ['mcp', 'protocol', 'server'],
    'Automation': ['automation', 'auto', 'script', 'workflow', 'cron', 'schedule'],
    'Document Processing': ['pdf', 'word', 'excel', 'document', 'office', 'pptx', 'docx', 'xlsx'],
    'Communication': ['dingtalk', 'email', 'message', 'notification'],
    'Data Analysis': ['data', 'analysis', 'visualization', 'chart', 'statistics'],
    'Web Scraping': ['spider', 'crawl', 'fetch', 'scrape'],
    'Web Tools': ['browser', 'web', 'website', 'http'],
    'AI Tools': ['ai', 'artificial intelligence', 'machine learning', 'neural']
}

# Skills 列表（clawhub_owner, clawhub_name, github_owner, github_repo）
# 共 50 个，覆盖 AI/代码/文档/数据/自动化/Web/DevOps 等领域
SKILL_LIST = [
    # === 原有 10 个 ===
    ('lamelas', 'himalaya', 'soywod', 'himalaya'),
    ('cursor', 'cursor', 'getcursor', 'cursor'),
    ('pptx', 'pptx', 'scanny', 'python-pptx'),
    ('pdf', 'pdf', 'py-pdf', 'fpdf2'),
    ('docx', 'docx', 'python-openxml', 'python-docx'),
    ('xlsx', 'xlsx', 'openpyxl', 'openpyxl'),
    ('news', 'news', 'codelucas', 'newspaper'),
    ('cron', 'cron', 'aptible', 'supercronic'),
    ('mcp', 'mcp', 'modelcontextprotocol', 'servers'),
    ('github', 'github', 'cli', 'cli'),

    # === AI & LLM 工具 (10个) ===
    ('langchain', 'langchain', 'langchain-ai', 'langchain'),
    ('llama-index', 'llama-index', 'run-llama', 'llama_index'),
    ('openai', 'openai-python', 'openai', 'openai-python'),
    ('huggingface', 'transformers', 'huggingface', 'transformers'),
    ('ollama', 'ollama', 'ollama', 'ollama'),
    ('anthropic', 'anthropic-sdk', 'anthropics', 'anthropic-sdk-python'),
    ('dify', 'dify', 'langgenius', 'dify'),
    ('autogpt', 'autogpt', 'Significant-Gravitas', 'AutoGPT'),
    ('chatgpt', 'chatgpt-next-web', 'ChatGPTNextWeb', 'ChatGPT-Next-Web'),
    ('open-webui', 'open-webui', 'open-webui', 'open-webui'),

    # === 代码 & 开发工具 (10个) ===
    ('vscode', 'vscode', 'microsoft', 'vscode'),
    ('prettier', 'prettier', 'prettier', 'prettier'),
    ('eslint', 'eslint', 'eslint', 'eslint'),
    ('webpack', 'webpack', 'webpack', 'webpack'),
    ('vite', 'vite', 'vitejs', 'vite'),
    ('docker', 'docker-cli', 'docker', 'cli'),
    ('playwright', 'playwright', 'microsoft', 'playwright'),
    ('selenium', 'selenium', 'SeleniumHQ', 'selenium'),
    ('jest', 'jest', 'jestjs', 'jest'),
    ('copilot', 'copilot-cli', 'github', 'copilot.vim'),

    # === 数据 & 爬虫 (10个) ===
    ('scrapy', 'scrapy', 'scrapy', 'scrapy'),
    ('pandas', 'pandas', 'pandas-dev', 'pandas'),
    ('requests', 'requests', 'psf', 'requests'),
    ('httpx', 'httpx', 'encode', 'httpx'),
    ('beautifulsoup', 'beautifulsoup', 'waylan', 'beautifulsoup'),
    ('fastapi', 'fastapi', 'fastapi', 'fastapi'),
    ('flask', 'flask', 'pallets', 'flask'),
    ('redis', 'redis-py', 'redis', 'redis-py'),
    ('sqlite', 'sqlite-utils', 'simonw', 'sqlite-utils'),
    ('aiohttp', 'aiohttp', 'aio-libs', 'aiohttp'),

    # === 自动化 & DevOps (10个) ===
    ('ansible', 'ansible', 'ansible', 'ansible'),
    ('terraform', 'terraform', 'hashicorp', 'terraform'),
    ('k8s', 'kubectl', 'kubernetes', 'kubectl'),
    ('nginx', 'nginx-proxy', 'nginx-proxy', 'nginx-proxy'),
    ('prometheus', 'prometheus', 'prometheus', 'prometheus'),
    ('grafana', 'grafana', 'grafana', 'grafana'),
    ('celery', 'celery', 'celery', 'celery'),
    ('airflow', 'airflow', 'apache', 'airflow'),
    ('n8n', 'n8n', 'n8n-io', 'n8n'),
    ('puppeteer', 'puppeteer', 'puppeteer', 'puppeteer'),
]


def classify_skill(text, _features=''):
    """Classify skill based on text content."""
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score
    if scores:
        best_cat = max(scores, key=scores.get)
        if scores[best_cat] >= 1:
            return best_cat
    return 'Other'


def fetch_url(url, timeout=15):
    """Fetch URL content with timeout. Returns content or empty string."""
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=timeout)
        if r.status_code == 200:
            return r.text
        return ''
    except Exception:
        return ''


def fetch_github_meta(owner, repo):
    """Fetch metadata from GitHub API with retry."""
    for attempt in range(2):
        try:
            r = requests.get(
                f'https://api.github.com/repos/{owner}/{repo}',
                headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github.v3+json'},
                timeout=15
            )
            if r.status_code == 200:
                data = r.json()
                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'description': data.get('description', '') or '',
                    'language': data.get('language', '') or '',
                    'topics': data.get('topics', []),
                    'homepage': data.get('homepage', '') or '',
                    'license': (data.get('license') or {}).get('spdx_id', ''),
                    'default_branch': data.get('default_branch', 'main'),
                }
            elif r.status_code == 403:
                print(f'  [WARN] GitHub API rate limited, waiting 5s...')
                time.sleep(5)
                continue
            else:
                print(f'  [WARN] GitHub API returned {r.status_code} for {owner}/{repo}')
                return None
        except Exception as e:
            print(f'  [WARN] GitHub API error for {owner}/{repo}: {e}')
            if attempt == 0:
                time.sleep(2)
    return None


def fetch_readme(gh_owner, gh_repo, default_branch='main'):
    """Fetch README from GitHub, trying default branch then fallback."""
    branches = [default_branch]
    if default_branch != 'master':
        branches.append('master')
    if default_branch != 'main':
        branches.append('main')

    for branch in branches:
        content = fetch_url(
            f'https://raw.githubusercontent.com/{gh_owner}/{gh_repo}/{branch}/README.md',
            timeout=10
        )
        if content and '404' not in content[:20]:
            return content

    return ''


def build_chinese_intro(name, gh_desc, features, level, stars):
    """Generate a meaningful chinese intro from available data."""
    parts = [f'{name}']
    if gh_desc:
        parts.append(f' - {gh_desc}')

    info = []
    if stars and stars > 0:
        if stars >= 10000:
            info.append(f'{stars // 1000}k+ stars')
        elif stars >= 1000:
            info.append(f'{stars / 1000:.1f}k stars')
        else:
            info.append(f'{stars} stars')

    if level:
        info.append(level)

    if features:
        feature_list = [f.strip() for f in features.split(',')[:5]]
        info.append(', '.join(feature_list))

    if info:
        parts.append(f' ({"; ".join(info)})')

    return ''.join(parts)


def deduplicate_skills(conn):
    """Remove duplicate skills, keeping the one with higher ID (newer data)."""
    c = conn.cursor()
    c.execute("""
        DELETE FROM skills WHERE id NOT IN (
            SELECT MAX(id) FROM skills GROUP BY name, owner
        )
    """)
    deleted = c.rowcount
    if deleted > 0:
        print(f'[DEDUP] Removed {deleted} duplicate records')
    conn.commit()
    return deleted


def _needs_github_api(conn, name, owner, max_age_days=7):
    """Check if a skill needs GitHub API refresh.
    Returns True if: no record, no stars, no readme, or data older than max_age_days.
    """
    row = conn.execute(
        'SELECT stars, readme_content, updated_at FROM skills WHERE name = ? AND owner = ?',
        (name, owner)
    ).fetchone()
    if not row:
        return True  # new skill, needs full fetch
    stars, readme, updated_at = row
    if not stars or stars == 0:
        return True  # missing stars
    if not readme:
        return True  # missing readme
    if updated_at:
        try:
            last = dt.strptime(updated_at, '%Y-%m-%d')
            if (dt.now() - last).days >= max_age_days:
                return True  # stale data
        except ValueError:
            pass
    return False


def fetch_skills(batch_size=15):
    """Main entry: incremental fetch — only crawl skills that need updating.

    Args:
        batch_size: Max number of GitHub API calls per run (default 15, safe for 60/hr limit).
    """
    conn = sqlite3.connect(SKILLS_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, owner TEXT, title TEXT,
        description TEXT, source TEXT, url TEXT, download_url TEXT, github_url TEXT,
        category TEXT, tags TEXT, features TEXT, capabilities TEXT, skill_level TEXT,
        implementation TEXT, tech_stack TEXT, languages TEXT, frameworks TEXT,
        use_cases TEXT, scenarios TEXT, chinese_intro TEXT, readme_content TEXT,
        stars INTEGER, downloads INTEGER, created_at TEXT, updated_at TEXT
    )""")

    # Add updated_at column if missing (for existing databases)
    try:
        conn.execute("ALTER TABLE skills ADD COLUMN updated_at TEXT")
        conn.commit()
        print('[DB] Added updated_at column')
    except Exception:
        pass  # column already exists

    # Step 0: deduplicate existing data
    deduplicate_skills(conn)

    # Step 1: Separate skills into "needs API" vs "skip" groups
    needs_api = []
    skip_list = []
    for item in SKILL_LIST:
        clawhub_owner, clawhub_name, gh_owner, gh_repo = item
        if _needs_github_api(conn, clawhub_name, clawhub_owner):
            needs_api.append(item)
        else:
            skip_list.append(item)

    print(f'[PLAN] Total: {len(SKILL_LIST)}, Need API: {len(needs_api)}, Skip: {len(skip_list)}')

    # Step 2: Limit to batch_size for API calls
    api_batch = needs_api[:batch_size]
    deferred = needs_api[batch_size:]
    if deferred:
        print(f'[PLAN] Batch size={batch_size}, deferred {len(deferred)} skills to next run')

    # Step 3: Process skills that need no API (just ensure DB record exists)
    for clawhub_owner, clawhub_name, gh_owner, gh_repo in skip_list:
        existing = conn.execute(
            'SELECT id FROM skills WHERE name = ? AND owner = ?',
            (clawhub_name, clawhub_owner)
        ).fetchone()
        if not existing:
            # Insert minimal record (shouldn't happen since skip means record exists)
            _insert_minimal(conn, clawhub_owner, clawhub_name, gh_owner, gh_repo)
        # else: already complete, skip entirely

    new_count = 0
    updated_count = 0
    skipped_count = len(skip_list)
    errors = []
    api_calls = 0

    # Step 4: Process the API batch (incremental)
    for clawhub_owner, clawhub_name, gh_owner, gh_repo in api_batch:
        print(f'[FETCH] {clawhub_owner}/{clawhub_name} (github: {gh_owner}/{gh_repo})')

        try:
            # 1. Fetch GitHub API metadata
            gh_meta = fetch_github_meta(gh_owner, gh_repo)
            api_calls += 1

            stars = 0
            gh_desc = ''
            gh_lang = ''
            gh_topics = []
            default_branch = 'main'

            if gh_meta:
                stars = gh_meta.get('stars', 0)
                gh_desc = gh_meta.get('description', '')
                gh_lang = gh_meta.get('language', '')
                gh_topics = gh_meta.get('topics', [])
                default_branch = gh_meta.get('default_branch', 'main')
                print(f'  [GitHub] stars={stars}, lang={gh_lang}, topics={gh_topics[:5]}')
            else:
                print(f'  [WARN] GitHub API failed, using defaults')

            # 2. Fetch README (only if GitHub meta succeeded, to save API budget)
            readme = ''
            if gh_meta:
                readme = fetch_readme(gh_owner, gh_repo, default_branch)
                api_calls += 1
                if readme:
                    readme = readme[:8000]
                    print(f'  [README] {len(readme)} chars')
                else:
                    print(f'  [README] Not found')
            else:
                print(f'  [README] Skipped (no GitHub meta)')

            # 3. Extract features from README + description
            combined_text = f'{gh_desc} {readme}'.lower()
            features = [label for kw, label in FEATURE_KEYWORDS.items() if kw in combined_text]
            feature_str = ', '.join(features) if features else 'General Purpose'

            # 4. Determine skill level
            if len(features) >= 5:
                level = 'Full-Stack'
            elif len(features) >= 3:
                level = 'Multi-Function'
            else:
                level = 'Specialized'

            # 5. Build tags / tech_stack / languages
            tags = ', '.join(gh_topics[:10]) if gh_topics else ''
            tech_stack = gh_lang if gh_lang else ''
            languages = gh_lang if gh_lang else ''

            # 6. Build chinese intro
            intro = build_chinese_intro(clawhub_name, gh_desc, feature_str, level, stars)

            # 7. Classify
            category = classify_skill(f'{gh_desc} {readme} {feature_str}', feature_str)

            # 8. URLs
            github_url = f'https://github.com/{gh_owner}/{gh_repo}'
            clawhub_url = f'https://clawhub.ai/skill/{clawhub_owner}/{clawhub_name}'
            download_url = f'https://github.com/{gh_owner}/{gh_repo}/zipball'
            now = dt.now().strftime('%Y-%m-%d')

            # 9. Upsert (by name + owner)
            existing = conn.execute(
                'SELECT id, stars, tags, languages, tech_stack, readme_content, description '
                'FROM skills WHERE name = ? AND owner = ?',
                (clawhub_name, clawhub_owner)
            ).fetchone()

            if existing:
                # Preserve existing data when GitHub API fails
                db_stars = existing[1] or 0
                db_tags = existing[2] or ''
                db_lang = existing[3] or ''
                db_tech = existing[4] or ''
                db_readme = existing[5] or ''
                db_desc = existing[6] or ''

                final_stars = stars if stars > 0 else db_stars
                final_tags = tags if tags else db_tags
                final_lang = languages if languages else db_lang
                final_tech = tech_stack if tech_stack else db_tech
                final_readme = readme if readme else db_readme
                final_desc = gh_desc if gh_desc else db_desc

                final_intro = build_chinese_intro(clawhub_name, final_desc, feature_str, level, final_stars)

                conn.execute("""UPDATE skills SET
                    title=?, description=?, category=?, features=?, capabilities=?,
                    skill_level=?, chinese_intro=?, readme_content=?,
                    stars=?, tags=?, languages=?, tech_stack=?,
                    url=?, download_url=?, github_url=?, updated_at=?
                    WHERE id=?""",
                    (clawhub_name, final_desc, category, feature_str, feature_str,
                     level, final_intro, final_readme,
                     final_stars, final_tags, final_lang, final_tech,
                     clawhub_url, download_url, github_url, now,
                     existing[0]))
                updated_count += 1
                print(f'  [UPDATE] stars={final_stars} cat={category}')
            else:
                conn.execute("""INSERT INTO skills
                    (name, owner, title, description, source, url, download_url, github_url,
                     category, tags, features, capabilities, skill_level,
                     chinese_intro, readme_content, stars, downloads, languages, tech_stack,
                     created_at, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (clawhub_name, clawhub_owner, clawhub_name, gh_desc,
                     'clawhub', clawhub_url, download_url, github_url,
                     category, tags, feature_str, feature_str, level,
                     intro, readme, stars, 0, languages, tech_stack,
                     now, now))
                new_count += 1
                print(f'  [NEW] stars={stars} cat={category}')

            conn.commit()

            # Rate limit: 1s delay between GitHub API calls
            time.sleep(1)

        except Exception as e:
            print(f'  [ERROR] {clawhub_name}: {e}')
            errors.append({'name': clawhub_name, 'error': str(e)})

    conn.close()

    summary = (f'Done: {new_count} new, {updated_count} updated, '
               f'{skipped_count} skipped (complete), {api_calls} API calls')
    if deferred:
        summary += f', {len(deferred)} deferred to next run'
    if errors:
        summary += f', {len(errors)} errors'
    print(f'\n{summary}')

    return {
        'total': len(SKILL_LIST),
        'new': new_count,
        'updated': updated_count,
        'skipped': skipped_count,
        'api_calls': api_calls,
        'deferred': len(deferred),
        'errors': errors
    }


def _insert_minimal(conn, clawhub_owner, clawhub_name, gh_owner, gh_repo):
    """Insert a minimal skill record (no API call)."""
    now = dt.now().strftime('%Y-%m-%d')
    github_url = f'https://github.com/{gh_owner}/{gh_repo}'
    clawhub_url = f'https://clawhub.ai/skill/{clawhub_owner}/{clawhub_name}'
    download_url = f'https://github.com/{gh_owner}/{gh_repo}/zipball'

    conn.execute("""INSERT INTO skills
        (name, owner, title, description, source, url, download_url, github_url,
         category, features, skill_level, chinese_intro,
         stars, downloads, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (clawhub_name, clawhub_owner, clawhub_name, '',
         'clawhub', clawhub_url, download_url, github_url,
         'Other', 'General Purpose', 'Specialized',
         clawhub_name, 0, 0, now, now))
    conn.commit()


if __name__ == '__main__':
    print('=' * 50)
    print('Skills Crawler v2.6.2')
    print('=' * 50)
    fetch_skills()
