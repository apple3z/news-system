"""
数据源管理数据访问层
"""

import sqlite3
import json
from datetime import datetime
from config import SYSTEM_DB


def _get_conn():
    conn = sqlite3.connect(SYSTEM_DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables():
    """确保 data_sources 和 unified_crawl_log 表存在"""
    conn = _get_conn()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            url TEXT NOT NULL,
            config TEXT DEFAULT '{}',
            status TEXT DEFAULT 'active',
            priority INTEGER DEFAULT 10,
            last_crawl_time TEXT,
            last_crawl_status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS unified_crawl_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            status TEXT DEFAULT 'running',
            total_count INTEGER DEFAULT 0,
            new_count INTEGER DEFAULT 0,
            updated_count INTEGER DEFAULT 0,
            detail TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
    finally:
        conn.close()


# ========== 数据源 CRUD ==========

def list_sources(source_type=None, status=None):
    """获取数据源列表"""
    conn = _get_conn()
    try:
        sql = 'SELECT * FROM data_sources WHERE 1=1'
        params = []
        if source_type:
            sql += ' AND type = ?'
            params.append(source_type)
        if status:
            sql += ' AND status = ?'
            params.append(status)
        sql += ' ORDER BY type, priority DESC, id'
        rows = conn.execute(sql, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d['config'] = json.loads(d['config']) if d['config'] else {}
            result.append(d)
        return result
    finally:
        conn.close()


def get_source(source_id):
    """获取单个数据源"""
    conn = _get_conn()
    try:
        row = conn.execute('SELECT * FROM data_sources WHERE id = ?', (source_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d['config'] = json.loads(d['config']) if d['config'] else {}
        return d
    finally:
        conn.close()


def create_source(data):
    """创建数据源"""
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        config_str = json.dumps(data.get('config', {}), ensure_ascii=False)
        conn.execute(
            'INSERT INTO data_sources (name, type, url, config, status, priority, created_at, updated_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (data['name'], data['type'], data['url'], config_str,
             data.get('status', 'active'), data.get('priority', 10), now, now)
        )
        conn.commit()
        return {'code': 200, 'message': '创建成功'}
    finally:
        conn.close()


def update_source(source_id, data):
    """更新数据源"""
    conn = _get_conn()
    try:
        fields = []
        values = []
        for key in ('name', 'type', 'url', 'status', 'priority'):
            if key in data:
                fields.append(f'{key} = ?')
                values.append(data[key])
        if 'config' in data:
            fields.append('config = ?')
            values.append(json.dumps(data['config'], ensure_ascii=False))
        if not fields:
            return {'code': 400, 'message': '无更新内容'}
        fields.append('updated_at = ?')
        values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        values.append(source_id)
        conn.execute(
            f'UPDATE data_sources SET {", ".join(fields)} WHERE id = ?', values
        )
        conn.commit()
        return {'code': 200, 'message': '更新成功'}
    finally:
        conn.close()


def delete_source(source_id):
    """删除数据源"""
    conn = _get_conn()
    try:
        conn.execute('DELETE FROM data_sources WHERE id = ?', (source_id,))
        conn.commit()
        return {'code': 200, 'message': '删除成功'}
    finally:
        conn.close()


def toggle_source(source_id):
    """切换数据源状态"""
    conn = _get_conn()
    try:
        row = conn.execute('SELECT status FROM data_sources WHERE id = ?', (source_id,)).fetchone()
        if not row:
            return {'code': 404, 'message': '数据源不存在'}
        new_status = 'inactive' if row['status'] == 'active' else 'active'
        conn.execute(
            'UPDATE data_sources SET status = ?, updated_at = ? WHERE id = ?',
            (new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), source_id)
        )
        conn.commit()
        return {'code': 200, 'message': f'已{"启用" if new_status == "active" else "禁用"}'}
    finally:
        conn.close()


def get_source_counts():
    """获取各类型数据源数量统计"""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT type, COUNT(*) as count FROM data_sources WHERE status = 'active' GROUP BY type"
        ).fetchall()
        counts = {r['type']: r['count'] for r in rows}
        return counts
    finally:
        conn.close()


def update_crawl_status(source_id, status, crawl_time=None):
    """更新数据源采集状态"""
    conn = _get_conn()
    try:
        if not crawl_time:
            crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'UPDATE data_sources SET last_crawl_time = ?, last_crawl_status = ? WHERE id = ?',
            (crawl_time, status, source_id)
        )
        conn.commit()
    finally:
        conn.close()


# ========== 统一采集日志 ==========

