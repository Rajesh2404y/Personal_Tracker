import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from .services import AnalyticsService
from apps.ai_engine.models import AIInsight
from apps.goals.models import SavingsGoal
from apps.notifications.models import Notification

LANDING_FEATURES = [
    ('bi-arrow-left-right', '#6366f1', 'Transaction Tracking', 'Log income and expenses with smart categorization, tags, and receipt uploads.'),
    ('bi-wallet2', '#f59e0b', 'Budget Management', 'Set monthly spending limits per category and get alerts before you overspend.'),
    ('bi-trophy', '#10b981', 'Savings Goals', 'Create savings targets, track progress, and celebrate milestones.'),
    ('bi-stars', '#8b5cf6', 'AI Insights', 'Get intelligent spending analysis, budget recommendations, and savings tips.'),
    ('bi-file-earmark-bar-graph', '#3b82f6', 'Reports & Exports', 'Generate detailed reports and export to CSV or Excel in one click.'),
    ('bi-speedometer2', '#ef4444', 'Analytics Dashboard', 'Visualize your financial health with interactive charts and KPI cards.'),
]


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html', {'features': LANDING_FEATURES})


@login_required
def dashboard(request):
    service = AnalyticsService(request.user)

    # Single cache round-trip for all dashboard data
    summary, monthly_trend, category_breakdown, budget_utilization = service.get_all_dashboard_data()

    # Trigger async insight refresh via Celery (non-blocking)
    try:
        from apps.ai_engine.tasks import refresh_user_insights
        refresh_user_insights.delay(request.user.id)
    except Exception:
        # Fallback to sync if Celery not available
        from apps.ai_engine.engine import InsightEngine
        InsightEngine(request.user).refresh_insights()

    # Indexed lookups — fast
    insights = list(
        AIInsight.objects
        .filter(user=request.user, is_read=False)
        .only('id', 'insight_type', 'title', 'message', 'severity')
        [:5]
    )
    goals = list(
        SavingsGoal.objects
        .filter(user=request.user, status='active')
        .only('id', 'name', 'target_amount', 'current_amount', 'icon', 'color')
        [:3]
    )
    unread_notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    return render(request, 'dashboard/index.html', {
        'summary': summary,
        'monthly_trend_json': json.dumps(monthly_trend),
        'category_breakdown_json': json.dumps([
            {
                'name': c['category__name'] or 'Uncategorized',
                'total': float(c['total']),
                'color': c['category__color'] or '#6366f1',
            }
            for c in category_breakdown
        ]),
        'budget_utilization_json': json.dumps(budget_utilization),
        'recent_transactions': service.get_recent_transactions(),
        'insights': insights,
        'goals': goals,
        'unread_notifications': unread_notifications,
    })


@login_required
@require_GET
@never_cache
def analytics_api(request):
    """JSON endpoint — used by HTMX widgets and external API consumers."""
    service = AnalyticsService(request.user)
    summary, monthly_trend, category_breakdown, budget_utilization = service.get_all_dashboard_data()
    return JsonResponse({
        'summary': {k: float(v) if hasattr(v, '__float__') else v for k, v in summary.items()},
        'monthly_trend': monthly_trend,
        'category_breakdown': [
            {'name': c['category__name'] or 'Uncategorized', 'total': float(c['total']), 'color': c['category__color']}
            for c in category_breakdown
        ],
        'budget_utilization': budget_utilization,
    })


@login_required
@require_GET
def dashboard_kpis(request):
    """Lightweight KPI-only endpoint for HTMX polling."""
    service = AnalyticsService(request.user)
    summary = service.get_dashboard_summary()
    return JsonResponse({
        k: float(v) if hasattr(v, '__float__') else v
        for k, v in summary.items()
    })
