# 统一版本管理模块 v1.0
# 用于 newsystem v2.5.0 "稳定之基" 版本

import os
import json
import re
from datetime import datetime
from functools import cmp_to_key

VERSIONS_FILE = ".versions.json"


def parse_version(version_str):
    """
    解析版本号字符串为可比较的元组
    
    Args:
        version_str: 如 "v2.5.0" 或 "2.5.0" 或 "1.0.5"
    
    Returns:
        tuple: (major, minor, patch)
    """
    clean = version_str.lstrip('v')
    parts = clean.split('.')
    return tuple(int(p) for p in parts[:3])


def compare_versions(v1, v2):
    """
    比较两个版本号
    
    Returns:
        >0: v1 > v2
        <0: v1 < v2
        =0: v1 = v2
    """
    p1 = parse_version(v1)
    p2 = parse_version(v2)
    
    for a, b in zip(p1, p2):
        if a != b:
            return a - b
    return len(p1) - len(p2)


def get_sorted_versions(base_dir='版本管理'):
    """
    获取按版本号倒序排列的版本列表
    
    Args:
        base_dir: 版本根目录路径
    
    Returns:
        list: ['v2.6.0', 'v2.5.0', 'v2.4.0', ...]
    """
    versions = []
    
    if not os.path.exists(base_dir):
        return versions
    
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if os.path.isdir(path):
            # 匹配版本号格式: v2.5.0 或 2.5.0
            if re.match(r'^v?\d+\.\d+(\.\d+)?$', name):
                versions.append(name)
    
    # 使用自定义比较函数排序（倒序）
    return sorted(versions, 
                  key=cmp_to_key(compare_versions), 
                  reverse=True)


def load_versions_meta(base_dir='.'):
    """
    加载版本元数据
    
    Args:
        base_dir: 基础目录
    
    Returns:
        dict: 版本元数据字典
    """
    meta_path = os.path.join(base_dir, VERSIONS_FILE)
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_versions_meta(meta, base_dir='.'):
    """
    保存版本元数据
    
    Args:
        meta: 版本元数据字典
        base_dir: 基础目录
    """
    meta_path = os.path.join(base_dir, VERSIONS_FILE)
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def get_doc_version(filepath, base_dir='.'):
    """
    获取文档版本信息（统一函数）
    
    Args:
        filepath: 文档相对路径，如 "版本管理/v2.5.0/02-需求.md"
        base_dir: 基础目录
    
    Returns:
        {
            'version': '1.0.5',
            'mtime': '2026-03-06 14:30:00',
            'history': [{'version': '1.0.1', 'time': '...', 'action': '...'}],
            'locked': False,
            'last_update': '2026-03-06 14:30:00'
        }
    """
    full_path = os.path.join(base_dir, filepath)
    
    # 获取文件实际修改时间
    mtime = os.path.getmtime(full_path) if os.path.exists(full_path) else 0
    mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    # 加载版本元数据
    meta = load_versions_meta(base_dir)
    doc_meta = meta.get(filepath, {})
    
    return {
        'version': f"{doc_meta.get('major', 1)}.{doc_meta.get('minor', 0)}.{doc_meta.get('patch', 0)}",
        'mtime': mtime_str,
        'history': doc_meta.get('history', []),
        'locked': doc_meta.get('locked', False),
        'last_update': doc_meta.get('last_update', mtime_str)
    }


def save_doc_with_version(filepath, content, base_dir='.', locked=None):
    """
    保存文档并自动更新版本（统一函数）
    
    Args:
        filepath: 文档路径
        content: 文档内容
        base_dir: 基础目录
        locked: 是否锁定（None表示保持原状态）
    
    Returns:
        {'code': 200, 'version': '1.0.6', 'msg': '保存成功'}
    """
    full_path = os.path.join(base_dir, filepath)
    
    # 确保目录存在
    dir_path = os.path.dirname(full_path)
    os.makedirs(dir_path, exist_ok=True)
    
    try:
        # 写入文件（同步）
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新版本元数据
        meta = load_versions_meta(base_dir)
        
        if filepath not in meta:
            meta[filepath] = {
                'major': 1,
                'minor': 0,
                'patch': 0,
                'history': [],
                'locked': False
            }
        
        doc = meta[filepath]
        
        # 检查锁定状态
        if doc.get('locked') and locked is None:
            return {'code': 403, 'msg': '文档已锁定，无法修改'}
        
        # 递增版本号（修订号）
        doc['patch'] = doc.get('patch', 0) + 1
        
        # 记录历史
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history = doc.get('history', [])
        history.append({
            'version': f"{doc['major']}.{doc['minor']}.{doc['patch']}",
            'time': now,
            'action': '更新'
        })
        doc['history'] = history[-20:]  # 只保留最近20条
        
        # 更新时间
        doc['last_update'] = now
        
        # 更新锁定状态
        if locked is not None:
            doc['locked'] = locked
        
        # 保存元数据
        save_versions_meta(meta, base_dir)
        
        return {
            'code': 200, 
            'version': f"{doc['major']}.{doc['minor']}.{doc['patch']}",
            'msg': '保存成功'
        }
        
    except Exception as e:
        return {'code': 500, 'msg': f'保存失败: {str(e)}'}


def validate_doc_path(filepath):
    """
    验证文档路径安全性
    
    Args:
        filepath: 路径字符串
    
    Returns:
        tuple: (is_valid, error_msg)
    """
    # 禁止路径遍历
    if '..' in filepath:
        return False, '路径包含非法字符'
    
    # 禁止绝对路径
    if filepath.startswith('/'):
        return False, '不允许绝对路径'
    
    # 只允许特定目录
    allowed = ['版本管理/', '版本历史/', '文档中心/', 'docs/', '研发规范/']
    if not any(filepath.startswith(p) for p in allowed):
        return False, '不允许访问该目录'
    
    return True, None


def scan_version_docs(version_name, base_dir='版本管理'):
    """
    扫描版本下的文档列表（每次重新扫描，无缓存）
    
    Args:
        version_name: 版本名称，如 "v2.5.0"
        base_dir: 版本根目录
    
    Returns:
        list: [{'name': '02-需求.md', 'size': 1234, 'mtime': '...'}, ...]
    """
    version_path = os.path.join(base_dir, version_name)
    
    if not os.path.exists(version_path):
        return []
    
    docs = []
    for name in os.listdir(version_path):
        if name.endswith('.md'):
            path = os.path.join(version_path, name)
            mtime = os.path.getmtime(path)
            docs.append({
                'name': name,
                'size': os.path.getsize(path),
                'mtime': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # 按文件名排序
    docs.sort(key=lambda x: x['name'])
    return docs
