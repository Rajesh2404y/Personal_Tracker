from .base import *
import dj_database_url

# ─────────────────────────────────────────────
# CORE
# ─────────────────────────────────────────────
DEBUG = False

# ─────────────────────────────────────────────
# DATABASE — Supabase PostgreSQL
#
# Why ssl_require=True:
#   Supabase enforces TLS on all connections.
#   Without it the connection is rejected or
#   transmitted in plaintext — a security risk.
#
# Why conn_max_age=600:
#   Keeps the TCP connection alive for 10 min
#   instead of opening a new one per request.
#   Reduces latency by ~5–20 ms per request and
#   lowers connection overhead on Supabase's
#   PgBouncer pool.
# ─────────────────────────────────────────────
DATABASES = {
    "default": dj_database_url.parse(
        env("DATABASE_URL"),          # set in Render/Railway env vars
        conn_max_age=600,             # persistent connections (10 min)
        ssl_require=True,             # mandatory for Supabase TLS
    )
}

# Supabase uses PgBouncer in transaction mode by default.
# Disable server-side cursors to stay compatible.
DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

# ─────────────────────────────────────────────
# SECURITY HEADERS
# ─────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # Render/Railway proxy
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ─────────────────────────────────────────────
# STATIC FILES — WhiteNoise
# ─────────────────────────────────────────────
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ─────────────────────────────────────────────
# LOGGING — structured JSON-style for Render/Railway
# ─────────────────────────────────────────────
LOGGING["handlers"]["console"]["formatter"] = "structured"
LOGGING["root"]["level"] = "WARNING"
LOGGING["loggers"]["django"]["level"] = "WARNING"
LOGGING["loggers"]["apps"]["level"] = "INFO"

# ─────────────────────────────────────────────
# SENTRY — error tracking (optional)
# ─────────────────────────────────────────────
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            LoggingIntegration(level=None, event_level="ERROR"),
        ],
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
        send_default_pii=False,
        environment=env("SENTRY_ENVIRONMENT", default="production"),
        release=env("GIT_COMMIT_SHA", default="unknown"),
    )
