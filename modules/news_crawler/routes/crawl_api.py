"""
Crawl management API routes (legacy).
Endpoints: /api/admin/crawl-logs, /api/admin/start-crawl
Note: New unified crawl endpoints are in datasource_api.py
"""

from flask import jsonify, request
from modules.news_crawler.routes import news_crawler_bp
from modules.news_crawler.services import news_service, crawler_service
from utils.auth import login_required


@news_crawler_bp.route('/api/admin/crawl-logs')
@login_required
def api_admin_crawl_logs():
    """Get crawl log entries."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    result = news_service.get_crawl_logs(page=page, per_page=per_page)
    return jsonify({'code': 200, 'message': 'success', 'data': result})


@news_crawler_bp.route('/api/admin/start-crawl', methods=['POST'])
@login_required
def api_admin_start_crawl():
    """Start unified crawler (supports type parameter)."""
    data = request.get_json() or {}
    crawl_type = data.get('type', 'full')
    result = crawler_service.start_unified_crawl(crawl_type)
    return jsonify(result)
