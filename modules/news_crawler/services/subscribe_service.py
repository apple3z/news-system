"""
Subscribe service layer.
Business logic for subscription operations.
Uses proxy for cross-module news keyword search.
"""

from modules.news_crawler.dal import subscribe_dal
from proxy import call as proxy_call


def list_subscriptions(status='all'):
    """List subscriptions with optional status filter."""
    return subscribe_dal.list_subscriptions(status=status)


def get_subscription(sub_id):
    """Get a single subscription."""
    return subscribe_dal.get_subscription(sub_id)


def create_subscription(data):
    """Create a new subscription."""
    return subscribe_dal.create_subscription(data)


def update_subscription(sub_id, data):
    """Update an existing subscription."""
    return subscribe_dal.update_subscription(sub_id, data)


def delete_subscription(sub_id):
    """Delete a subscription and its history."""
    return subscribe_dal.delete_subscription(sub_id)


def toggle_active(sub_id):
    """Toggle subscription active status."""
    return subscribe_dal.toggle_active(sub_id)


def get_history(sub_id, limit=50):
    """Get subscription update history."""
    return subscribe_dal.get_history(sub_id, limit=limit)


def check_keywords(keywords_str):
    """Check news matching keywords via proxy (no direct NEWS_DB import)."""
    keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
    return proxy_call('news.search_by_keywords', keywords=keywords)


def add_subscription_simple(name, url, sub_type='website'):
    """Simple add subscription (public API)."""
    return subscribe_dal.add_subscription_simple(name, url, sub_type)


def delete_subscription_simple(sub_id):
    """Simple delete subscription (public API)."""
    return subscribe_dal.delete_subscription_simple(sub_id)


def get_all_subscriptions_simple():
    """Get all subscriptions for public listing."""
    return subscribe_dal.get_all_subscriptions_simple()


def get_feed_content(page=1, per_page=20, source='', keyword='', time_range='', sort_by='latest'):
    """获取订阅内容列表（公开展示用，支持搜索/时间筛选/排序）"""
    return subscribe_dal.get_feed_content(page, per_page, source, keyword, time_range, sort_by)


def get_active_sources():
    """获取活跃订阅源列表"""
    return subscribe_dal.get_active_sources()


def get_feed_detail(item_id):
    """获取单条订阅内容详情（增强版）"""
    return subscribe_dal.get_feed_detail(item_id)


def get_subscribe_stats():
    """获取订阅统计数据"""
    return subscribe_dal.get_subscribe_stats()


def get_subscriptions_with_count():
    """获取订阅源详情列表（含内容数量）"""
    return subscribe_dal.get_subscriptions_with_count()


def get_sources_with_metadata():
    """获取订阅源列表（含元数据）"""
    return subscribe_dal.get_sources_with_metadata()


def get_digest_feeds(time_range='today', limit=50, source_weights=None):
    """获取摘要内容（含智能排序：源权重 × 时间衰减）"""
    import math
    from datetime import datetime

    feeds = subscribe_dal.get_digest_feeds(time_range, limit)
    if source_weights is None:
        source_weights = {}

    for feed in feeds:
        weight = source_weights.get(str(feed.get('sub_id', '')), 3)
        time_score = _calculate_time_score(feed.get('detected_at', ''))
        feed['source_weight'] = weight
        feed['time_score'] = round(time_score, 4)
        feed['sort_score'] = round(weight * time_score, 4)

    feeds.sort(key=lambda x: x['sort_score'], reverse=True)
    return feeds[:limit]


def _calculate_time_score(date_str):
    """计算时间衰减分数: exp(-hours / 24)"""
    import math
    from datetime import datetime
    if not date_str:
        return 0
    try:
        dt = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
        hours = (datetime.now() - dt).total_seconds() / 3600
        return math.exp(-hours / 24)
    except Exception:
        return 0


def get_source_weights():
    """获取所有源权重设置"""
    return subscribe_dal.get_source_weights()


def set_source_weight(source_id, weight):
    """设置单个源的权重"""
    subscribe_dal.set_source_weight(source_id, weight)


def get_feeds_by_source(per_source=10, time_range=''):
    """按源分组获取内容"""
    return subscribe_dal.get_feeds_by_source(per_source, time_range)
