"""
Crawl management API routes.
Endpoints: /api/admin/crawl-logs, /api/admin/start-crawl
"""

from flask import jsonify, request
from modules.news_crawler.routes import news_crawler_bp
from modules.news_crawler.services import news_service, crawler_service


@news_crawler_bp.route('/api/admin/crawl-logs')
def api_admin_crawl_logs():
    """Get crawl log entries."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    result = news_service.get_crawl_logs(page=page, per_page=per_page)
    return jsonify({'code': 200, 'message': 'success', 'data': result})


@news_crawler_bp.route('/api/admin/start-crawl', methods=['POST'])
def api_admin_start_crawl():
    """Start the news crawler."""
    try:
        crawler_service.start_news_crawl()
        return jsonify({'code': 200, 'message': 'Crawler started'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})
