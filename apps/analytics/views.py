import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
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

    # All cached — 120–300s TTL
    summary = service.get_dashboard_summary()
    monthly_trend = service.get_monthly_trend()
    category_breakdown = service.get_category_breakdown()
    budget_utilization = service.get_budget_utilization()
    recent_transactions = service.get_recent_transactions()

    # Insights only refresh once per hour
    from apps.ai_engine.engine import InsightEngine
    InsightEngine(request.user).refresh_insights()

    # Simple queries — indexed lookups
    insights = list(AIInsight.objects.filter(user=request.user, is_read=False).only('id', 'insight_type', 'title', 'message', 'severity')[:5])
    goals = list(SavingsGoal.objects.filter(user=request.user, status='active').only('id', 'name', 'target_amount', 'current_amount', 'icon', 'color')[:3])
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'dashboard/index.html', {
        'summary': summary,
        'monthly_trend_json': json.dumps(monthly_trend),
        'category_breakdown_json': json.dumps([
            {
                'name': c['category__name'] or 'Uncategorized',
                'total': float(c['total']),
                'color': c['category__color'] or '#6366f1'
            }
            for c in category_breakdown
        ]),
        'budget_utilization_json': json.dumps(budget_utilization),
        'recent_transactions': recent_transactions,
        'insights': insights,
        'goals': goals,
        'unread_notifications': unread_notifications,
    })


@login_required
def analytics_api(request):
    service = AnalyticsService(request.user)
    summary = service.get_dashboard_summary()
    return JsonResponse({
        'summary': {k: float(v) if hasattr(v, '__float__') else v for k, v in summary.items()},
        'monthly_trend': service.get_monthly_trend(),
        'category_breakdown': [
            {'name': c['category__name'], 'total': float(c['total'])}
            for c in service.get_category_breakdown()
        ],
    })
