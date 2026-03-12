"""
共享鉴权装饰器
供所有模块的 admin API 路由使用
"""

from flask import session, jsonify
from functools import wraps


def login_required(f):
    """登录鉴权装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated


def super_admin_required(f):
    """超级管理员权限装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '未登录'}), 401
        if session.get('role') != 'super_admin':
            return jsonify({'code': 403, 'message': '权限不足'}), 403
        return f(*args, **kwargs)
    return decorated
