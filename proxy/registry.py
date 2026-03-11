"""
Service proxy registry for inter-module communication.
Enables modules to call each other's services without direct imports.
"""

_registry = {}


def register(name, func):
    """Register a service function.

    Usage: register('news.search_by_keywords', news_service.search_by_keywords)
    """
    _registry[name] = func


def call(name, **kwargs):
    """Call a registered service by name.

    Usage: call('news.search_by_keywords', keywords=['AI', 'ML'])
    """
    if name not in _registry:
        raise KeyError(f"Service '{name}' not registered")
    return _registry[name](**kwargs)


def get(name):
    """Get a registered function reference, or None if not found."""
    return _registry.get(name)


def list_services():
    """List all registered service names."""
    return list(_registry.keys())
