"""
Skills data access layer.
All skills.db SQL operations extracted from routes/skills.py and routes/admin.py.
"""

import sqlite3
from datetime import datetime
from config import SKILLS_DB


def _get_conn():
    return sqlite3.connect(SKILLS_DB)


def _get_row_conn():
    conn = sqlite3.connect(SKILLS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def list_skills(keyword='', category=''):
    """List skills with optional keyword/category filter (admin view)."""
    conn = _get_row_conn()
    c = conn.cursor()

    sql = ("SELECT id, name, owner, title, description, category, url, github_url, "
           "skill_level, features, chinese_intro, stars, downloads, created_at "
           "FROM skills WHERE 1=1")
    params = []

    if keyword:
        sql += " AND (name LIKE ? OR description LIKE ? OR chinese_intro LIKE ?)"
        kw = '%' + keyword + '%'
        params.extend([kw, kw, kw])
    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY id DESC"
    c.execute(sql, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    return rows


def get_skill(skill_id):
    """Get a single skill by ID."""
    conn = _get_row_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM skills WHERE id = ?", (skill_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_skill(data):
    """Create a new skill. Returns new ID or None on error."""
    conn = _get_row_conn()
    try:
        c = conn.cursor()
        c.execute(
            """INSERT INTO skills (name, owner, title, description, category, url, github_url,
               download_url, skill_level, features, chinese_intro, stars, downloads, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data.get('name', ''), data.get('owner', ''), data.get('title', data.get('name', '')),
             data.get('description', ''), data.get('category', ''), data.get('url', ''),
             data.get('github_url', ''), data.get('download_url', ''),
             data.get('skill_level', ''), data.get('features', ''),
             data.get('chinese_intro', ''), data.get('stars', 0), data.get('downloads', 0),
             datetime.now().strftime('%Y-%m-%d'))
        )
        conn.commit()
        new_id = c.lastrowid
        return new_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_skill(skill_id, data):
    """Update an existing skill. Returns True if found, False otherwise."""
    conn = _get_row_conn()
    try:
        c = conn.cursor()
        c.execute("SELECT id FROM skills WHERE id = ?", (skill_id,))
        if not c.fetchone():
            return False

        c.execute(
            """UPDATE skills SET name=?, owner=?, title=?, description=?, category=?,
               url=?, github_url=?, download_url=?, skill_level=?, features=?, chinese_intro=?,
               stars=?, downloads=?
               WHERE id=?""",
            (data.get('name', ''), data.get('owner', ''), data.get('title', ''),
             data.get('description', ''), data.get('category', ''),
             data.get('url', ''), data.get('github_url', ''), data.get('download_url', ''),
             data.get('skill_level', ''), data.get('features', ''),
             data.get('chinese_intro', ''), data.get('stars', 0), data.get('downloads', 0),
             skill_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_skill(skill_id):
    """Delete a skill by ID."""
    conn = _get_conn()
    try:
        c = conn.cursor()
        c.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_categories():
    """Get distinct skill categories."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM skills WHERE category IS NOT NULL AND category != '' ORDER BY category")
    cats = [row[0] for row in c.fetchall()]
    conn.close()
    return cats


def search_skills_public(keyword=''):
    """Search skills for public API."""
    conn = _get_row_conn()
    c = conn.cursor()

    fields = ("id, name, owner, description, chinese_intro, category, "
              "stars, downloads, url, github_url, skill_level, features, created_at")

    if keyword:
        c.execute(
            f"SELECT {fields} FROM skills "
            "WHERE name LIKE ? OR description LIKE ? OR chinese_intro LIKE ? ORDER BY name",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
    else:
        c.execute(f"SELECT {fields} FROM skills ORDER BY category, name")

    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    for r in rows:
        r['stars'] = r.get('stars') or 0
        r['downloads'] = r.get('downloads') or 0

    return rows


def get_all_skills_simple():
    """Get all skills in simple format for listing page."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, description, category FROM skills ORDER BY category, name")
    skills = c.fetchall()
    conn.close()
    return skills


def get_daily_stats(days=30):
    """Get daily skill count statistics for the last N days."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT created_at AS day, COUNT(*) AS count
        FROM skills
        WHERE created_at >= date('now', '-' || ? || ' days')
        GROUP BY created_at
        ORDER BY created_at ASC
    """, (days,))
    rows = c.fetchall()
    conn.close()
    return [{'day': r[0], 'count': r[1]} for r in rows]


def get_skill_rankings(limit=20):
    """Get top skills ranked by stars."""
    conn = _get_row_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, name, owner, description, chinese_intro, category, stars, downloads "
        "FROM skills WHERE stars IS NOT NULL ORDER BY stars DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    for r in rows:
        r['stars'] = r.get('stars') or 0
        r['downloads'] = r.get('downloads') or 0
    return rows
