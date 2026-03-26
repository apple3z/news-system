"""
Semantic API - 语义爬虫REST API

提供语义任务管理、状态查询、结果获取的HTTP接口
"""

from flask import Blueprint, request, jsonify
from utils.auth import login_required

semantic_bp = Blueprint('semantic', __name__, url_prefix='/api/semantic')


def get_engine():
    """获取语义引擎"""
    from modules.semantic.services.semantic_service import SemanticEngine
    return SemanticEngine()


# ===== 任务管理 =====

@semantic_bp.route('/tasks', methods=['GET'])
@login_required
def list_tasks():
    """获取任务列表"""
    engine = get_engine()
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)

    tasks = engine.list_tasks(status, limit)

    return jsonify({
        'code': 200,
        'data': tasks
    })


@semantic_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """创建语义任务"""
    engine = get_engine()
    data = request.get_json()

    if not data or not data.get('user_query'):
        return jsonify({'code': 400, 'message': 'user_query不能为空'})

    task_id = engine.create_task(
        name=data.get('name', data['user_query'][:30]),
        user_query=data['user_query'],
        config=data.get('config', {})
    )

    return jsonify({
        'code': 200,
        'message': '任务创建成功',
        'data': {'task_id': task_id}
    })


@semantic_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """获取任务详情"""
    engine = get_engine()
    task = engine.get_task(task_id)

    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'})

    return jsonify({
        'code': 200,
        'data': task
    })


@semantic_bp.route('/tasks/<int:task_id>/status', methods=['GET'])
@login_required
def get_task_status(task_id):
    """获取任务状态（轮询用）"""
    engine = get_engine()
    task = engine.get_task(task_id)

    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'})

    return jsonify({
        'code': 200,
        'data': {
            'status': task.get('status'),
            'progress': task.get('progress', 0),
            'total_items': task.get('total_items', 0),
            'relevant_items': task.get('relevant_items', 0),
            'error_message': task.get('error_message')
        }
    })


@semantic_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """删除任务"""
    engine = get_engine()
    result = engine.delete_task(task_id)
    return jsonify(result)


@semantic_bp.route('/tasks/<int:task_id>/run', methods=['POST'])
@login_required
def run_task(task_id):
    """手动执行任务"""
    engine = get_engine()
    result = engine.execute_task(task_id, async_mode=True)
    return jsonify(result)


# ===== 结果获取 =====

@semantic_bp.route('/tasks/<int:task_id>/results', methods=['GET'])
@login_required
def get_results(task_id):
    """获取分析结果"""
    engine = get_engine()
    results = engine.get_results(task_id)
    return jsonify({
        'code': 200,
        'data': results
    })


@semantic_bp.route('/tasks/<int:task_id>/sources', methods=['GET'])
@login_required
def get_sources(task_id):
    """获取任务来源列表"""
    engine = get_engine()
    sources = engine.get_sources(task_id)
    return jsonify({
        'code': 200,
        'data': sources
    })


@semantic_bp.route('/tasks/<int:task_id>/items', methods=['GET'])
@login_required
def get_items(task_id):
    """获取采集内容列表"""
    engine = get_engine()
    min_relevance = request.args.get('min_relevance', 0, type=float)
    limit = request.args.get('limit', 100, type=int)

    items = engine.get_items(task_id, min_relevance, limit)
    return jsonify({
        'code': 200,
        'data': items
    })
