import logging
import time
import uuid

logger = logging.getLogger('apps')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.request_id = request_id
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        log_data = {
            'request_id': request_id,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user': getattr(request.user, 'email', 'anon'),
        }
        if duration >= 1:
            logger.warning('slow_request', extra=log_data)
        else:
            logger.info('request', extra=log_data)
        response['X-Request-ID'] = request_id
        return response
