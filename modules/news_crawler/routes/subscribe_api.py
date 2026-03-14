"""
Subscribe API routes.
Public: /api/subscribe (POST, DELETE), /api/subscribe/check, /api/subscribe/feed, /api/subscribe/sources
Admin: /api/admin/subscriptions CRUD, toggle, history, check-all
"""

from flask import jsonify, request
from modules.news_crawler.routes import news_crawler_bp
from modules.news_crawler.services import subscribe_service
from utils.auth import login_required


# ========== Public Subscribe API ==========

@news_crawler_bp.route('/api/subscribe', methods=['POST'])
def api_subscribe_add():
    """Add a subscription (public)."""
    data = request.json
    sub_id = subscribe_service.add_subscription_simple(
        name=data.get('name', ''),
        url=data.get('url', ''),
        sub_type=data.get('sub_type', 'website'),
    )
    return jsonify({'code': 200, 'message': 'Added', 'id': sub_id})


@news_crawler_bp.route('/api/subscribe/<int:sub_id>', methods=['DELETE'])
def api_subscribe_delete(sub_id):
    """Delete a subscription (public)."""
    subscribe_service.delete_subscription_simple(sub_id)
    return jsonify({'code': 200, 'message': 'Deleted'})


@news_crawler_bp.route('/api/subscribe/check', methods=['POST'])
def api_subscribe_check():
    """Check subscribed keywords against news (public)."""
    data = request.json
    keywords_str = data.get('keywords', '')
    news_list = subscribe_service.check_keywords(keywords_str)
    return jsonify({'code': 200, 'data': news_list})


