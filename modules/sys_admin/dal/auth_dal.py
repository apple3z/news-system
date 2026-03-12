"""
账户管理数据访问层
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from config import SYSTEM_DB


def _get_conn():
    conn = sqlite3.connect(SYSTEM_DB)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def _generate_salt():
    return os.urandom(16).hex()


def ensure_tables():
    """确保 admin_users 表存在"""
    conn = _get_conn()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            display_name TEXT,
            role TEXT DEFAULT 'admin',
            status TEXT DEFAULT 'active',
            last_login TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
    finally:
        conn.close()


def verify_login(username, password):
    """验证登录，返回用户信息或 None"""
    conn = _get_conn()
    try:
        row = conn.execute(
            'SELECT * FROM admin_users WHERE username = ?', (username,)
        ).fetchone()
        if not row:
            return None
        if row['status'] != 'active':
            return None
        if _hash_password(password, row['salt']) != row['password_hash']:
            return None
        # 更新最后登录时间
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'UPDATE admin_users SET last_login = ? WHERE id = ?',
            (now, row['id'])
        )
        conn.commit()
        return dict(row)
    finally:
        conn.close()


def list_users():
    """获取所有用户列表"""
    conn = _get_conn()
    try:
        rows = conn.execute(
            'SELECT id, username, display_name, role, status, last_login, created_at '
            'FROM admin_users ORDER BY id'
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_user(user_id):
    """获取单个用户"""
    conn = _get_conn()
    try:
        row = conn.execute(
            'SELECT id, username, display_name, role, status, last_login, created_at '
            'FROM admin_users WHERE id = ?', (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_user(username, password, display_name='', role='admin'):
    """创建用户"""
    conn = _get_conn()
    try:
        salt = _generate_salt()
        password_hash = _hash_password(password, salt)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'INSERT INTO admin_users (username, password_hash, salt, display_name, role, created_at, updated_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (username, password_hash, salt, display_name, role, now, now)
        )
        conn.commit()
        return {'code': 200, 'message': '创建成功'}
    except sqlite3.IntegrityError:
        return {'code': 400, 'message': '用户名已存在'}
    finally:
        conn.close()


def update_user(user_id, data):
    """更新用户信息（不含密码）"""
    conn = _get_conn()
    try:
        fields = []
        values = []
        for key in ('display_name', 'role', 'status'):
            if key in data:
                fields.append(f'{key} = ?')
                values.append(data[key])
        if not fields:
            return {'code': 400, 'message': '无更新内容'}
        fields.append('updated_at = ?')
        values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        values.append(user_id)
        conn.execute(
            f'UPDATE admin_users SET {", ".join(fields)} WHERE id = ?', values
        )
        conn.commit()
        return {'code': 200, 'message': '更新成功'}
    finally:
        conn.close()


def reset_password(user_id, new_password):
    """重置密码"""
    conn = _get_conn()
    try:
        salt = _generate_salt()
        password_hash = _hash_password(new_password, salt)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'UPDATE admin_users SET password_hash = ?, salt = ?, updated_at = ? WHERE id = ?',
            (password_hash, salt, now, user_id)
        )
        conn.commit()
        return {'code': 200, 'message': '密码重置成功'}
    finally:
        conn.close()


def delete_user(user_id):
    """删除用户"""
    conn = _get_conn()
    try:
        # 不允许删除最后一个超级管理员
        count = conn.execute(
            "SELECT COUNT(*) FROM admin_users WHERE role = 'super_admin' AND id != ?",
            (user_id,)
        ).fetchone()[0]
        row = conn.execute('SELECT role FROM admin_users WHERE id = ?', (user_id,)).fetchone()
        if row and row['role'] == 'super_admin' and count == 0:
            return {'code': 400, 'message': '不能删除最后一个超级管理员'}
        conn.execute('DELETE FROM admin_users WHERE id = ?', (user_id,))
        conn.commit()
        return {'code': 200, 'message': '删除成功'}
    finally:
        conn.close()
