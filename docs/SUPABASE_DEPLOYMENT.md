# FinPilot — Supabase PostgreSQL Deployment Guide

## 🎯 Overview

This guide covers deploying FinPilot with **Supabase PostgreSQL** as the production database.

---

## 📋 Prerequisites

1. **Supabase Account** — [supabase.com](https://supabase.com)
2. **Render/Railway Account** — for hosting Django
3. **Git Repository** — code pushed to GitHub/GitLab

---

## 🗄️ Step 1: Set Up Supabase Database

### 1.1 Create a New Project

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click **New Project**
3. Fill in:
   - **Name:** `finpilot-prod`
   - **Database Password:** Generate a strong password (save it!)
   - **Region:** Choose closest to your users
4. Wait 2–3 minutes for provisioning

### 1.2 Get Connection String

1. Go to **Project Settings** → **Database**
2. Scroll to **Connection string**
3. Select **URI** tab
4. Copy the connection string:

```
postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@db.[project-ref].supabase.co:5432/postgres
```

**⚠️ IMPORTANT:** Replace `[YOUR-PASSWORD]` with your actual database password.

### 1.3 Use Transaction Pooler (Recommended)

For better performance with Django, use the **Transaction pooler**:

1. In the same **Connection string** section
2. Switch to **Transaction** mode
3. Copy the pooler URL (port `6543`):

```
postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Why Transaction Pooler?**
- Reduces connection overhead
- Works with Django's `conn_max_age`
- Handles 1000+ concurrent connections
- Lower latency (~5–10ms improvement)

---

## 🚀 Step 2: Deploy to Render

### 2.1 Create Web Service

1. Go to [render.com/dashboard](https://render.com/dashboard)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `finpilot`
   - **Environment:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements/production.txt && python manage.py collectstatic --noinput --settings=config.settings.production && python manage.py migrate --settings=config.settings.production
     ```
   - **Start Command:**
     ```bash
     gunicorn config.wsgi:application -c gunicorn.conf.py
     ```

### 2.2 Set Environment Variables

In Render dashboard → **Environment** tab, add:

| Key | Value |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `finpilot.onrender.com,www.finpilot.com` |
| `DATABASE_URL` | Your Supabase connection string (from Step 1.3) |
| `CACHE_URL` | Leave empty (uses in-memory cache) |
| `CORS_ALLOWED_ORIGINS` | `https://finpilot.onrender.com` |

**Optional but recommended:**

| Key | Value |
|-----|-------|
| `SENTRY_DSN` | Your Sentry DSN for error tracking |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_HOST_USER` | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail app password |

### 2.3 Deploy

1. Click **Create Web Service**
2. Wait 5–10 minutes for first deploy
3. Check logs for errors

---

## 🚂 Step 3: Deploy to Railway (Alternative)

### 3.1 Install Railway CLI

```bash
npm install -g @railway/cli
```

### 3.2 Initialize Project

```bash
cd finpilot
railway login
railway init
```

### 3.3 Set Environment Variables

```bash
railway variables set DJANGO_SETTINGS_MODULE=config.settings.production
railway variables set SECRET_KEY="your-secret-key-here"
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS="finpilot.up.railway.app"
railway variables set DATABASE_URL="your-supabase-connection-string"
```

### 3.4 Deploy

```bash
railway up
```

---

## 🧪 Step 4: Test Database Connection

### 4.1 Local Test (Before Deploying)

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Set DATABASE_URL temporarily
export DATABASE_URL="your-supabase-connection-string"  # macOS/Linux
set DATABASE_URL=your-supabase-connection-string  # Windows

# Test connection
python manage.py check --settings=config.settings.production

# Run migrations
python manage.py migrate --settings=config.settings.production

# Create superuser
python manage.py createsuperuser --settings=config.settings.production
```

### 4.2 Production Test

After deployment, check logs:

```bash
# Render
# Go to Logs tab in dashboard

# Railway
railway logs
```

Look for:
```
✅ "Applying migrations..."
✅ "163 static files copied to..."
✅ "Booting worker with pid: 1"
```

### 4.3 Database Connection Test

SSH into your production environment (if available) or use Django shell:

```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
# Should print: ('PostgreSQL 15.x on x86_64-pc-linux-gnu...',)
```

---

## 🔄 Step 5: Run Migrations

### 5.1 Initial Migration

Migrations run automatically during build (see Build Command in Step 2.1).

### 5.2 Manual Migration (if needed)

**Render:**
1. Go to **Shell** tab
2. Run:
   ```bash
   python manage.py migrate --settings=config.settings.production
   ```

**Railway:**
```bash
railway run python manage.py migrate --settings=config.settings.production
```

### 5.3 Create Superuser

**Render:**
```bash
# In Shell tab
python manage.py createsuperuser --settings=config.settings.production
```

**Railway:**
```bash
railway run python manage.py createsuperuser --settings=config.settings.production
```

---

## 🔐 Step 6: Security Checklist

### 6.1 Verify Settings

- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` is unique and not in version control
- [ ] `ALLOWED_HOSTS` contains only your domains
- [ ] `DATABASE_URL` uses SSL (`ssl_require=True` is set)
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`

### 6.2 Supabase Security

1. **Enable Row Level Security (RLS)** — optional for Django ORM
2. **Restrict IP Access** — Supabase Dashboard → Settings → Database → Network Restrictions
3. **Rotate Database Password** — every 90 days

### 6.3 Django Security

```bash
# Run Django security check
python manage.py check --deploy --settings=config.settings.production
```

Should return: `System check identified no issues (0 silenced).`

---

## 📊 Step 7: Monitor Database Performance

### 7.1 Supabase Dashboard

1. Go to **Database** → **Logs**
2. Monitor:
   - Query performance
   - Connection count
   - Slow queries (>100ms)

### 7.2 Django Query Optimization

Enable query logging in production (temporarily):

```python
# In production.py
LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}
```

Look for:
- N+1 queries (use `select_related()` / `prefetch_related()`)
- Missing indexes (check `EXPLAIN ANALYZE` in Supabase SQL Editor)

### 7.3 Connection Pooling Stats

Check active connections:

```sql
-- Run in Supabase SQL Editor
SELECT count(*) FROM pg_stat_activity WHERE datname = 'postgres';
```

Should be < 20 connections for a single Django instance.

---

## 🐛 Troubleshooting

### Issue 1: `FATAL: no pg_hba.conf entry for host`

**Cause:** SSL not enabled.

**Fix:** Ensure `ssl_require=True` in `production.py` (already set).

---

### Issue 2: `OperationalError: FATAL: remaining connection slots are reserved`

**Cause:** Too many connections to Supabase.

**Fix:**
1. Use Transaction pooler URL (port `6543`) instead of direct connection
2. Reduce `conn_max_age` to `300` (5 min)
3. Scale down Gunicorn workers: `WEB_CONCURRENCY=2`

---

### Issue 3: `django.db.utils.OperationalError: server closed the connection unexpectedly`

**Cause:** PgBouncer transaction mode incompatibility.

**Fix:** Already handled — `DISABLE_SERVER_SIDE_CURSORS = True` is set in `production.py`.

---

### Issue 4: Migrations fail with `relation does not exist`

**Cause:** Migrations not applied or wrong database.

**Fix:**
```bash
# Check current migrations
python manage.py showmigrations --settings=config.settings.production

# Apply all migrations
python manage.py migrate --settings=config.settings.production
```

---

### Issue 5: Static files not loading

**Cause:** `collectstatic` not run or WhiteNoise misconfigured.

**Fix:**
```bash
# Collect static files
python manage.py collectstatic --noinput --settings=config.settings.production

# Verify WhiteNoise is in MIDDLEWARE (already set in base.py)
```

---

## 🔄 Step 8: Backup & Restore

### 8.1 Automated Backups

Supabase automatically backs up your database:
- **Daily backups** — retained for 7 days (Free tier)
- **Point-in-time recovery** — Pro tier only

### 8.2 Manual Backup

```bash
# Export database to SQL file
pg_dump "your-supabase-connection-string" > backup.sql

# Restore from backup
psql "your-supabase-connection-string" < backup.sql
```

### 8.3 Django Data Export

```bash
# Export all data to JSON
python manage.py dumpdata --settings=config.settings.production > data.json

# Import data
python manage.py loaddata data.json --settings=config.settings.production
```

---

## 📈 Step 9: Scaling Considerations

### 9.1 Database Scaling

**Supabase Free Tier:**
- 500 MB storage
- 2 GB bandwidth
- Unlimited API requests

**When to upgrade:**
- Storage > 400 MB
- Concurrent connections > 50
- Query latency > 200ms

### 9.2 Django Scaling

**Horizontal Scaling:**
```bash
# Render: Scale to 2 instances
# Dashboard → Settings → Scaling → Instances: 2

# Railway: Scale replicas
railway scale --replicas 2
```

**Vertical Scaling:**
- Increase Gunicorn workers: `WEB_CONCURRENCY=4`
- Increase memory: 1 GB → 2 GB

### 9.3 Caching

Add Redis for caching:

```bash
# Set CACHE_URL in environment
CACHE_URL=redis://red-xxxxx.redis.render.com:6379/1
```

Django will automatically use Redis (already configured in `base.py`).

---

## ✅ Deployment Checklist

Before going live:

- [ ] Database connection tested
- [ ] Migrations applied
- [ ] Superuser created
- [ ] Static files collected
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` set correctly
- [ ] SSL enabled (`SECURE_SSL_REDIRECT = True`)
- [ ] Sentry configured (optional)
- [ ] Email configured (optional)
- [ ] Backup strategy in place
- [ ] Security check passed (`python manage.py check --deploy`)

---

## 🆘 Support

**Supabase Issues:**
- [Supabase Docs](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)

**Django Issues:**
- [Django Docs](https://docs.djangoproject.com)
- [Django Forum](https://forum.djangoproject.com)

**FinPilot Issues:**
- Check logs in Render/Railway dashboard
- Enable `DEBUG = True` temporarily (local only!)
- Run `python manage.py check --deploy`

---

## 📝 Summary

You've successfully configured FinPilot with Supabase PostgreSQL:

✅ Production-grade database with SSL  
✅ Connection pooling for performance  
✅ Secure Django settings  
✅ Deployment-ready configuration  
✅ Monitoring and backup strategy  

**Next Steps:**
1. Deploy to Render/Railway
2. Run migrations
3. Create superuser
4. Test the application
5. Monitor performance

---

*Last updated: 2024*