@news_crawler_bp.route('/api/subscribe/feed', methods=['GET'])
def api_subscribe_feed():
    """获取订阅内容列表（公开API，支持搜索/时间筛选/排序）"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    source = request.args.get('source', '')
    keyword = request.args.get('keyword', '')
    time_range = request.args.get('time_range', '')
    sort_by = request.args.get('sort_by', 'latest')
    result = subscribe_service.get_feed_content(page, per_page, source, keyword, time_range, sort_by)
    return jsonify({'code': 200, **result})


@news_crawler_bp.route('/api/subscribe/sources', methods=['GET'])
def api_subscribe_sources():
    """获取活跃订阅源列表（公开API，用于前台筛选下拉框）"""
    result = subscribe_service.get_active_sources()
    return jsonify({'code': 200, 'data': result})


@news_crawler_bp.route('/api/subscribe/stats', methods=['GET'])
def api_subscribe_stats():
    """获取订阅统计数据（公开API）"""
    result = subscribe_service.get_subscribe_stats()
    return jsonify({'code': 200, 'data': result})


@news_crawler_bp.route('/api/subscribe/subscriptions', methods=['GET'])
def api_subscribe_subscriptions():
    """获取订阅源详情列表（公开API，含每个源的内容数量）"""
    result = subscribe_service.get_subscriptions_with_count()
    return jsonify({'code': 200, 'data': result})


@news_crawler_bp.route('/api/subscribe/<int:item_id>', methods=['GET'])
def api_subscribe_detail(item_id):
    """获取单条订阅内容详情（增强版：含parsed_content/thumbnail/author）"""
    result = subscribe_service.get_feed_detail(item_id)
    if result:
        return jsonify({'code': 200, 'data': result})
    return jsonify({'code': 404, 'message': '内容不存在'})


@news_crawler_bp.route('/api/subscribe/sources-meta', methods=['GET'])
def api_subscribe_sources_meta():
    """获取订阅源列表（增强版：含id/url/sub_type/feed_count元数据）"""
    result = subscribe_service.get_sources_with_metadata()
    return jsonify({'code': 200, 'data': result})


@news_crawler_bp.route('/api/subscribe/digest', methods=['GET'])
def api_subscribe_digest():
    """获取摘要内容（智能排序：源权重 × 时间衰减）"""
    time_range = request.args.get('time_range', 'today')
    limit = int(request.args.get('limit', 50))
    # 从数据库获取源权重
    source_weights = subscribe_service.get_source_weights()
    feeds = subscribe_service.get_digest_feeds(time_range, limit, source_weights)
    # 统计
    stats = subscribe_service.get_subscribe_stats()
    return jsonify({
        'code': 200,
        'data': {
            'stats': stats,
            'feeds': feeds
        }
    })


@news_crawler_bp.route('/api/subscribe/source-weights', methods=['GET'])
def api_subscribe_get_weights():
    """获取所有源优先级设置"""
    weights = subscribe_service.get_source_weights()
    return jsonify({'code': 200, 'data': weights})


@news_crawler_bp.route('/api/subscribe/source-weights', methods=['POST'])
def api_subscribe_set_weight():
    """设置单个源优先级（1-5星）"""
    data = request.get_json()
    source_id = data.get('source_id')
    weight = data.get('weight', 3)
    if source_id is None:
        return jsonify({'code': 400, 'message': 'source_id required'})
    subscribe_service.set_source_weight(int(source_id), int(weight))
    return jsonify({'code': 200, 'message': '设置成功'})


@news_crawler_bp.route('/api/subscribe/by-source', methods=['GET'])
def api_subscribe_by_source():
    """按源分组获取内容"""
    per_source = int(request.args.get('per_source', 10))
    time_range = request.args.get('time_range', '')
    result = subscribe_service.get_feeds_by_source(per_source, time_range)
    return jsonify({'code': 200, 'data': result})


# ========== Admin Subscriptions API ==========

@news_crawler_bp.route('/api/admin/subscriptions')
@login_required
def api_admin_subscriptions_list():
    """Get subscription list (admin)."""
    status = request.args.get('status', 'all')
    result = subscribe_service.list_subscriptions(status=status)
    return jsonify({'code': 200, **result})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>')
@login_required
def api_admin_subscriptions_get(sub_id):
    """Get single subscription detail."""
    sub = subscribe_service.get_subscription(sub_id)
    if not sub:
        return jsonify({'code': 404, 'message': 'Subscription not found'})
    return jsonify({'code': 200, 'data': sub})


@news_crawler_bp.route('/api/admin/subscriptions', methods=['POST'])
@login_required
def api_admin_subscriptions_create():
    """Create a new subscription (admin)."""
    data = request.get_json()
    name = data.get('name', '').strip()
    url = data.get('url', '').strip()
    if not name or not url:
        return jsonify({'code': 400, 'message': 'Name and URL required'})

    new_id = subscribe_service.create_subscription(data)
    return jsonify({'code': 200, 'message': 'Created', 'id': new_id})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>', methods=['PUT'])
@login_required
def api_admin_subscriptions_update(sub_id):
    """Update an existing subscription."""
    data = request.get_json()
    found = subscribe_service.update_subscription(sub_id, data)
    if not found:
        return jsonify({'code': 404, 'message': 'Subscription not found'})
    return jsonify({'code': 200, 'message': 'Updated'})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>', methods=['DELETE'])
@login_required
def api_admin_subscriptions_delete(sub_id):
    """Delete a subscription."""
    subscribe_service.delete_subscription(sub_id)
    return jsonify({'code': 200, 'message': 'Deleted'})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>/toggle', methods=['PUT'])
@login_required
def api_admin_subscriptions_toggle(sub_id):
    """Toggle subscription active/inactive."""
    new_status = subscribe_service.toggle_active(sub_id)
    if new_status is None:
        return jsonify({'code': 404, 'message': 'Subscription not found'})
    return jsonify({'code': 200, 'message': 'Status updated', 'is_active': new_status})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>/history')
@login_required
def api_admin_subscriptions_history(sub_id):
    """Get subscription update history."""
    rows = subscribe_service.get_history(sub_id)
    return jsonify({'code': 200, 'data': rows})


@news_crawler_bp.route('/api/admin/subscriptions/check-all', methods=['POST'])
@login_required
def api_admin_subscriptions_check_all():
    """Trigger check for all subscriptions."""
    try:
        import sys
        import os
        from threading import Thread
        from config import PROJECT_ROOT

        def run_check():
            try:
                if PROJECT_ROOT not in sys.path:
                    sys.path.insert(0, PROJECT_ROOT)
                from subscribe_manager import check_all_subscriptions
                check_all_subscriptions()
            except Exception as e:
                print(f"Subscription check failed: {e}")

        thread = Thread(target=run_check, daemon=True)
        thread.start()
        return jsonify({'code': 200, 'message': 'Check started'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})
