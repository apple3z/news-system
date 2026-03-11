#!/usr/bin/env python3
"""
版本管理模块
实现版本号递增、版本历史记录等功能
"""

import os
import json
from datetime import datetime

VERSIONS_FILE = '.versions.json'


def get_versions_file_path():
    """获取版本元数据文件路径"""
    from path_utils import get_project_root
    doc_dir = os.path.join(get_project_root(), 'doc')
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir, exist_ok=True)
    return os.path.join(doc_dir, VERSIONS_FILE)


def load_versions():
    """加载版本元数据"""
    versions_file = get_versions_file_path()
    if os.path.exists(versions_file):
        try:
            with open(versions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_versions(versions):
    """保存版本元数据"""
    versions_file = get_versions_file_path()
    with open(versions_file, 'w', encoding='utf-8') as f:
        json.dump(versions, f, ensure_ascii=False, indent=2)


def get_file_key(path):
    """将路径转换为版本元数据的键"""
    if path.startswith('版本历史/'):
        return path[5:]
    elif path.startswith('文档中心/'):
        return path[5:]
    return path


def increment_version(filename):
    """
    自动递增版本号
    
    Args:
        filename (str): 文件路径（如 '文档中心/研发管理规范.md'）
    
    Returns:
        dict: 版本信息
    """
    versions = load_versions()
    key = get_file_key(filename)
    doc = versions.get(key, {})
    
    # patch +1
    current_patch = doc.get('patch', 0)
    doc['patch'] = current_patch + 1
    
    # 构建新版本号
    major = doc.get('major', 1)
    minor = doc.get('minor', 0)
    patch = doc['patch']
    version = f"{major}.{minor}.{patch}"
    
    # 记录历史
    history = doc.get('history', [])
    history.append({
        'version': version,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action': '更新'
    })
    doc['history'] = history
    
    # 更新时间
    doc['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    versions[key] = doc
    save_versions(versions)
    
    return {
        'code': 200,
        'version': version,
        'major': major,
        'minor': minor,
        'patch': patch,
        'history': history
    }


def get_version_info(filename):
    """获取文档版本信息"""
    versions = load_versions()
    key = get_file_key(filename)
    doc = versions.get(key, {})
    
    major = doc.get('major', 1)
    minor = doc.get('minor', 0)
    patch = doc.get('patch', 0)
    
    return {
        'code': 200,
        'version': f"{major}.{minor}.{patch}",
        'major': major,
        'minor': minor,
        'patch': patch,
        'history': doc.get('history', []),
        'last_update': doc.get('last_update', ''),
        'locked': doc.get('locked', False)
    }


def _resolve_path(path):
    """将逻辑路径解析为物理路径"""
    from path_utils import VERSION_HISTORY_DIR, DOCS_DIR
    if path.startswith('版本历史/'):
        return os.path.join(VERSION_HISTORY_DIR, path[5:])
    elif path.startswith('版本历史'):
        return VERSION_HISTORY_DIR
    elif path.startswith('文档中心/'):
        return os.path.join(DOCS_DIR, path[5:])
    elif path.startswith('文档中心'):
        return DOCS_DIR
    return None


def list_documents(path):
    """列出目录下的文件和子目录"""
    real_path = _resolve_path(path)
    if not real_path or not os.path.exists(real_path):
        return {'code': 200, 'data': []}

    items = []
    for name in sorted(os.listdir(real_path)):
        full = os.path.join(real_path, name)
        if name.startswith('.'):
            continue
        if os.path.isdir(full):
            items.append({'name': name, 'type': 'dir'})
        elif name.endswith('.md'):
            items.append({'name': name, 'type': 'file'})
    return {'code': 200, 'data': items}


def read_document(path):
    """读取文档内容及版本信息"""
    real_path = _resolve_path(path)
    if not real_path or not os.path.exists(real_path):
        return {'code': 404, 'message': '文件不存在'}

    try:
        with open(real_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'code': 500, 'message': str(e)}

    mtime = datetime.fromtimestamp(os.path.getmtime(real_path)).strftime('%Y-%m-%d %H:%M:%S')
    ver = get_version_info(path)
    return {
        'code': 200,
        'content': content,
        'version': ver.get('version', '1.0.0'),
        'mtime': mtime,
        'author': '管理员',
        'history': ver.get('history', [])
    }


def save_document(path, content, author='管理员'):
    """保存文档并递增版本"""
    real_path = _resolve_path(path)
    if not real_path:
        return {'code': 400, 'message': '无效的路径'}

    os.makedirs(os.path.dirname(real_path), exist_ok=True)
    try:
        with open(real_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        return {'code': 500, 'message': str(e)}

    ver = increment_version(path)
    ver['message'] = '保存成功'
    return ver


def create_document(path, content='', author='管理员'):
    """创建新文档"""
    real_path = _resolve_path(path)
    if not real_path:
        return {'code': 400, 'message': '无效的路径'}

    if os.path.exists(real_path):
        return {'code': 400, 'message': '文件已存在'}

    os.makedirs(os.path.dirname(real_path), exist_ok=True)
    try:
        with open(real_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        return {'code': 500, 'message': str(e)}

    ver = increment_version(path)
    ver['message'] = '创建成功'
    return ver


def delete_document(filename):
    """删除文档"""
    from path_utils import VERSION_HISTORY_DIR, DOCS_DIR
    
    if filename.startswith('版本历史/'):
        target_file = os.path.join(VERSION_HISTORY_DIR, filename[5:])
    elif filename.startswith('文档中心/'):
        target_file = os.path.join(DOCS_DIR, filename[5:])
    else:
        return {'code': 400, 'message': '无效的路径'}
    
    if os.path.exists(target_file):
        os.remove(target_file)
        
        # 从版本元数据中删除
        versions = load_versions()
        key = get_file_key(filename)
        if key in versions:
            del versions[key]
            save_versions(versions)
        
        return {'code': 200, 'message': '删除成功'}
    else:
        return {'code': 404, 'message': '文件不存在'}
