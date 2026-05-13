import dj_database_url
from .base import *

DEBUG = True

# ── Database — Supabase PostgreSQL ────────────────────────────
DATABASES = {
    "default": dj_database_url.parse(
        env("DATABASE_URL"),
        conn_max_age=60,        # reuse connections for 60s locally
        ssl_require=False,
    )
}
DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True   # drop stale connections fast

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
CELERY_TASK_ALWAYS_EAGER = True

# ── Speed: disable heavy password hashing in dev ──────────────
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
