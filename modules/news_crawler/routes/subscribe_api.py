"""
Subscribe API routes.
Public: /api/subscribe (POST, DELETE), /api/subscribe/check
Admin: /api/admin/subscriptions CRUD, toggle, history, check-all
"""

from flask import jsonify, request
from modules.news_crawler.routes import news_crawler_bp
from modules.news_crawler.services import subscribe_service


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


# ========== Admin Subscriptions API ==========

@news_crawler_bp.route('/api/admin/subscriptions')
def api_admin_subscriptions_list():
    """Get subscription list (admin)."""
    status = request.args.get('status', 'all')
    result = subscribe_service.list_subscriptions(status=status)
    return jsonify({'code': 200, **result})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>')
def api_admin_subscriptions_get(sub_id):
    """Get single subscription detail."""
    sub = subscribe_service.get_subscription(sub_id)
    if not sub:
        return jsonify({'code': 404, 'message': 'Subscription not found'})
    return jsonify({'code': 200, 'data': sub})


@news_crawler_bp.route('/api/admin/subscriptions', methods=['POST'])
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
def api_admin_subscriptions_update(sub_id):
    """Update an existing subscription."""
    data = request.get_json()
    found = subscribe_service.update_subscription(sub_id, data)
    if not found:
        return jsonify({'code': 404, 'message': 'Subscription not found'})
    return jsonify({'code': 200, 'message': 'Updated'})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>', methods=['DELETE'])
def api_admin_subscriptions_delete(sub_id):
    """Delete a subscription."""
    subscribe_service.delete_subscription(sub_id)
    return jsonify({'code': 200, 'message': 'Deleted'})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>/toggle', methods=['PUT'])
def api_admin_subscriptions_toggle(sub_id):
    """Toggle subscription active/inactive."""
    new_status = subscribe_service.toggle_active(sub_id)
    if new_status is None:
        return jsonify({'code': 404, 'message': 'Subscription not found'})
    return jsonify({'code': 200, 'message': 'Status updated', 'is_active': new_status})


@news_crawler_bp.route('/api/admin/subscriptions/<int:sub_id>/history')
def api_admin_subscriptions_history(sub_id):
    """Get subscription update history."""
    rows = subscribe_service.get_history(sub_id)
    return jsonify({'code': 200, 'data': rows})


@news_crawler_bp.route('/api/admin/subscriptions/check-all', methods=['POST'])
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
