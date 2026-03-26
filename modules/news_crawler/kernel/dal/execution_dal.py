"""
Execution DAL - 执行记录数据访问层

管理 crawl_executions 表的 CRUD 操作
"""

import sqlite3
import json
from datetime import datetime
from config import SYSTEM_DB


def _get_conn():
    conn = sqlite3.connect(SYSTEM_DB)
    conn.row_factory = sqlite3.Row
    return conn


def create_execution(task_id: int, source_id: int = None, source_name: str = '') -> int:
    """创建执行记录"""
    from modules.news_crawler.kernel.dal.task_dal import ensure_kernel_tables
    ensure_kernel_tables()

    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.execute("""
            INSERT INTO crawl_executions
            (task_id, source_id, source_name, start_time, status)
            VALUES (?, ?, ?, ?, 'running')
        """, (task_id, source_id, source_name, now))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_execution(exec_id: int, updates: dict) -> bool:
    """更新执行记录"""
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        set_clauses = ['end_time = ?']
        params = [now]

        if 'status' in updates:
            set_clauses.append('status = ?')
            params.append(updates['status'])
        if 'items_total' in updates:
            set_clauses.append('items_total = ?')
            params.append(updates['items_total'])
        if 'items_new' in updates:
            set_clauses.append('items_new = ?')
            params.append(updates['items_new'])
        if 'items_updated' in updates:
            set_clauses.append('items_updated = ?')
            params.append(updates['items_updated'])
        if 'error_message' in updates:
            set_clauses.append('error_message = ?')
            params.append(updates['error_message'])
        if 'detail' in updates:
            set_clauses.append('detail = ?')
            params.append(json.dumps(updates['detail']))

        params.append(exec_id)
        conn.execute(
            f"UPDATE crawl_executions SET {', '.join(set_clauses)} WHERE id = ?",
            params
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_execution(exec_id: int) -> dict:
    """获取单个执行记录"""
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM crawl_executions WHERE id = ?", (exec_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def get_executions_by_task(task_id: int, limit: int = 50) -> list:
    """获取任务的所有执行记录"""
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT * FROM crawl_executions
            WHERE task_id = ?
            ORDER BY start_time DESC
            LIMIT ?
        """, (task_id, limit)).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_recent_executions(limit: int = 100) -> list:
    """获取最近的执行记录"""
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT e.*, t.name as task_name, t.task_type
            FROM crawl_executions e
            LEFT JOIN crawl_tasks t ON e.task_id = t.id
            ORDER BY e.start_time DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_execution_stats(task_id: int = None, date_from: str = None) -> dict:
    """获取执行统计"""
    conn = _get_conn()
    try:
        where_clause = "WHERE 1=1"
        params = []

        if task_id:
            where_clause += " AND task_id = ?"
            params.append(task_id)
        if date_from:
            where_clause += " AND date(start_time) >= date(?)"
            params.append(date_from)

        total = conn.execute(
            f"SELECT COUNT(*) as c FROM crawl_executions {where_clause}",
            params
        ).fetchone()['c']

        completed = conn.execute(
            f"SELECT COUNT(*) as c FROM crawl_executions {where_clause} AND status = 'completed'",
            params
        ).fetchone()['c']

        failed = conn.execute(
            f"SELECT COUNT(*) as c FROM crawl_executions {where_clause} AND status = 'failed'",
            params
        ).fetchone()['c']

        total_items = conn.execute(
            f"SELECT COALESCE(SUM(items_total), 0) as s FROM crawl_executions {where_clause}",
            params
        ).fetchone()['s']

        total_new = conn.execute(
            f"SELECT COALESCE(SUM(items_new), 0) as s FROM crawl_executions {where_clause}",
            params
        ).fetchone()['s']

        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'items_total': total_items,
            'items_new': total_new
        }
    finally:
        conn.close()


def get_running_executions() -> list:
    """获取正在执行的记录"""
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT e.*, t.name as task_name
            FROM crawl_executions e
            LEFT JOIN crawl_tasks t ON e.task_id = t.id
            WHERE e.status = 'running'
            ORDER BY e.start_time DESC
        """).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """将 Row 转换为字典"""
    if not row:
        return None
    d = dict(row)
    # 解析 JSON 字段
    if d.get('detail'):
        try:
            d['detail'] = json.loads(d['detail'])
        except:
            pass
    return d
