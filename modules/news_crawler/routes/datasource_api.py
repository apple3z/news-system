"""
数据源管理与统一采集API路由层
"""

from flask import request, jsonify
from modules.news_crawler.routes import news_crawler_bp
from modules.news_crawler.services import datasource_service, crawler_service, news_service
from utils.auth import login_required


# ========== 数据源 CRUD ==========

@news_crawler_bp.route('/api/admin/datasources', methods=['GET'])
@login_required
def api_list_sources():
    source_type = request.args.get('type')
    status = request.args.get('status')
    result = datasource_service.get_sources(source_type, status)
    return jsonify(result)


@news_crawler_bp.route('/api/admin/datasources', methods=['POST'])
@login_required
def api_create_source():
    data = request.get_json() or {}
    result = datasource_service.add_source(data)
    return jsonify(result)


@news_crawler_bp.route('/api/admin/datasources/<int:source_id>', methods=['GET'])
@login_required
def api_get_source(source_id):
    result = datasource_service.get_source_detail(source_id)
    return jsonify(result)


@news_crawler_bp.route('/api/admin/datasources/<int:source_id>', methods=['PUT'])
@login_required
def api_update_source(source_id):
    data = request.get_json() or {}
    result = datasource_service.modify_source(source_id, data)
    return jsonify(result)


@news_crawler_bp.route('/api/admin/datasources/<int:source_id>', methods=['DELETE'])
@login_required
def api_delete_source(source_id):
    result = datasource_service.remove_source(source_id)
    return jsonify(result)


@news_crawler_bp.route('/api/admin/datasources/<int:source_id>/toggle', methods=['PUT'])
@login_required
def api_toggle_source(source_id):
    result = datasource_service.toggle_source_status(source_id)
    return jsonify(result)


# ========== 数据源统计 ==========

@news_crawler_bp.route('/api/admin/datasources/stats', methods=['GET'])
@login_required
def api_source_stats():
    result = datasource_service.get_stats()
    return jsonify(result)


# ========== 统一采集 ==========

@news_crawler_bp.route('/api/admin/crawl/start', methods=['POST'])
@login_required
def api_start_crawl():
    """统一采集入口"""
    data = request.get_json() or {}
    crawl_type = data.get('type', 'full')  # full / news / skill / rss
    result = crawler_service.start_unified_crawl(crawl_type)
    return jsonify(result)


# ========== 采集日志 ==========

@news_crawler_bp.route('/api/admin/crawl/logs', methods=['GET'])
@login_required
def api_crawl_logs():
    log_type = request.args.get('type')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    result = datasource_service.get_crawl_log_list(log_type, page, per_page)
    return jsonify(result)


# ========== 数据统计 ==========

@news_crawler_bp.route('/api/admin/stats/daily', methods=['GET'])
@login_required
def api_daily_stats():
    """获取每日数据统计，按3种源类型分组（新闻源/RSS源/Skill源）"""
    days = int(request.args.get('days', 30))
    # 按类型分组的新闻+RSS统计
    type_stats = news_service.get_daily_stats_by_type(days)
    # Skills每日统计
    from modules.news_crawler.dal import skills_dal
    skill_stats = skills_dal.get_daily_stats(days)
    return jsonify({'code': 200, 'data': {
        'news': type_stats.get('news', []),
        'rss': type_stats.get('rss', []),
        'skill': skill_stats
    }})
