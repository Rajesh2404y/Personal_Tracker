FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install PostgreSQL client libraries + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt requirements/production.txt
RUN pip install --upgrade pip && \
    pip install -r requirements/production.txt

# Copy application code
COPY . .

# Collect static files (will fail gracefully if DB not ready)
RUN python manage.py collectstatic --noinput --settings=config.settings.production 2>/dev/null || true

# Create required directories
RUN mkdir -p logs media

EXPOSE 8000

# Use production settings by default
ENV DJANGO_SETTINGS_MODULE=config.settings.production

CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]
