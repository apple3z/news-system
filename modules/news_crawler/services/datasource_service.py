"""
数据源管理业务逻辑层
"""

from modules.news_crawler.dal.datasource_dal import (
    list_sources, get_source, create_source, update_source,
    delete_source, toggle_source, get_source_counts,
    list_crawl_logs
)


def get_sources(source_type=None, status=None):
    """获取数据源列表"""
    sources = list_sources(source_type, status)
    return {'code': 200, 'data': sources}


def get_source_detail(source_id):
    """获取数据源详情"""
    source = get_source(source_id)
    if not source:
        return {'code': 404, 'message': '数据源不存在'}
    return {'code': 200, 'data': source}


def add_source(data):
    """新增数据源"""
    if not data.get('name') or not data.get('url') or not data.get('type'):
        return {'code': 400, 'message': '名称、类型和URL不能为空'}
    if data['type'] not in ('news', 'skill', 'rss'):
        return {'code': 400, 'message': '类型必须为 news/skill/rss'}
    return create_source(data)


def modify_source(source_id, data):
    """修改数据源"""
    if 'type' in data and data['type'] not in ('news', 'skill', 'rss'):
        return {'code': 400, 'message': '类型必须为 news/skill/rss'}
    return update_source(source_id, data)


def remove_source(source_id):
    """删除数据源"""
    return delete_source(source_id)


def toggle_source_status(source_id):
    """切换数据源状态"""
    return toggle_source(source_id)


def get_stats():
    """获取数据源统计"""
    counts = get_source_counts()
    return {
        'code': 200,
        'data': {
            'news': counts.get('news', 0),
            'skill': counts.get('skill', 0),
            'rss': counts.get('rss', 0),
            'total': sum(counts.values())
        }
    }


def get_crawl_log_list(log_type=None, page=1, per_page=20):
    """获取采集日志"""
    result = list_crawl_logs(log_type, page, per_page)
    return {'code': 200, **result}
