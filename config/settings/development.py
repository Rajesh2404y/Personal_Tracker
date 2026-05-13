from .base import *

DEBUG = True

# Disable template caching in dev — use APP_DIRS for live reload
TEMPLATES[0]['APP_DIRS'] = True
TEMPLATES[0]['OPTIONS'].pop('loaders', None)

# Disable cachalot in dev to avoid stale query cache confusion
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'cachalot']

INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = ['127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CELERY_TASK_ALWAYS_EAGER = True

# Log all SQL queries in dev
LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
