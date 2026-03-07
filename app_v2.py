#!/usr/bin/env python3
"""
Web服务 v2.5 - newsystem v2 模式
只包含 v2 API 和新版系统管理页面
"""

from flask import Flask, render_template, jsonify, request
import os
import sys

# 添加 utils 路径
sys.path.insert(0, '/home/zhang/.copaw/news_system')
from utils.version_manager import (
    get_sorted_versions,
    scan_version_docs,
    get_doc_version,
    save_doc_with_version,
    validate_doc_path
)

app = Flask(__name__, 
            template_folder='/home/zhang/.copaw/news_system/templates',
            static_folder='/home/zhang/.copaw/news_system/static',
            static_url_path='/static')

BASE_DIR = '/home/zhang/.copaw/news_system'
VERSION_MANAGE_DIR = os.path.join(BASE_DIR, '版本管理')
RESEARCH_SPEC_DIR = os.path.join(BASE_DIR, '研发规范')


# ========== API v2 路由 ==========

@app.route('/api/v2/versions')
def api_v2_versions():
    """获取版本列表（倒序）"""
    try:
        versions = get_sorted_versions(VERSION_MANAGE_DIR)
        
        data = []
        for v in versions:
            docs = scan_version_docs(v, VERSION_MANAGE_DIR)
            data.append({
                'version': v,
                'path': f'版本管理/{v}',
                'docs': docs
            })
        
        return jsonify({'code': 200, 'data': data})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)}), 500


@app.route('/api/v2/wiki/read/<path:filepath>')
def api_v2_wiki_read(filepath):
    """读取文档内容和版本信息"""
    # 安全验证
    is_valid, error_msg = validate_doc_path(filepath)
    if not is_valid:
        return jsonify({'code': 400, 'msg': error_msg}), 400
    
    full_path = os.path.join(BASE_DIR, filepath)
    
    if not os.path.exists(full_path):
        return jsonify({'code': 404, 'msg': '文件不存在'}), 404
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        version_info = get_doc_version(filepath, BASE_DIR)
        
        return jsonify({
            'code': 200,
            'content': content,
            'version': version_info['version'],
            'mtime': version_info['mtime'],
            'locked': version_info['locked']
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)}), 500


@app.route('/api/v2/wiki/save', methods=['POST'])
def api_v2_wiki_save():
    """保存文档并更新版本"""
    data = request.get_json()
    
    if not data:
        return jsonify({'code': 400, 'msg': '请求体为空'}), 400
    
    filepath = data.get('filepath')
    content = data.get('content')
    locked = data.get('locked')
    
    if not filepath or content is None:
        return jsonify({'code': 400, 'msg': '缺少filepath或content'}), 400
    
    # 安全验证
    is_valid, error_msg = validate_doc_path(filepath)
    if not is_valid:
        return jsonify({'code': 400, 'msg': error_msg}), 400
    
    # 保存文档
    result = save_doc_with_version(filepath, content, BASE_DIR, locked)
    
    return jsonify(result)


# ========== 页面路由 ==========

@app.route('/')
def index():
    """首页重定向到 sys_v2"""
    return render_template('index.html')


@app.route('/sys_v2')
def sys_v2_page():
    """新版系统管理页面"""
    return render_template('sys_v2.html')


@app.route('/sys')
def sys_page_redirect():
    """旧版 /sys 重定向到新版 /sys_v2"""
    return """<!DOCTYPE html><html><head><meta charset="utf-8">
    <script>window.location.href = '/sys_v2';</script>
    </head><body>正在跳转到新版系统管理...</body></html>"""


@app.route('/static/<path:filename>')
def serve_static(filename):
    """静态文件路由"""
    from flask import send_from_directory
    return send_from_directory(app.static_folder, filename)


# ========== 启动服务 ==========

if __name__ == "__main__":
    print("="*50)
    print("Web服务 v2.5 (新版) 启动!")
    print("系统管理: http://localhost:5001/sys_v2")
    print("="*50)
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
