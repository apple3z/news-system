"""
Semantic DAL - 语义爬虫数据访问层

管理 semantic_* 表的 CRUD 操作
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
    """确保语义爬虫所需的表存在"""
    conn = _get_conn()
    try:
        # semantic_tasks 表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                user_query TEXT NOT NULL,
                generated_keywords TEXT,
                intent_analysis TEXT,
                status TEXT DEFAULT 'pending',
                task_config TEXT DEFAULT '{}',
                progress INTEGER DEFAULT 0,
                total_items INTEGER DEFAULT 0,
                relevant_items INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                started_at TEXT,
                completed_at TEXT
            )
        """)

        # semantic_results 表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                result_type TEXT NOT NULL,
                data TEXT NOT NULL,
                generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES semantic_tasks(id) ON DELETE CASCADE
            )
        """)

        # semantic_sources 表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                source_type TEXT NOT NULL,
                source_name TEXT,
                source_url TEXT,
                items_count INTEGER DEFAULT 0,
                relevant_count INTEGER DEFAULT 0,
                discovered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES semantic_tasks(id) ON DELETE CASCADE
            )
        """)

        # semantic_items 表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                source_id INTEGER,
                title TEXT,
                summary TEXT,
                content TEXT,
                url TEXT,
                relevance_score REAL DEFAULT 0,
                entities TEXT,
                keywords TEXT,
                published_at TEXT,
                collected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES semantic_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (source_id) REFERENCES semantic_sources(id) ON DELETE SET NULL
            )
        """)

        # 索引
        conn.execute("CREATE INDEX IF NOT EXISTS idx_results_task_id ON semantic_results(task_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sources_task_id ON semantic_sources(task_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_items_task_id ON semantic_items(task_id)")

        conn.commit()
    finally:
        conn.close()


# ===== semantic_tasks CRUD =====

def create_task(name: str, user_query: str, config: dict = None) -> int:
    """创建语义任务"""
    ensure_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.execute("""
            INSERT INTO semantic_tasks
            (name, user_query, task_config, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
        """, (name, user_query, json.dumps(config or {}), now))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_task(task_id: int) -> dict:
    """获取任务"""
    ensure_tables()
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM semantic_tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def list_tasks(status: str = None, limit: int = 50) -> list:
    """列出任务"""
    ensure_tables()
    conn = _get_conn()
    try:
        sql = "SELECT * FROM semantic_tasks"
        params = []
        if status:
            sql += " WHERE status = ?"
            params.append(status)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def update_task(task_id: int, updates: dict) -> bool:
    """更新任务"""
    ensure_tables()
    conn = _get_conn()
    try:
        set_clauses = []
        params = []

        for field in ['name', 'user_query', 'generated_keywords', 'intent_analysis',
                      'status', 'task_config', 'progress', 'total_items',
                      'relevant_items', 'error_message', 'started_at', 'completed_at']:
            if field in updates:
                if field in ['task_config', 'generated_keywords', 'intent_analysis']:
                    set_clauses.append(f"{field} = ?")
                    params.append(json.dumps(updates[field]) if updates[field] else '{}')
                else:
                    set_clauses.append(f"{field} = ?")
                    params.append(updates[field])

        if not set_clauses:
            return False

        params.append(task_id)
        conn.execute(
            f"UPDATE semantic_tasks SET {', '.join(set_clauses)} WHERE id = ?",
            params
        )
        conn.commit()
        return True
    finally:
        conn.close()


# ===== semantic_results CRUD =====

def save_result(task_id: int, result_type: str, data: dict) -> int:
    """保存分析结果"""
    ensure_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.execute("""
            INSERT INTO semantic_results (task_id, result_type, data, generated_at)
            VALUES (?, ?, ?, ?)
        """, (task_id, result_type, json.dumps(data), now))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_results(task_id: int, result_type: str = None) -> list:
    """获取分析结果"""
    ensure_tables()
    conn = _get_conn()
    try:
        sql = "SELECT * FROM semantic_results WHERE task_id = ?"
        params = [task_id]
        if result_type:
            sql += " AND result_type = ?"
            params.append(result_type)
        sql += " ORDER BY generated_at DESC"
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


# ===== semantic_sources CRUD =====

def save_source(task_id: int, source_type: str, source_name: str,
                source_url: str = None) -> int:
    """保存发现的来源"""
    ensure_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.execute("""
            INSERT INTO semantic_sources
            (task_id, source_type, source_name, source_url, discovered_at)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, source_type, source_name, source_url, now))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_source_stats(source_id: int, items_count: int, relevant_count: int):
    """更新来源统计"""
    conn = _get_conn()
    try:
        conn.execute("""
            UPDATE semantic_sources SET items_count = ?, relevant_count = ?
            WHERE id = ?
        """, (items_count, relevant_count, source_id))
        conn.commit()
    finally:
        conn.close()


def get_sources(task_id: int) -> list:
    """获取任务的所有来源"""
    ensure_tables()
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT * FROM semantic_sources WHERE task_id = ?
            ORDER BY discovered_at DESC
        """, (task_id,)).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


# ===== semantic_items CRUD =====

def save_item(task_id: int, source_id: int, item: dict) -> int:
    """保存采集内容"""
    ensure_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.execute("""
            INSERT INTO semantic_items
            (task_id, source_id, title, summary, content, url,
             relevance_score, entities, keywords, published_at, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, source_id,
            item.get('title'), item.get('summary'), item.get('content'), item.get('url'),
            item.get('relevance_score', 0),
            json.dumps(item.get('entities', [])),
            json.dumps(item.get('keywords', [])),
            item.get('published_at'),
            now
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def save_items_batch(task_id: int, source_id: int, items: list) -> int:
    """批量保存采集内容"""
    ensure_tables()
    conn = _get_conn()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        count = 0
        for item in items:
            conn.execute("""
                INSERT INTO semantic_items
                (task_id, source_id, title, summary, content, url,
                 relevance_score, entities, keywords, published_at, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id, source_id,
                item.get('title'), item.get('summary'), item.get('content'), item.get('url'),
                item.get('relevance_score', 0),
                json.dumps(item.get('entities', [])),
                json.dumps(item.get('keywords', [])),
                item.get('published_at'),
                now
            ))
            count += 1
        conn.commit()
        return count
    finally:
        conn.close()


def get_items(task_id: int, min_relevance: float = 0, limit: int = 100) -> list:
    """获取采集内容"""
    ensure_tables()
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT * FROM semantic_items
            WHERE task_id = ? AND relevance_score >= ?
            ORDER BY relevance_score DESC, collected_at DESC
            LIMIT ?
        """, (task_id, min_relevance, limit)).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_task_stats(task_id: int) -> dict:
    """获取任务统计"""
    ensure_tables()
    conn = _get_conn()
    try:
        total = conn.execute(
            "SELECT COUNT(*) as c FROM semantic_items WHERE task_id = ?", (task_id,)
        ).fetchone()['c']
        relevant = conn.execute(
            "SELECT COUNT(*) as c FROM semantic_items WHERE task_id = ? AND relevance_score >= 0.5",
            (task_id,)
        ).fetchone()['c']
        return {'total': total, 'relevant': relevant}
    finally:
        conn.close()


# ===== 工具函数 =====

def _row_to_dict(row: sqlite3.Row) -> dict:
    """将 Row 转换为字典"""
    if not row:
        return None
    d = dict(row)
    # 解析 JSON 字段
    for field in ['task_config', 'generated_keywords', 'intent_analysis', 'entities', 'keywords']:
        if field in d and d[field]:
            try:
                d[field] = json.loads(d[field])
            except:
                pass
    return d
