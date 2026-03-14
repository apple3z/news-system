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
        title TEXT,
        summary TEXT,
        content TEXT,
        link TEXT,
        pub_date TEXT,
        detected_at TEXT
    )""")
    # 兼容旧表：如果表已存在但缺少新字段，逐个添加
    for col in ['title', 'summary', 'link', 'pub_date', 'author', 'thumbnail']:
        try:
            conn.execute(f"ALTER TABLE subscription_history ADD COLUMN {col} TEXT")
        except Exception:
            pass  # 字段已存在，忽略
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


def get_feed_content(page=1, per_page=20, source='', keyword='', time_range='', sort_by='latest'):
    """获取订阅内容列表（公开展示用，从 subscription_history 获取）
    支持 keyword 搜索、time_range 时间筛选、sort_by 排序
    """
    conn = _get_conn()
    try:
        sql = '''SELECT h.id, h.sub_id, h.sub_name, h.title, h.summary, h.content, h.link, h.detected_at,
                        h.author, h.thumbnail, h.comments, h.pub_date,
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
        if keyword:
            sql += ' AND (h.title LIKE ? OR h.summary LIKE ? OR h.sub_name LIKE ?)'
            count_sql += ' AND (h.title LIKE ? OR h.summary LIKE ? OR h.sub_name LIKE ?)'
            kw = f'%{keyword}%'
            params.extend([kw, kw, kw])
        if time_range == 'today':
            sql += " AND date(h.detected_at) = date('now', 'localtime')"
            count_sql += " AND date(h.detected_at) = date('now', 'localtime')"
        elif time_range == 'week':
            sql += " AND h.detected_at >= datetime('now', '-7 days', 'localtime')"
            count_sql += " AND h.detected_at >= datetime('now', '-7 days', 'localtime')"
        elif time_range == 'month':
            sql += " AND h.detected_at >= datetime('now', '-30 days', 'localtime')"
            count_sql += " AND h.detected_at >= datetime('now', '-30 days', 'localtime')"
        total = conn.execute(count_sql, params).fetchone()[0]
        if sort_by == 'source':
            sql += ' ORDER BY h.sub_name ASC, h.detected_at DESC'
        else:
            sql += ' ORDER BY h.detected_at DESC'
        sql += ' LIMIT ? OFFSET ?'
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


def get_feed_detail(item_id):
    """获取单条订阅内容详情（增强版：含 parsed_content/thumbnail/author）"""
    conn = _get_conn()
    try:
        sql = '''SELECT h.id, h.sub_id, h.sub_name, h.title, h.summary, h.content, h.link,
                        h.pub_date, h.detected_at,
                        s.url as source_url, s.sub_type
                 FROM subscription_history h
                 LEFT JOIN subscription s ON h.sub_id = s.id
                 WHERE h.id = ?'''
        row = conn.execute(sql, (item_id,)).fetchone()
        if row:
            data = dict(row)
            data['parsed_content'] = _parse_content(data.get('content', ''))
            data['thumbnail'] = _extract_thumbnail(data.get('content', ''))
            data['author'] = _extract_author(data.get('content', ''))
            return data
        return None
    finally:
        conn.close()


def get_subscribe_stats():
    """获取订阅统计数据"""
    conn = _get_conn()
    try:
        total_feeds = conn.execute(
            "SELECT COUNT(*) FROM subscription_history"
        ).fetchone()[0]

        total_sources = conn.execute(
            "SELECT COUNT(*) FROM subscription"
        ).fetchone()[0]

        today_feeds = conn.execute(
            "SELECT COUNT(*) FROM subscription_history WHERE date(detected_at) = date('now', 'localtime')"
        ).fetchone()[0]

        this_week_feeds = conn.execute(
            "SELECT COUNT(*) FROM subscription_history WHERE detected_at >= datetime('now', '-7 days', 'localtime')"
        ).fetchone()[0]

        active_sources = conn.execute(
            """SELECT COUNT(DISTINCT s.id) FROM subscription s
               INNER JOIN subscription_history h ON s.id = h.sub_id
               WHERE h.detected_at >= datetime('now', '-7 days', 'localtime')
                 AND s.is_active = 1"""
        ).fetchone()[0]

        return {
            'total_feeds': total_feeds,
            'total_sources': total_sources,
            'today_feeds': today_feeds,
            'this_week_feeds': this_week_feeds,
            'active_sources': active_sources
        }
    finally:
        conn.close()


def get_subscriptions_with_count():
    """获取订阅源详情列表（含每个源的内容数量）"""
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT s.id, s.name, s.url, s.sub_type, s.is_active,
                   s.last_check, s.created_at,
                   COUNT(h.id) as feed_count
            FROM subscription s
            LEFT JOIN subscription_history h ON s.id = h.sub_id
            GROUP BY s.id
            ORDER BY feed_count DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def ensure_source_weight_table():
    """Ensure source_weight table exists for priority scoring."""
    conn = _get_conn()
    conn.execute("""CREATE TABLE IF NOT EXISTS source_weight (
        source_id INTEGER PRIMARY KEY,
        weight INTEGER DEFAULT 3,
        updated_at TEXT
    )""")
    conn.commit()
    conn.close()


def get_sources_with_metadata():
    """获取订阅源列表（含元数据：id, name, url, sub_type, feed_count）"""
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT s.id, s.name, s.url, s.sub_type, s.is_active,
                   COUNT(h.id) as feed_count
            FROM subscription s
            LEFT JOIN subscription_history h ON s.id = h.sub_id
            WHERE s.is_active = 1
            GROUP BY s.id
            ORDER BY feed_count DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_digest_feeds(time_range='today', limit=50):
    """获取摘要内容（用于智能排序）"""
    conn = _get_conn()
    try:
        sql = '''SELECT h.id, h.sub_id, h.sub_name, h.title, h.summary, h.link,
                        h.detected_at, h.author, h.thumbnail, h.comments, h.pub_date
                 FROM subscription_history h
                 WHERE 1=1'''
        params = []
        if time_range == 'today':
            sql += " AND date(h.detected_at) = date('now', 'localtime')"
        elif time_range == 'week':
            sql += " AND h.detected_at >= datetime('now', '-7 days', 'localtime')"
        elif time_range == 'month':
            sql += " AND h.detected_at >= datetime('now', '-30 days', 'localtime')"
        sql += ' ORDER BY h.detected_at DESC LIMIT ?'
        params.append(limit * 5)  # fetch more, will trim after scoring
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_source_weights():
    """获取所有源权重设置"""
    ensure_source_weight_table()
    conn = _get_conn()
    try:
        rows = conn.execute("SELECT source_id, weight FROM source_weight").fetchall()
        return {str(r['source_id']): r['weight'] for r in rows}
    finally:
        conn.close()


def set_source_weight(source_id, weight):
    """设置单个源的权重（1-5）"""
    ensure_source_weight_table()
    weight = max(1, min(5, int(weight)))
    conn = _get_conn()
    try:
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            "INSERT OR REPLACE INTO source_weight (source_id, weight, updated_at) VALUES (?, ?, ?)",
            (source_id, weight, now)
        )
        conn.commit()
    finally:
        conn.close()


def get_feeds_by_source(per_source=10, time_range=''):
    """按源分组获取内容"""
    conn = _get_conn()
    try:
        # 先获取活跃源列表
        sources = conn.execute(
            "SELECT id, name FROM subscription WHERE is_active = 1 ORDER BY name"
        ).fetchall()

        time_clause = ''
        if time_range == 'today':
            time_clause = " AND date(h.detected_at) = date('now', 'localtime')"
        elif time_range == 'week':
            time_clause = " AND h.detected_at >= datetime('now', '-7 days', 'localtime')"
        elif time_range == 'month':
            time_clause = " AND h.detected_at >= datetime('now', '-30 days', 'localtime')"

        result = {}
        for src in sources:
            rows = conn.execute(
                f"""SELECT h.id, h.sub_id, h.sub_name, h.title, h.summary, h.link,
                           h.detected_at, h.author, h.thumbnail, h.comments
                    FROM subscription_history h
                    WHERE h.sub_id = ?{time_clause}
                    ORDER BY h.detected_at DESC LIMIT ?""",
                (src['id'], per_source)
            ).fetchall()
            if rows:
                result[src['name']] = [dict(r) for r in rows]
        return result
    finally:
        conn.close()


def _parse_content(content):
    """解析RSS内容，清理XML标签，返回纯净HTML"""
    if not content:
        return ''
    import re
    text = content
    # 移除 CDATA 包装
    text = re.sub(r'<!\[CDATA\[', '', text)
    text = re.sub(r'\]\]>', '', text)
    # 如果内容是 RSS XML 格式，提取 description 中的内容
    desc_match = re.search(r'<description>([\s\S]*?)</description>', text)
    if desc_match:
        text = desc_match.group(1)
        # 再次清理 CDATA
        text = re.sub(r'<!\[CDATA\[', '', text)
        text = re.sub(r'\]\]>', '', text)
    # 移除 RSS/XML 特有标签
    for tag in ['item', 'channel', 'rss', 'feed', 'entry', 'guid', 'pubDate',
                'dc:creator', 'dc:date', 'category', 'comments', 'enclosure']:
        text = re.sub(rf'</?{re.escape(tag)}[^>]*>', '', text)
    # 清理多余空白
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text


def _extract_thumbnail(content):
    """从RSS内容中提取缩略图URL"""
    if not content:
        return None
    import re
    # 尝试 enclosure
    enc_match = re.search(r'<enclosure[^>]+url=["\']([^"\']+)["\']', content)
    if enc_match:
        return enc_match.group(1)
    # 尝试 media:thumbnail
    media_match = re.search(r'<media:thumbnail[^>]+url=["\']([^"\']+)["\']', content)
    if media_match:
        return media_match.group(1)
    # 尝试 img 标签
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if img_match:
        return img_match.group(1)
    return None


def _extract_author(content):
    """从RSS内容中提取作者信息"""
    if not content:
        return None
    import re
    # dc:creator
    creator_match = re.search(r'<dc:creator><!\[CDATA\[([^\]]+)\]\]></dc:creator>', content)
    if creator_match:
        return creator_match.group(1)
    creator_match2 = re.search(r'<dc:creator>([^<]+)</dc:creator>', content)
    if creator_match2:
        return creator_match2.group(1)
    # author 标签
    author_match = re.search(r'<author>([^<]+)</author>', content)
    if author_match:
        return author_match.group(1)
    return None
