"""
Subscribe data access layer.
All subscribe.db SQL operations extracted from routes/subscribe.py and routes/admin.py.
"""

import sqlite3
from datetime import datetime
from config import SUBSCRIBE_DB


def _get_conn():
    conn = sqlite3.connect(SUBSCRIBE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables():
    """Ensure subscription tables exist."""
    conn = _get_conn()
    conn.execute("""CREATE TABLE IF NOT EXISTS subscription (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        sub_type TEXT DEFAULT 'website',
        check_interval INTEGER DEFAULT 300,
        last_check TEXT,
        last_content TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS subscription_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_id INTEGER,
        sub_name TEXT,
        content TEXT,
        detected_at TEXT
    )""")
    conn.commit()
    conn.close()


def list_subscriptions(status='all'):
    """List subscriptions with optional status filter."""
    conn = _get_conn()
    c = conn.cursor()

    sql = "SELECT id, name, url, sub_type, check_interval, last_check, is_active, created_at FROM subscription"
    params = []

    if status == 'active':
        sql += " WHERE is_active = 1"
    elif status == 'inactive':
        sql += " WHERE is_active = 0"

    sql += " ORDER BY created_at DESC"
    c.execute(sql, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    active_count = sum(1 for r in rows if r.get('is_active') == 1)
    return {'data': rows, 'total': len(rows), 'active_count': active_count}


def get_subscription(sub_id):
    """Get a single subscription by ID."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM subscription WHERE id = ?", (sub_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_subscription(data):
    """Create a new subscription. Returns new ID."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        """INSERT INTO subscription (name, url, sub_type, check_interval, is_active, created_at)
           VALUES (?,?,?,?,1,?)""",
        (data.get('name', ''), data.get('url', ''),
         data.get('sub_type', 'website'), data.get('check_interval', 300),
         datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id


def update_subscription(sub_id, data):
    """Update an existing subscription. Returns True if found."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM subscription WHERE id = ?", (sub_id,))
    if not c.fetchone():
        conn.close()
        return False

    c.execute(
        """UPDATE subscription SET name=?, url=?, sub_type=?, check_interval=? WHERE id=?""",
        (data.get('name', ''), data.get('url', ''),
         data.get('sub_type', 'website'), data.get('check_interval', 300), sub_id)
    )
    conn.commit()
    conn.close()
    return True


def delete_subscription(sub_id):
    """Delete a subscription and its history."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM subscription WHERE id = ?", (sub_id,))
    c.execute("DELETE FROM subscription_history WHERE sub_id = ?", (sub_id,))
    conn.commit()
    conn.close()


def toggle_active(sub_id):
    """Toggle subscription active/inactive. Returns new status or None if not found."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT is_active FROM subscription WHERE id = ?", (sub_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None

    new_status = 0 if row['is_active'] == 1 else 1
    c.execute("UPDATE subscription SET is_active = ? WHERE id = ?", (new_status, sub_id))
    conn.commit()
    conn.close()
    return new_status


def get_history(sub_id, limit=50):
    """Get subscription update history."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, sub_name, content, detected_at FROM subscription_history "
        "WHERE sub_id = ? ORDER BY detected_at DESC LIMIT ?",
        (sub_id, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_subscription_simple(name, url, sub_type='website'):
    """Simple add subscription (public API)."""
    conn = sqlite3.connect(SUBSCRIBE_DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO subscription (name, url, sub_type, is_active) VALUES (?, ?, ?, ?)",
        (name, url, sub_type, 1)
    )
    conn.commit()
    sub_id = c.lastrowid
    conn.close()
    return sub_id


def delete_subscription_simple(sub_id):
    """Simple delete subscription (public API)."""
    conn = sqlite3.connect(SUBSCRIBE_DB)
    c = conn.cursor()
    c.execute("DELETE FROM subscription WHERE id = ?", (sub_id,))
    conn.commit()
    conn.close()


def get_all_subscriptions_simple():
    """Get all subscriptions for public listing."""
    conn = sqlite3.connect(SUBSCRIBE_DB)
    c = conn.cursor()
    c.execute("SELECT id, name, url, sub_type, is_active, created_at FROM subscription ORDER BY id")
    subs = c.fetchall()
    conn.close()
    return subs


def get_feed_content(page=1, per_page=20, source=''):
    """获取订阅内容列表（公开展示用，从 subscription_history 获取）"""
    conn = _get_conn()
    try:
        sql = '''SELECT h.id, h.sub_id, h.sub_name, h.content, h.detected_at,
                        s.url as source_url, s.sub_type
                 FROM subscription_history h
                 LEFT JOIN subscription s ON h.sub_id = s.id
                 WHERE 1=1'''
        count_sql = '''SELECT COUNT(*) FROM subscription_history h
                       LEFT JOIN subscription s ON h.sub_id = s.id
                       WHERE 1=1'''
        params = []
        if source:
            sql += ' AND h.sub_name = ?'
            count_sql += ' AND h.sub_name = ?'
            params.append(source)
        total = conn.execute(count_sql, params).fetchone()[0]
        sql += ' ORDER BY h.detected_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        rows = conn.execute(sql, params).fetchall()
        data = [dict(r) for r in rows]
        return {'data': data, 'total': total, 'page': page, 'per_page': per_page}
    finally:
        conn.close()


def get_active_sources():
    """获取活跃订阅源名称列表"""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT DISTINCT name FROM subscription WHERE is_active = 1 ORDER BY name"
        ).fetchall()
        return [r['name'] for r in rows]
    finally:
        conn.close()
