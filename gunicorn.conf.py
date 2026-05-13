import multiprocessing
import os

bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')

# (2 * CPU) + 1 is the standard formula for sync workers
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv('GUNICORN_THREADS', '4'))
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gthread')
worker_connections = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', '1000'))

timeout = int(os.getenv('GUNICORN_TIMEOUT', '30'))
graceful_timeout = int(os.getenv('GUNICORN_GRACEFUL_TIMEOUT', '30'))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', '5'))

# Recycle workers to prevent memory leaks
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '100'))

# Load app before forking workers — saves memory via copy-on-write
preload_app = os.getenv('GUNICORN_PRELOAD', 'true').lower() == 'true'

accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'warning')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)sµs'

# Forward client IP from Nginx/proxy
forwarded_allow_ips = os.getenv('FORWARDED_ALLOW_IPS', '127.0.0.1')
proxy_protocol = False
