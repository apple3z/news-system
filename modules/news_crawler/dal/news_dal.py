"""
News data access layer.
All news.db SQL operations extracted from routes/news.py and routes/admin.py.
"""

import sqlite3
from config import NEWS_DB


def _get_conn():
    return sqlite3.connect(NEWS_DB)


def search_news(keyword='', category='', source='', date_from='', date_to='',
                sort_by='time', sort_order='desc', page=1, per_page=20):
    """Search news with filters, sorting, and pagination."""
    conn = _get_conn()
    c = conn.cursor()

    # Validate sort_order to prevent SQL injection
    sort_order = 'ASC' if sort_order.upper() == 'ASC' else 'DESC'

    conditions = []
    params = []

    if keyword:
        conditions.append("(title LIKE ? OR summary LIKE ? OR content LIKE ?)")
        search_term = f"%{keyword}%"
        params.extend([search_term, search_term, search_term])

    if category:
        conditions.append("category = ?")
        params.append(category)

    if source:
        conditions.append("source = ?")
        params.append(source)

    if date_from:
        conditions.append("time >= ?")
        params.append(date_from)

    if date_to:
        conditions.append("time <= ?")
        params.append(date_to)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    c.execute(f"SELECT COUNT(*) FROM news WHERE {where_clause}", params)
    total = c.fetchone()[0]

    offset = (page - 1) * per_page

    # Build ORDER BY clause
    if sort_by == 'relevance' and keyword:
        order_clause = '''
            CASE
                WHEN title LIKE ? THEN 3
                WHEN summary LIKE ? THEN 2
                WHEN content LIKE ? THEN 1
                ELSE 0
            END DESC, hot_score DESC, time DESC
        '''
        search_term = f"%{keyword}%"
        params.extend([search_term, search_term, search_term])
    elif sort_by == 'hot_score':
        order_clause = f"hot_score {sort_order}, time DESC"
    elif sort_by == 'time':
        order_clause = f"time {sort_order}, hot_score DESC"
    else:
        order_clause = "time DESC, hot_score DESC"

    c.execute(
        f"SELECT id, title, summary, source, category, time, hot_score, link, author, content, image "
        f"FROM news WHERE {where_clause} ORDER BY {order_clause} LIMIT ? OFFSET ?",
        params + [per_page, offset]
    )
    rows = c.fetchall()
    conn.close()

    news_list = []
    for row in rows:
        news_list.append({
            'id': row[0], 'title': row[1], 'summary': row[2],
            'source': row[3], 'category': row[4], 'time': row[5],
            'hot_score': row[6], 'link': row[7], 'author': row[8] or '',
            'content': row[9] or '', 'image': row[10] or ''
        })

    return {'data': news_list, 'total': total}


