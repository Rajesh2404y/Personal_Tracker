import logging
import time
import uuid
from django.conf import settings

logger = logging.getLogger('apps')
db_logger = logging.getLogger('django.db.backends')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD_MS', 200) / 1000

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.request_id = request_id
        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start
        log_data = {
            'request_id': request_id,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user': getattr(request.user, 'email', 'anon'),
        }
        if duration >= self.slow_threshold:
            logger.warning('slow_request', extra=log_data)
        elif not request.path.startswith('/static/'):
            logger.info('request', extra=log_data)
        response['X-Request-ID'] = request_id
        response['X-Response-Time'] = f'{round(duration * 1000, 2)}ms'
        return response
