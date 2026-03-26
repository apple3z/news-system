"""
Kernel API - 爬虫内核REST API

提供任务管理、执行控制、状态监控的HTTP接口
"""

import json
from flask import Blueprint, request, jsonify
from modules.news_crawler.kernel.core import CrawlerKernel, TaskStatus
from utils.auth import login_required

kernel_bp = Blueprint('kernel', __name__, url_prefix='/api/admin/kernel')


def get_kernel():
    """获取内核单例"""
    return CrawlerKernel()


# ===== 任务管理 =====

@kernel_bp.route('/tasks', methods=['GET'])
@login_required
def list_tasks():
    """获取任务列表"""
    kernel = get_kernel()

    task_type = request.args.get('type')
    status = request.args.get('status')

    tasks = kernel.list_tasks(task_type, status)

    return jsonify({
        'code': 200,
        'data': tasks
    })


@kernel_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """创建任务"""
    kernel = get_kernel()

    data = request.get_json()

    result = kernel.create_task({
        'name': data.get('name', ''),
        'task_type': data.get('task_type', 'news'),
        'trigger_type': data.get('trigger_type', 'manual'),
        'trigger_config': json.loads(data.get('trigger_config', '{}')) if isinstance(data.get('trigger_config'), str) else data.get('trigger_config', {}),
        'source_filter': json.loads(data.get('source_filter', '[]')) if isinstance(data.get('source_filter'), str) else data.get('source_filter', []),
        'pipeline': json.loads(data.get('pipeline', '["fetch","parse","store"]')) if isinstance(data.get('pipeline'), str) else data.get('pipeline', ['fetch', 'parse', 'store']),
        'config': json.loads(data.get('config', '{}')) if isinstance(data.get('config'), str) else data.get('config', {}),
        'enabled': data.get('enabled', True)
    })

    return jsonify(result)


@kernel_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """获取单个任务"""
    kernel = get_kernel()

    task = kernel.get_task(task_id)
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'})

    return jsonify({
        'code': 200,
        'data': task
    })


@kernel_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """更新任务"""
    kernel = get_kernel()

    data = request.get_json()

    result = kernel.update_task(task_id, {
        'name': data.get('name'),
        'task_type': data.get('task_type'),
        'trigger_type': data.get('trigger_type'),
        'trigger_config': json.loads(data.get('trigger_config', '{}')) if isinstance(data.get('trigger_config'), str) else data.get('trigger_config', {}),
        'source_filter': json.loads(data.get('source_filter', '[]')) if isinstance(data.get('source_filter'), str) else data.get('source_filter', []),
        'pipeline': json.loads(data.get('pipeline', '["fetch","parse","store"]')) if isinstance(data.get('pipeline'), str) else data.get('pipeline', ['fetch', 'parse', 'store']),
        'config': json.loads(data.get('config', '{}')) if isinstance(data.get('config'), str) else data.get('config', {}),
        'enabled': data.get('enabled', True)
    })

    return jsonify(result)


@kernel_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """删除任务"""
    kernel = get_kernel()

    result = kernel.delete_task(task_id)
    return jsonify(result)


@kernel_bp.route('/tasks/<int:task_id>/toggle', methods=['PUT'])
@login_required
def toggle_task(task_id):
    """暂停/恢复任务"""
    kernel = get_kernel()

    result = kernel.toggle_task(task_id)
    return jsonify(result)


@kernel_bp.route('/tasks/<int:task_id>/run', methods=['POST'])
@login_required
def run_task(task_id):
    """手动执行任务"""
    kernel = get_kernel()

    result = kernel.execute_task(task_id, async_mode=True)
    return jsonify(result)


# ===== 执行记录 =====

@kernel_bp.route('/executions', methods=['GET'])
@login_required
def list_executions():
    """获取执行记录"""
    kernel = get_kernel()

    task_id = request.args.get('task_id', type=int)
    limit = request.args.get('limit', 100, type=int)

    if task_id:
        executions = kernel.get_task_executions(task_id, limit)
    else:
        executions = kernel.get_recent_executions(limit)

    return jsonify({
        'code': 200,
        'data': executions
    })


# ===== 状态监控 =====

@kernel_bp.route('/status', methods=['GET'])
@login_required
def get_status():
    """获取内核状态"""
    kernel = get_kernel()

    stats = kernel.get_stats()
    running = kernel.get_running_tasks()

    return jsonify({
        'code': 200,
        'data': {
            'stats': stats,
            'running': running
        }
    })


# ===== 调度任务（调度器触发） =====

@kernel_bp.route('/schedule/add', methods=['POST'])
@login_required
def add_schedule():
    """手动添加调度任务"""
    kernel = get_kernel()

    data = request.get_json()
    task_id = data.get('task_id')

    if not task_id:
        return jsonify({'code': 400, 'message': 'task_id不能为空'})

    task = kernel.get_task(task_id)
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'})

    from modules.news_crawler.kernel.core import TriggerType

    if task['trigger_type'] == TriggerType.INTERVAL:
        seconds = task.get('trigger_config', {}).get('seconds', 3600)
        kernel._scheduler.add_interval_job(task_id, seconds)
    elif task['trigger_type'] == TriggerType.CRON:
        hour = task.get('trigger_config', {}).get('hour', 9)
        minute = task.get('trigger_config', {}).get('minute', 0)
        kernel._scheduler.add_cron_job(task_id, hour, minute)
    else:
        return jsonify({'code': 400, 'message': '任务不是定时类型'})

    return jsonify({'code': 200, 'message': '调度任务已添加'})
