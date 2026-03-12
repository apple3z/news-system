"""
账户管理API路由层
"""

from flask import request, session, jsonify
from functools import wraps
from modules.sys_admin.routes import sys_admin_bp
from modules.sys_admin.services import auth_service


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


# ========== 登录/登出 ==========

@sys_admin_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    result = auth_service.login(data.get('username', ''), data.get('password', ''))
    if result['code'] == 200:
        user = result['data']
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['display_name'] = user['display_name']
        session['role'] = user['role']
        session.permanent = True
    return jsonify(result)


@sys_admin_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'code': 200, 'message': '已登出'})


@sys_admin_bp.route('/api/auth/me', methods=['GET'])
def api_me():
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '未登录'})
    return jsonify({
        'code': 200,
        'data': {
            'id': session['user_id'],
            'username': session['username'],
            'display_name': session.get('display_name', ''),
            'role': session.get('role', 'admin')
        }
    })


# ========== 账户管理 CRUD ==========

@sys_admin_bp.route('/api/admin/users', methods=['GET'])
@login_required
def api_list_users():
    result = auth_service.get_all_users()
    return jsonify(result)


@sys_admin_bp.route('/api/admin/users', methods=['POST'])
@super_admin_required
def api_create_user():
    data = request.get_json() or {}
    result = auth_service.add_user(
        data.get('username', ''),
        data.get('password', ''),
        data.get('display_name', ''),
        data.get('role', 'admin')
    )
    return jsonify(result)


@sys_admin_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@super_admin_required
def api_update_user(user_id):
    data = request.get_json() or {}
    result = auth_service.modify_user(user_id, data)
    return jsonify(result)


@sys_admin_bp.route('/api/admin/users/<int:user_id>/password', methods=['PUT'])
@super_admin_required
def api_reset_password(user_id):
    data = request.get_json() or {}
    result = auth_service.change_password(user_id, data.get('password', ''))
    return jsonify(result)


@sys_admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@super_admin_required
def api_delete_user(user_id):
    result = auth_service.remove_user(user_id)
    return jsonify(result)
