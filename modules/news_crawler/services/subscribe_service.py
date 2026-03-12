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


def get_feed_content(page=1, per_page=20, source=''):
    """获取订阅内容列表（公开展示用）"""
    return subscribe_dal.get_feed_content(page, per_page, source)


def get_active_sources():
    """获取活跃订阅源列表"""
    return subscribe_dal.get_active_sources()
