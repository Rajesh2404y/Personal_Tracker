from .base import *
import dj_database_url

DEBUG = False

# ── Database — persistent connections + PgBouncer-safe ────────
DATABASES = {
    "default": {
        **dj_database_url.parse(
            env("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True,
        ),
        'CONN_HEALTH_CHECKS': True,
        'DISABLE_SERVER_SIDE_CURSORS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30s hard limit per query
        },
    }
}

# ── Security Headers ──────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ── Static Files — WhiteNoise ─────────────────────────────────
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ── Template caching disabled in DEBUG=False (already cached) ─
# Cachalot: disable for tables that change very frequently
CACHALOT_UNCACHABLE_TABLES = frozenset([
    'django_session',
    'notifications',
])
CACHALOT_TIMEOUT = 300

# ── Logging ───────────────────────────────────────────────────
LOGGING["handlers"]["console"]["formatter"] = "structured"
LOGGING["root"]["level"] = "WARNING"
LOGGING["loggers"]["django"]["level"] = "WARNING"
LOGGING["loggers"]["apps"]["level"] = "INFO"

# ── Sentry ────────────────────────────────────────────────────
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            LoggingIntegration(level=None, event_level="ERROR"),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.05),
        profiles_sample_rate=env.float("SENTRY_PROFILES_SAMPLE_RATE", default=0.01),
        send_default_pii=False,
        environment=env("SENTRY_ENVIRONMENT", default="production"),
        release=env("GIT_COMMIT_SHA", default="unknown"),
    )
