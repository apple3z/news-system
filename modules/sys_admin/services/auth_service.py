"""
账户管理业务逻辑层
"""

from modules.sys_admin.dal.auth_dal import (
    verify_login, list_users, get_user,
    create_user, update_user, reset_password, delete_user
)


def login(username, password):
    """登录验证"""
    if not username or not password:
        return {'code': 400, 'message': '用户名和密码不能为空'}
    user = verify_login(username, password)
    if not user:
        return {'code': 401, 'message': '用户名或密码错误'}
    return {
        'code': 200,
        'message': '登录成功',
        'data': {
            'id': user['id'],
            'username': user['username'],
            'display_name': user['display_name'],
            'role': user['role']
        }
    }


def get_all_users():
    """获取所有用户"""
    return {'code': 200, 'data': list_users()}


def get_user_detail(user_id):
    """获取用户详情"""
    user = get_user(user_id)
    if not user:
        return {'code': 404, 'message': '用户不存在'}
    return {'code': 200, 'data': user}


def add_user(username, password, display_name='', role='admin'):
    """新增用户"""
    if not username or not password:
        return {'code': 400, 'message': '用户名和密码不能为空'}
    if len(password) < 6:
        return {'code': 400, 'message': '密码长度至少6位'}
    if role not in ('admin', 'super_admin'):
        return {'code': 400, 'message': '角色无效'}
    return create_user(username, password, display_name, role)


def modify_user(user_id, data):
    """修改用户"""
    return update_user(user_id, data)


def change_password(user_id, new_password):
    """修改密码"""
    if not new_password or len(new_password) < 6:
        return {'code': 400, 'message': '密码长度至少6位'}
    return reset_password(user_id, new_password)


def remove_user(user_id):
    """删除用户"""
    return delete_user(user_id)
