"""
Task DAL - 任务数据访问层

管理 crawl_tasks 表的 CRUD 操作
"""

import sqlite3
import json
from datetime import datetime
from config import SYSTEM_DB


def _get_conn():
    conn = sqlite3.connect(SYSTEM_DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_kernel_tables():
    """确保内核所需的表存在"""
    conn = _get_conn()
    try:
        # crawl_tasks 表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crawl_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                task_type TEXT NOT NULL,
                trigger_type TEXT DEFAULT 'manual',
                trigger_config TEXT DEFAULT '{}',
                source_filter TEXT DEFAULT '[]',
                pipeline TEXT DEFAULT '["fetch","parse","store"]',
                config TEXT DEFAULT '{}',
                status TEXT DEFAULT 'pending',
                enabled INTEGER DEFAULT 1,
                last_run_time TEXT,
                last_run_result TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # crawl_executions 表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crawl_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                source_id INTEGER,
                source_name TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT DEFAULT 'running',
                items_total INTEGER DEFAULT 0,
                items_new INTEGER DEFAULT 0,
                items_updated INTEGER DEFAULT 0,
                error_message TEXT,
                detail TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES crawl_tasks(id) ON DELETE CASCADE
            )
        """)

        # schedule_log 表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedule_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                event_type TEXT,
                event_time TEXT,
                message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 索引
        conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_task_id ON crawl_executions(task_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_source_id ON crawl_executions(source_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_start_time ON crawl_executions(start_time)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_schedule_log_task_time ON schedule_log(task_id, event_time)")

        conn.commit()
    finally:
        conn.close()


def create_task(task: dict) -> int:
    """
    创建新任务
    task: {
        name, task_type, trigger_type, trigger_config,
        source_filter, pipeline, config, enabled
    }
    """
    ensure_kernel_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.execute("""
            INSERT INTO crawl_tasks
            (name, task_type, trigger_type, trigger_config, source_filter,
             pipeline, config, status, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
        """, (
            task.get('name', ''),
            task.get('task_type', 'news'),
            task.get('trigger_type', 'manual'),
            json.dumps(task.get('trigger_config', {})),
            json.dumps(task.get('source_filter', [])),
            json.dumps(task.get('pipeline', ['fetch', 'parse', 'store'])),
            json.dumps(task.get('config', {})),
            1 if task.get('enabled', True) else 0,
            now, now
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_task(task_id: int) -> dict:
    """获取单个任务"""
    ensure_kernel_tables()
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM crawl_tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def list_tasks(task_type: str = None, status: str = None, enabled: bool = None) -> list:
    """
    列出任务
    """
    ensure_kernel_tables()
    conn = _get_conn()
    try:
        sql = "SELECT * FROM crawl_tasks WHERE 1=1"
        params = []

        if task_type:
            sql += " AND task_type = ?"
            params.append(task_type)
        if status:
            sql += " AND status = ?"
            params.append(status)
        if enabled is not None:
            sql += " AND enabled = ?"
            params.append(1 if enabled else 0)

        sql += " ORDER BY created_at DESC"
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def update_task(task_id: int, task: dict) -> bool:
    """更新任务"""
    ensure_kernel_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute("""
            UPDATE crawl_tasks SET
                name = ?,
                task_type = ?,
                trigger_type = ?,
                trigger_config = ?,
                source_filter = ?,
                pipeline = ?,
                config = ?,
                enabled = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            task.get('name'),
            task.get('task_type'),
            task.get('trigger_type'),
            json.dumps(task.get('trigger_config', {})),
            json.dumps(task.get('source_filter', [])),
            json.dumps(task.get('pipeline', ['fetch', 'parse', 'store'])),
            json.dumps(task.get('config', {})),
            1 if task.get('enabled', True) else 0,
            now,
            task_id
        ))
        conn.commit()
        return True
    finally:
        conn.close()


def delete_task(task_id: int) -> bool:
    """删除任务"""
    ensure_kernel_tables()
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM crawl_tasks WHERE id = ?", (task_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def update_task_status(task_id: int, status: str,
                       last_run_time: str = None,
                       last_run_result: dict = None) -> bool:
    """更新任务状态和执行结果"""
    ensure_kernel_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result_json = json.dumps(last_run_result) if last_run_result else None

        if last_run_time:
            conn.execute("""
                UPDATE crawl_tasks SET
                    status = ?,
                    last_run_time = ?,
                    last_run_result = ?,
                    updated_at = ?
                WHERE id = ?
            """, (status, last_run_time, result_json, now, task_id))
        else:
            conn.execute("""
                UPDATE crawl_tasks SET status = ?, updated_at = ? WHERE id = ?
            """, (status, now, task_id))
        conn.commit()
        return True
    finally:
        conn.close()


def get_task_stats() -> dict:
    """获取任务统计"""
    ensure_kernel_tables()
    conn = _get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) as c FROM crawl_tasks").fetchone()['c']
        active = conn.execute(
            "SELECT COUNT(*) as c FROM crawl_tasks WHERE status = 'running'"
        ).fetchone()['c']
        pending = conn.execute(
            "SELECT COUNT(*) as c FROM crawl_tasks WHERE status = 'pending'"
        ).fetchone()['c']
        completed_today = conn.execute(
            "SELECT COUNT(*) as c FROM crawl_tasks WHERE status = 'completed' AND date(last_run_time) = date('now', 'localtime')"
        ).fetchone()['c']
        failed_today = conn.execute(
            "SELECT COUNT(*) as c FROM crawl_tasks WHERE status = 'failed' AND date(last_run_time) = date('now', 'localtime')"
        ).fetchone()['c']

        return {
            'total': total,
            'active': active,
            'pending': pending,
            'completed_today': completed_today,
            'failed_today': failed_today
        }
    finally:
        conn.close()


def log_schedule_event(task_id: int, event_type: str, message: str = ''):
    """记录调度事件"""
    ensure_kernel_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute("""
            INSERT INTO schedule_log (task_id, event_type, event_time, message)
            VALUES (?, ?, ?, ?)
        """, (task_id, event_type, now, message))
        conn.commit()
    finally:
        conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """将 Row 转换为字典"""
    if not row:
        return None
    d = dict(row)
    # 解析 JSON 字段
    for field in ['trigger_config', 'source_filter', 'pipeline', 'config', 'last_run_result']:
        if field in d and d[field]:
            try:
                d[field] = json.loads(d[field])
            except:
                pass
    # 转换 enabled
    d['enabled'] = bool(d.get('enabled'))
    return d