def get_news_by_id(news_id):
    """Get a single news item by ID."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, summary, source, category, time, hot_score, link, author, "
        "content, image, keywords, entities, trend_level, view_count, created_at "
        "FROM news WHERE id = ?", (news_id,)
    )
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'id': row[0], 'title': row[1], 'summary': row[2],
        'source': row[3], 'category': row[4], 'time': row[5],
        'hot_score': row[6], 'link': row[7], 'author': row[8] or '',
        'content': row[9] or '', 'image': row[10] or '',
        'keywords': row[11] or '[]', 'entities': row[12] or '{}',
        'trend_level': row[13] or '', 'view_count': row[14] or 0,
        'created_at': row[15] or ''
    }


def get_categories():
    """Get news category list with counts."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT category, COUNT(*) as count
        FROM news
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
    """)
    categories = [{'name': row[0], 'count': row[1]} for row in c.fetchall()]
    conn.close()
    return categories


def get_sources():
    """Get news source list with counts."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT source, COUNT(*) as count
        FROM news
        WHERE source IS NOT NULL
        GROUP BY source
        ORDER BY count DESC
    """)
    sources = [{'name': row[0], 'count': row[1]} for row in c.fetchall()]
    conn.close()
    return sources


def get_crawl_logs(page=1, per_page=10):
    """Get crawl log entries with pagination."""
    conn = _get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM crawl_log")
    total = c.fetchone()[0]

    c.execute(
        "SELECT id, start_time, end_time, status, total_news_count, "
        "new_news_count, updated_news_count, error_message FROM crawl_log "
        "ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, (page - 1) * per_page)
    )
    logs = c.fetchall()
    conn.close()

    import json
    log_list = []
    for row in logs:
        detail = None
        if row[7]:
            try:
                detail = json.loads(row[7])
            except (json.JSONDecodeError, TypeError):
                detail = row[7]
        log_list.append({
            'id': row[0], 'start_time': row[1], 'end_time': row[2],
            'status': row[3], 'total_news_count': row[4],
            'new_news_count': row[5], 'updated_news_count': row[6],
            'detail': detail
        })

    return {'logs': log_list, 'total': total}


def get_daily_stats(days=30):
    """Get daily news count statistics for the last N days."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT time AS day, COUNT(*) AS count
        FROM news
        WHERE time >= date('now', '-' || ? || ' days')
        GROUP BY time
        ORDER BY time ASC
    """, (days,))
    rows = c.fetchall()
    conn.close()
    return [{'day': r[0], 'count': r[1]} for r in rows]


def get_daily_stats_by_type(days=30):
    """Get daily news count statistics grouped by source type (news/rss/skill).
    Maps source names to types via system.db data_sources table."""
    from config import SYSTEM_DB

    # Step 1: get source name → type mapping from system.db
    source_type_map = {}
    try:
        sys_conn = sqlite3.connect(SYSTEM_DB)
        sys_conn.row_factory = sqlite3.Row
        rows = sys_conn.execute("SELECT name, type FROM data_sources").fetchall()
        sys_conn.close()
        for r in rows:
            source_type_map[r['name']] = r['type']
    except Exception:
        pass

    # Step 2: get daily counts grouped by source from news.db
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT time AS day, source, COUNT(*) AS count
        FROM news
        WHERE time >= date('now', '-' || ? || ' days')
        GROUP BY time, source
        ORDER BY time ASC
    """, (days,))
    rows = c.fetchall()
    conn.close()

    # Step 3: aggregate by type
    # day → { news: count, rss: count }
    day_type = {}
    for day, source, count in rows:
        if not day:
            continue
        stype = source_type_map.get(source, 'news')  # default to 'news'
        if day not in day_type:
            day_type[day] = {'news': 0, 'rss': 0}
        if stype in ('news', 'rss'):
            day_type[day][stype] += count
        else:
            day_type[day]['news'] += count

    result = {'news': [], 'rss': []}
    for day in sorted(day_type.keys()):
        result['news'].append({'day': day, 'count': day_type[day]['news']})
        result['rss'].append({'day': day, 'count': day_type[day]['rss']})
    return result


def get_crawl_daily_stats(days=30):
    """Get daily crawl statistics for the last N days."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT DATE(start_time) AS day, COUNT(*) AS crawl_count,
               SUM(new_news_count) AS new_total, SUM(total_news_count) AS total
        FROM crawl_log
        WHERE start_time >= date('now', '-' || ? || ' days')
        GROUP BY DATE(start_time)
        ORDER BY day ASC
    """, (days,))
    rows = c.fetchall()
    conn.close()
    return [{'day': r[0], 'crawl_count': r[1], 'new_total': r[2] or 0, 'total': r[3] or 0} for r in rows]


def search_by_keywords(keywords):
    """Search news matching a list of keywords. Used by subscribe module via proxy."""
    conn = _get_conn()
    c = conn.cursor()

    conditions = []
    params = []
    for kw in keywords:
        if kw.strip():
            conditions.append("(title LIKE ? OR summary LIKE ? OR content LIKE ?)")
            term = f"%{kw.strip()}%"
            params.extend([term, term, term])

    if conditions:
        where = " OR ".join(conditions)
        c.execute(
            f"SELECT id, title, source, time FROM news "
            f"WHERE {where} ORDER BY time DESC LIMIT 20",
            params
        )
    else:
        c.execute("SELECT id, title, source, time FROM news ORDER BY time DESC LIMIT 20")

    results = c.fetchall()
    conn.close()

    return [{'id': r[0], 'title': r[1], 'source': r[2], 'time': r[3]} for r in results]
