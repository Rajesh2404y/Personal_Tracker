# FinPilot 🚀
### AI-Powered Personal Finance Intelligence Platform

> A production-grade, full-stack Django web application for personal finance management — featuring AI-powered insights, interactive analytics dashboards, budget tracking, savings goals, and multi-format report exports.

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.15-red)](https://django-rest-framework.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📸 Screenshots

| Dashboard | Transactions | Budgets | Goals |
|-----------|-------------|---------|-------|
| KPI cards, charts, AI insights | Filter, search, HTMX delete | Monthly limits, utilization | Progress tracking, milestones |

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13, Django 4.2.16, Django REST Framework 3.15 |
| **Auth** | JWT (SimpleJWT 5.3) + Session Authentication |
| **Database** | SQLite (dev) / PostgreSQL 15 (production) |
| **Frontend** | Django Templates, Bootstrap 5.3, HTMX 1.9, Alpine.js 3.13, Chart.js 4.4 |
| **DevOps** | Docker, Docker Compose, Gunicorn 23, WhiteNoise 6.8 |
| **Exports** | CSV (stdlib), Excel (openpyxl 3.1), PDF-ready (reportlab) |
| **AI Engine** | Rule-based InsightEngine (OpenAI-ready architecture) |

---

## ✨ Features

### 🔐 Authentication
- Register / Login / Logout with email-based auth
- JWT API authentication with refresh token rotation & blacklisting
- User profile management (avatar, currency, income/savings goals)
- Signal-based automatic profile creation

### 📊 Analytics Dashboard
- KPI cards — Monthly Income, Expenses, Net Balance, Savings Rate
- Financial Health Score (0–100) with animated SVG ring
- Cash Flow Trend — 6-month bar chart (Chart.js)
- Expense Breakdown — Doughnut chart by category
- Budget Utilization — Horizontal bar chart
- Recent Transactions feed
- AI Insights panel
- Savings Goals progress

### 💸 Transactions
- Full CRUD — Add, Edit, Delete transactions
- Income & Expense separation
- Category assignment with color-coded icons
- Tags / labels support
- Receipt image uploads
- Recurrence settings (daily, weekly, monthly, yearly)
- Advanced filtering — by type, category, date range, search
- HTMX-powered inline delete (no page reload)
- Pagination (20 per page)

### 💰 Budgets
- Monthly category budgets
- Real-time utilization tracking (spent vs. budget)
- Configurable alert threshold (default 80%)
- Visual progress bars with color-coded status
- Overspend detection and warnings

### 🏆 Savings Goals
- Create savings targets with icons and colors
- Track progress with animated progress bars
- Contribute funds via modal
- Auto-complete when target reached
- Active / Completed goal separation

### 🤖 AI Insights Engine
- Budget exceeded alerts
- Budget threshold warnings
- Spending trend analysis (month-over-month comparison)
- Savings rate tips (below 10% warning, above 20% celebration)
- Monthly summary generation
- Architecture ready for OpenAI GPT integration

### 📈 Reports & Exports
- Custom date range reports
- Quick-export presets: This Month, Last Month, This Year, Last Year
- Export formats: **CSV**, **Excel** (styled with openpyxl)
- In-browser preview with summary KPIs
- Category breakdown in exports

### 🔔 Notifications
- Budget alert notifications
- Goal milestone notifications
- HTMX mark-as-read (no page reload)
- Unread count badge in topbar

### 🌐 REST API
- Full versioned API at `/api/v1/`
- JWT authentication
- Pagination, filtering, search, ordering on all endpoints
- Rate throttling (100/day anon, 1000/day user)
- DRF ViewSets with custom actions

---

## 🗂️ Project Structure

```
finpilot/
│
├── apps/
│   ├── accounts/                  # Auth, CustomUser, Profile
│   │   ├── migrations/
│   │   ├── models.py              # CustomUser, Profile
│   │   ├── views.py               # register, login, logout, profile
│   │   ├── forms.py               # RegisterForm, LoginForm, ProfileForm
│   │   ├── signals.py             # Auto-create Profile on user creation
│   │   ├── admin.py
│   │   └── urls.py
│   │
│   ├── transactions/              # Core financial transactions
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_default_categories.py   # Seeds 15 default categories
│   │   │   └── 0003_transaction_query_indexes.py
│   │   ├── models.py              # Transaction, Category
│   │   ├── views.py               # CRUD views + HTMX support
│   │   ├── forms.py               # TransactionForm
│   │   ├── repository.py          # TransactionRepository (query abstraction)
│   │   ├── admin.py
│   │   └── urls.py
│   │
│   ├── budgets/                   # Monthly budget management
│   │   ├── migrations/
│   │   ├── models.py              # Budget (with live spent/remaining properties)
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── urls.py
│   │
│   ├── goals/                     # Savings goals
│   │   ├── migrations/
│   │   ├── models.py              # SavingsGoal
│   │   ├── views.py               # CRUD + contribute
│   │   ├── admin.py
│   │   └── urls.py
│   │
│   ├── analytics/                 # Dashboard & analytics
│   │   ├── services.py            # AnalyticsService (business logic)
│   │   ├── views.py               # dashboard, home, analytics_api
│   │   └── urls.py
│   │
│   ├── ai_engine/                 # AI insights engine
│   │   ├── migrations/
│   │   ├── models.py              # AIInsight
│   │   ├── engine.py              # InsightEngine (rule-based)
│   │   ├── tasks.py               # Celery tasks (stubbed, OpenAI-ready)
│   │   └── admin.py
│   │
│   ├── reports/                   # Report generation & exports
│   │   ├── migrations/
│   │   ├── models.py              # Report
│   │   ├── generator.py           # ReportGenerator (CSV, Excel)
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── notifications/             # User notifications
│   │   ├── migrations/
│   │   ├── models.py              # Notification
│   │   ├── views.py               # list, mark_read, mark_all_read
│   │   └── urls.py
│   │
│   └── api/                       # REST API layer
│       ├── serializers.py         # All DRF serializers
│       ├── views.py               # ViewSets + APIViews
│       └── urls.py                # Router + JWT endpoints
│
├── config/
│   ├── settings/
│   │   ├── base.py                # Shared settings (JWT, DRF, logging)
│   │   ├── local.py               # SQLite, DEBUG=True, console email
│   │   ├── development.py         # Debug toolbar
│   │   └── production.py          # Security headers, HTTPS
│   ├── urls.py                    # Root URL configuration
│   ├── middleware.py              # RequestLoggingMiddleware
│   ├── pagination.py              # StandardResultsPagination
│   ├── context_processors.py      # Global template context
│   └── wsgi.py
│
├── templates/
│   ├── base.html                  # App shell (sidebar, topbar, dark mode)
│   ├── auth_base.html             # Auth page layout
│   ├── landing.html               # Public landing page
│   ├── dashboard/
│   │   └── index.html             # Main dashboard with all charts
│   ├── registration/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── transactions/
│   │   ├── list.html              # Filterable table with HTMX delete
│   │   ├── form.html              # Add/Edit form
│   │   └── categories.html
│   ├── budgets/
│   │   └── list.html              # Budget cards with progress bars
│   ├── goals/
│   │   ├── list.html              # Goal cards with contribute modals
│   │   └── form.html
│   ├── reports/
│   │   ├── dashboard.html         # Report generator + quick exports
│   │   └── preview.html           # In-browser report preview
│   └── partials/
│       ├── notifications.html     # HTMX notification panel
│       └── empty.html
│
├── static/
│   ├── css/
│   │   └── finpilot.css           # Full custom design system (~600 lines)
│   └── js/
│       └── finpilot.js            # HTMX CSRF, Chart.js defaults, animations
│
├── tests/
│   └── test_core.py               # 12 test cases (auth, models, views, API)
│
├── requirements/
│   ├── base.txt                   # Production dependencies
│   ├── development.txt            # + debug toolbar, pytest, factory-boy
│   └── production.txt             # + sentry, django-redis
│
├── docker-compose.yml             # web + db (postgres) + redis
├── Dockerfile                     # Python 3.11-slim, gunicorn
├── gunicorn.conf.py               # Worker config
├── manage.py
├── pytest.ini
├── .env                           # Local environment (gitignored)
├── .env.example                   # Environment variable template
└── .gitignore
```

---

## 🗄️ Database Schema

```
CustomUser (AUTH_USER_MODEL)
    │
    ├──[1:1]── Profile
    │           └── currency, monthly_income_goal, monthly_savings_goal, avatar
    │
    ├──[1:N]── Transaction ──[N:1]── Category
    │           └── amount, date, type, tags, receipt, recurrence
    │
    ├──[1:N]── Budget ──[N:1]── Category
    │           └── amount, month, year, alert_threshold
    │           └── @property: spent, remaining, utilization_percent
    │
    ├──[1:N]── SavingsGoal
    │           └── target_amount, current_amount, target_date
    │           └── @property: progress_percent, remaining_amount
    │
    ├──[1:N]── AIInsight
    │           └── insight_type, severity, message, data (JSON)
    │
    ├──[1:N]── Notification
    │           └── notification_type, title, message, is_read
    │
    └──[1:N]── Report
                └── report_type, format, date_from, date_to, file
```

**Indexes:**
- `users` → `email`
- `categories` → `(user, category_type)`
- `transactions` → `(user, date)`, `(user, transaction_type)`, `(user, category)`
- `budgets` → `(user, year, month)`
- `savings_goals` → `(user, status)`
- `ai_insights` → `(user, is_read, created_at)`
- `notifications` → `(user, is_read)`

---

## 🌐 API Reference

**Base URL:** `http://localhost:8080/api/v1/`

### Authentication Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/register/` | Create new account | ❌ |
| `POST` | `/auth/login/` | Obtain JWT access + refresh tokens | ❌ |
| `POST` | `/auth/refresh/` | Refresh access token | ❌ |
| `POST` | `/auth/logout/` | Blacklist refresh token | ✅ |
| `GET` | `/auth/me/` | Get current user profile | ✅ |
| `PUT` | `/auth/me/` | Update current user profile | ✅ |

### Resource Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/transactions/` | List transactions (paginated, filterable) |
| `POST` | `/transactions/` | Create transaction |
| `GET` | `/transactions/{id}/` | Get transaction detail |
| `PUT/PATCH` | `/transactions/{id}/` | Update transaction |
| `DELETE` | `/transactions/{id}/` | Delete transaction |
| `GET` | `/categories/` | List categories |
| `POST` | `/categories/` | Create custom category |
| `GET` | `/budgets/` | List budgets (filter by month/year) |
| `POST` | `/budgets/` | Create budget |
| `GET` | `/goals/` | List savings goals |
| `POST` | `/goals/` | Create savings goal |
| `POST` | `/goals/{id}/contribute/` | Add funds to goal |
| `GET` | `/insights/` | List AI insights |
| `POST` | `/insights/refresh/` | Regenerate all insights |
| `POST` | `/insights/{id}/mark_read/` | Mark insight as read |
| `GET` | `/analytics/` | Full dashboard summary (JSON) |

### Query Parameters (Transactions)

| Param | Type | Example |
|-------|------|---------|
| `transaction_type` | string | `?transaction_type=expense` |
| `category` | integer | `?category=3` |
| `date_from` | date | `?date_from=2024-01-01` |
| `date_to` | date | `?date_to=2024-01-31` |
| `search` | string | `?search=coffee` |
| `ordering` | string | `?ordering=-date` |
| `page` | integer | `?page=2` |
| `page_size` | integer | `?page_size=50` |

### Request Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Sample Request — Create Transaction

```bash
curl -X POST http://localhost:8080/api/v1/transactions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "expense",
    "amount": "45.50",
    "description": "Grocery shopping",
    "category": 1,
    "date": "2024-01-15",
    "tags": "groceries,weekly"
  }'
```

### Sample Response

```json
{
  "id": 42,
  "transaction_type": "expense",
  "amount": "45.50",
  "description": "Grocery shopping",
  "category": 1,
  "category_name": "Food & Dining",
  "category_color": "#f59e0b",
  "date": "2024-01-15",
  "tags": "groceries,weekly",
  "tag_list": ["groceries", "weekly"],
  "recurrence": "none",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 🚀 Quick Start (Local — SQLite)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/finpilot.git
cd finpilot

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements/base.txt

# 4. Copy environment file
cp .env.example .env

# 5. Run migrations (creates SQLite DB + seeds 15 default categories)
python manage.py migrate --settings=config.settings.local

# 6. Create superuser
python manage.py createsuperuser --settings=config.settings.local

# 7. Collect static files
python manage.py collectstatic --noinput --settings=config.settings.local

# 8. Start development server
python manage.py runserver 8080 --settings=config.settings.local
```

Open **http://localhost:8080** in your browser.

**Admin panel:** http://localhost:8080/admin/
**API root:** http://localhost:8080/api/v1/

---

## 🐳 Docker Setup (PostgreSQL)

```bash
# 1. Clone and configure
git clone https://github.com/yourusername/finpilot.git
cd finpilot
cp .env.example .env

# 2. Build and start all services (web + postgres + redis)
docker-compose up --build

# 3. Run migrations (in a new terminal)
docker-compose exec web python manage.py migrate

# 4. Seed default categories
# Already handled by migration 0002_default_categories

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Open browser
# http://localhost:8000
```

**Services started by Docker Compose:**
- `web` — Django + Gunicorn on port 8000
- `db` — PostgreSQL 15 on port 5432
- `redis` — Redis 7 on port 6379

---

## ☁️ Deployment

### Render

1. Push code to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repository
4. Set **Build Command:**
   ```bash
   pip install -r requirements/production.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
5. Set **Start Command:**
   ```bash
   gunicorn config.wsgi:application
   ```
6. Add a **PostgreSQL** database from Render dashboard
7. Set environment variables (see table below)
8. Set `DJANGO_SETTINGS_MODULE=config.settings.production`

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up

# Add PostgreSQL from Railway dashboard
# Set all environment variables in Railway dashboard
```

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | ✅ | Django secret key | `django-insecure-...` |
| `DEBUG` | ✅ | Debug mode | `False` |
| `DATABASE_URL` | ✅ | Database connection URL | `postgresql://user:pass@host/db` |
| `ALLOWED_HOSTS` | ✅ | Comma-separated hosts | `yourdomain.com,www.yourdomain.com` |
| `CORS_ALLOWED_ORIGINS` | ✅ | CORS origins | `https://yourdomain.com` |
| `EMAIL_BACKEND` | ❌ | Email backend | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | ❌ | SMTP host | `smtp.gmail.com` |
| `EMAIL_PORT` | ❌ | SMTP port | `587` |
| `EMAIL_HOST_USER` | ❌ | SMTP username | `you@gmail.com` |
| `EMAIL_HOST_PASSWORD` | ❌ | SMTP password | `app-password` |
| `CURRENCY_SYMBOL` | ❌ | Display symbol | `$` |
| `CURRENCY_CODE` | ❌ | ISO code | `USD` |

---

## 🧪 Running Tests

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run all tests
pytest --settings=config.settings.local

# Run with coverage report
pytest --settings=config.settings.local --cov=apps --cov-report=html

# Run specific test file
pytest tests/test_core.py -v --settings=config.settings.local

# Run specific test class
pytest tests/test_core.py::TestAuthentication -v --settings=config.settings.local
```

**Test Coverage:**

| Test Class | Tests | Coverage |
|---|---|---|
| `TestAuthentication` | Register, Login, Dashboard redirect | Auth flow |
| `TestTransactionModel` | Create, tag_list property | Transaction model |
| `TestBudgetModel` | Utilization %, exceeded flag | Budget model |
| `TestSavingsGoal` | Progress %, is_completed, remaining | Goal model |
| `TestAnalyticsService` | Empty summary, health score range | Analytics |
| `TestTransactionViews` | List view, create transaction | Views |
| `TestAPIEndpoints` | Register API, Login API | REST API |

---

## 🏗️ Architecture

### Service Layer Pattern
Business logic is isolated from views in dedicated service classes:

```
views.py  →  AnalyticsService  →  ORM queries
views.py  →  InsightEngine     →  Rule evaluation
views.py  →  ReportGenerator   →  CSV/Excel output
```

### Repository Pattern
Query logic is abstracted in repository classes:

```python
# Instead of raw ORM in views:
TransactionRepository.get_user_transactions(user, filters)
TransactionRepository.get_categories(user)
```

### Modular Django Apps
Each domain is a self-contained app with its own models, views, URLs, and migrations. Apps communicate only through model imports — no circular dependencies.

### AI Engine Architecture
The `InsightEngine` is designed for extensibility:

```python
class InsightEngine:
    def generate_all_insights(self):
        # Rule-based today
        # Drop-in OpenAI replacement tomorrow:
        # return OpenAIInsightEngine(self.user).generate()
        ...
```

### Security Implementation
- CSRF protection on all forms and HTMX requests
- JWT with refresh token rotation + blacklisting
- Rate throttling: 100 req/day (anon), 1000 req/day (user)
- SQL injection protection via Django ORM (parameterized queries)
- XSS protection via Django template auto-escaping
- Secure file upload handling (Pillow validation)
- Production: HSTS, SSL redirect, secure cookies, X-Frame-Options

---

## 📦 Default Categories (Auto-seeded)

**Expense Categories:**
`Food & Dining` · `Housing` · `Transport` · `Health` · `Entertainment` · `Shopping` · `Education` · `Utilities` · `Travel` · `Other Expense`

**Income Categories:**
`Salary` · `Freelance` · `Investment` · `Business` · `Other Income`

---

## 🔧 Development Notes

### Adding a New App

```bash
# 1. Create app
python manage.py startapp myapp apps/myapp

# 2. Add to LOCAL_APPS in config/settings/base.py
# 3. Create migrations
python manage.py makemigrations myapp --settings=config.settings.local
# 4. Apply migrations
python manage.py migrate --settings=config.settings.local
```

### Enabling Celery (Async Tasks)

```bash
# Install celery + redis
pip install celery redis django-redis

# Uncomment tasks in apps/ai_engine/tasks.py
# Update config/__init__.py to import celery app
# Start worker
celery -A config worker --loglevel=info
```

### Enabling OpenAI Integration

```python
# In apps/ai_engine/engine.py, replace _spending_trends() with:
import openai

def _openai_insights(self):
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": self._build_prompt()}]
    )
    # Parse and return AIInsight objects
```

---

## 📄 License

MIT License — free to use for personal projects, portfolios, and commercial applications.

---

## 👤 Author

Built as a production-grade portfolio project demonstrating:
- Django architecture & best practices
- REST API design with DRF
- Full-stack web development
- Database optimization & indexing
- Docker & deployment readiness
- Clean code & modular design

---

*FinPilot — Built with Django 4.2 · PostgreSQL · Bootstrap 5 · Chart.js · HTMX · Alpine.js*
