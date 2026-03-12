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
        f"SELECT id, title, summary, source, category, time, hot_score, link, author "
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
            'hot_score': row[6], 'link': row[7], 'author': row[8] or ''
        })

    return {'data': news_list, 'total': total}


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
        "new_news_count, updated_news_count FROM crawl_log "
        "ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, (page - 1) * per_page)
    )
    logs = c.fetchall()
    conn.close()

    return {'logs': logs, 'total': total}


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