def create_crawl_log(log_type):
    """创建采集日志"""
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.execute(
            'INSERT INTO unified_crawl_log (type, start_time, status, created_at) VALUES (?, ?, ?, ?)',
            (log_type, now, 'running', now)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_crawl_log(log_id, status, total=0, new=0, updated=0, detail=None):
    """更新采集日志"""
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        detail_str = json.dumps(detail or {}, ensure_ascii=False)
        conn.execute(
            'UPDATE unified_crawl_log SET end_time = ?, status = ?, '
            'total_count = ?, new_count = ?, updated_count = ?, detail = ? WHERE id = ?',
            (now, status, total, new, updated, detail_str, log_id)
        )
        conn.commit()
    finally:
        conn.close()


def list_crawl_logs(log_type=None, page=1, per_page=20):
    """获取采集日志列表"""
    conn = _get_conn()
    try:
        sql = 'SELECT * FROM unified_crawl_log WHERE 1=1'
        count_sql = 'SELECT COUNT(*) FROM unified_crawl_log WHERE 1=1'
        params = []
        if log_type:
            sql += ' AND type = ?'
            count_sql += ' AND type = ?'
            params.append(log_type)
        total = conn.execute(count_sql, params).fetchone()[0]
        sql += ' ORDER BY id DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        rows = conn.execute(sql, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d['detail'] = json.loads(d['detail']) if d['detail'] else {}
            result.append(d)
        return {'data': result, 'total': total, 'page': page, 'per_page': per_page}
    finally:
        conn.close()


def seed_default_sources():
    """初始化默认数据源（如果表为空则插入）"""
    conn = _get_conn()
    try:
        count = conn.execute('SELECT COUNT(*) FROM data_sources').fetchone()[0]
        if count > 0:
            return
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 新闻源（现有10个）
        news_sources = [
            ('网易科技', 'news', 'https://tech.163.com/', 15, {'keywords': 'AI,智能,大模型,GPT,芯片,科技'}),
            ('新浪科技', 'news', 'https://tech.sina.com.cn/', 10, {'keywords': 'AI,智能,大模型,GPT,芯片,科技'}),
            ('凤凰科技', 'news', 'https://tech.ifeng.com/', 8, {'keywords': 'AI,智能,大模型,GPT,芯片,科技'}),
            ('36氪', 'news', 'https://36kr.com/', 12, {'keywords': 'AI,智能,大模型,创业,融资'}),
            ('虎嗅网', 'news', 'https://www.huxiu.com/', 10, {'keywords': 'AI,智能,大模型,GPT,芯片,科技'}),
            ('机器之心', 'news', 'https://www.jiqizhixin.com/', 15, {}),
            ('新智元', 'news', 'https://www.ai-era.com/', 15, {}),
            ('量子位', 'news', 'https://www.qbitai.com/', 15, {}),
            ('InfoQ', 'news', 'https://www.infoq.cn/', 10, {'keywords': 'AI,智能,大模型,架构,技术'}),
            ('CSDN', 'news', 'https://www.csdn.net/', 8, {'keywords': 'AI,智能,大模型,Python,技术'}),
        ]
        for name, stype, url, priority, config in news_sources:
            conn.execute(
                'INSERT INTO data_sources (name, type, url, config, priority, created_at, updated_at) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, stype, url, json.dumps(config, ensure_ascii=False), priority, now, now)
            )
        # Skills源（现有10个）
        skills_sources = [
            ('Himalaya', 'skill', 'https://clawhub.ai/skill/lamelas/himalaya', 10, {'owner': 'lamelas', 'name': 'himalaya'}),
            ('Cursor', 'skill', 'https://clawhub.ai/skill/cursor/cursor', 10, {'owner': 'cursor', 'name': 'cursor'}),
            ('PPTX', 'skill', 'https://clawhub.ai/skill/pptx/pptx', 10, {'owner': 'pptx', 'name': 'pptx'}),
            ('PDF', 'skill', 'https://clawhub.ai/skill/pdf/pdf', 10, {'owner': 'pdf', 'name': 'pdf'}),
            ('DOCX', 'skill', 'https://clawhub.ai/skill/docx/docx', 10, {'owner': 'docx', 'name': 'docx'}),
            ('XLSX', 'skill', 'https://clawhub.ai/skill/xlsx/xlsx', 10, {'owner': 'xlsx', 'name': 'xlsx'}),
            ('News', 'skill', 'https://clawhub.ai/skill/news/news', 10, {'owner': 'news', 'name': 'news'}),
            ('Cron', 'skill', 'https://clawhub.ai/skill/cron/cron', 10, {'owner': 'cron', 'name': 'cron'}),
            ('MCP', 'skill', 'https://clawhub.ai/skill/mcp/mcp', 10, {'owner': 'mcp', 'name': 'mcp'}),
            ('GitHub', 'skill', 'https://clawhub.ai/skill/github/github', 10, {'owner': 'github', 'name': 'github'}),
        ]
        for name, stype, url, priority, config in skills_sources:
            conn.execute(
                'INSERT INTO data_sources (name, type, url, config, priority, created_at, updated_at) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, stype, url, json.dumps(config, ensure_ascii=False), priority, now, now)
            )
        conn.commit()
    finally:
        conn.close()
