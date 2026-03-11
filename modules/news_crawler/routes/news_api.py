"""
News API routes.
Endpoints: /api/news/search, /api/news/categories, /api/news/sources
"""

from flask import jsonify, request
from modules.news_crawler.routes import news_crawler_bp
from modules.news_crawler.services import news_service


@news_crawler_bp.route('/api/news/search')
def api_news_search():
    """News search API with filters, sorting, pagination."""
    result = news_service.search_news(
        keyword=request.args.get('keyword', ''),
        category=request.args.get('category', ''),
        source=request.args.get('source', ''),
        date_from=request.args.get('date_from', ''),
        date_to=request.args.get('date_to', ''),
        sort_by=request.args.get('sort_by', 'time'),
        sort_order=request.args.get('sort_order', 'desc'),
        page=int(request.args.get('page', 1)),
        per_page=int(request.args.get('per_page', 20)),
    )

    filters = {}
    for key in ('keyword', 'category', 'source', 'date_from', 'date_to'):
        val = request.args.get(key, '')
        if val:
            filters[key] = val
    sort_by = request.args.get('sort_by', 'time')
    sort_order = request.args.get('sort_order', 'desc')
    if sort_by != 'time':
        filters['sort_by'] = sort_by
    if sort_order != 'desc':
        filters['sort_order'] = sort_order

    resp = {
        'code': 200,
        'data': result['data'],
        'total': result['total'],
        'page': int(request.args.get('page', 1)),
        'per_page': int(request.args.get('per_page', 20)),
    }
    if filters:
        resp['filters'] = filters

    return jsonify(resp)


@news_crawler_bp.route('/api/news/categories')
def api_news_categories():
    """Get news category list."""
    categories = news_service.get_categories()
    return jsonify({'code': 200, 'data': categories})


@news_crawler_bp.route('/api/news/sources')
def api_news_sources():
    """Get news source list."""
    sources = news_service.get_sources()
    return jsonify({'code': 200, 'data': sources})
