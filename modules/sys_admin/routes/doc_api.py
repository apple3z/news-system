"""
Document management API routes.
Endpoints: /api/v2/doc/list, /api/v2/doc/read, /api/v2/doc/save, /api/v2/doc/delete, /api/v2/doc/create
"""

from flask import jsonify, request
from modules.sys_admin.routes import sys_admin_bp
from modules.sys_admin.services import doc_service
from utils.auth import login_required


@sys_admin_bp.route('/api/v2/doc/list')
@login_required
def api_v2_doc_list():
    """List documents in a directory."""
    path = request.args.get('path', '')
    result = doc_service.list_documents(path)
    return jsonify(result)


@sys_admin_bp.route('/api/v2/doc/read')
@login_required
def api_v2_doc_read():
    """Read document content."""
    path = request.args.get('path', '')
    result = doc_service.read_document(path)
    return jsonify(result)


@sys_admin_bp.route('/api/v2/doc/save', methods=['POST'])
@login_required
def api_v2_doc_save():
    """Save document with version management."""
    data = request.get_json()
    path = data.get('path')
    content = data.get('content', '')
    author = data.get('author', '管理员')

    if not path:
        return jsonify({'code': 400, 'message': 'Missing path parameter'})

    result = doc_service.save_document(path, content, author)
    return jsonify(result)


@sys_admin_bp.route('/api/v2/doc/delete', methods=['POST'])
@login_required
def api_v2_doc_delete():
    """Delete a document."""
    data = request.get_json()
    path = data.get('path')

    if not path:
        return jsonify({'code': 400, 'message': 'Missing path parameter'})

    result = doc_service.delete_document(path)
    return jsonify(result)


@sys_admin_bp.route('/api/v2/doc/create', methods=['POST'])
@login_required
def api_v2_doc_create():
    """Create a new document."""
    data = request.get_json()
    path = data.get('path')
    content = data.get('content', '')
    author = data.get('author', '管理员')

    if not path:
        return jsonify({'code': 400, 'message': 'Missing path parameter'})

    result = doc_service.create_document(path, content, author)
    return jsonify(result)
