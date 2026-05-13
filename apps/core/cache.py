from django.core.cache import cache


ANALYTICS_VERSION_KEY = 'analytics:v:{user_id}'
ANALYTICS_KEY = 'analytics:{user_id}:{version}:{name}'
DEFAULT_ANALYTICS_TIMEOUT = 300


def get_user_cache_version(user_id):
    key = ANALYTICS_VERSION_KEY.format(user_id=user_id)
    version = cache.get(key)
    if version is None:
        version = 1
        cache.set(key, version, None)
    return version


def bump_user_cache_version(user_id):
    key = ANALYTICS_VERSION_KEY.format(user_id=user_id)
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 2, None)


def user_analytics_cache_key(user_id, name):
    version = get_user_cache_version(user_id)
    return ANALYTICS_KEY.format(user_id=user_id, version=version, name=name)


def get_or_set_user_analytics(user_id, name, producer, timeout=DEFAULT_ANALYTICS_TIMEOUT):
    key = user_analytics_cache_key(user_id, name)
    value = cache.get(key)
    if value is None:
        value = producer()
        cache.set(key, value, timeout)
    return value
