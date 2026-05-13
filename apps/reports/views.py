from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from datetime import date
from calendar import monthrange
from .generator import ReportGenerator
from .models import Report


def _quick_exports(now):
    # This month
    month_start = now.replace(day=1).date()
    month_end = now.replace(day=monthrange(now.year, now.month)[1]).date()
    # Last month
    last = (now.replace(day=1) - timezone.timedelta(days=1))
    last_start = last.replace(day=1).date()
    last_end = last.replace(day=monthrange(last.year, last.month)[1]).date()
    # This year
    year_start = date(now.year, 1, 1)
    year_end = now.date()
    # Last year
    ly_start = date(now.year - 1, 1, 1)
    ly_end = date(now.year - 1, 12, 31)
    return [
        ('This Month', month_start, month_end),
        ('Last Month', last_start, last_end),
        ('This Year', year_start, year_end),
        ('Last Year', ly_start, ly_end),
    ]


@login_required
def report_dashboard(request):
    reports = Report.objects.filter(user=request.user)[:10]
    now = timezone.now()
    return render(request, 'reports/dashboard.html', {
        'reports': reports,
        'current_month': now.month,
        'current_year': now.year,
        'quick_exports': _quick_exports(now),
    })


@login_required
def generate_report(request):
    if request.method != 'POST':
        return render(request, 'reports/dashboard.html')

    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')
    fmt = request.POST.get('format', 'csv')

    try:
        date_from = date.fromisoformat(date_from)
        date_to = date.fromisoformat(date_to)
    except (ValueError, TypeError):
        now = timezone.now()
        date_from = now.replace(day=1).date()
        date_to = now.date()

    if date_from > date_to:
        now = timezone.now()
        messages.error(request, 'Report start date must be before end date.')
        return render(request, 'reports/dashboard.html', {
            'reports': Report.objects.filter(user=request.user)[:10],
            'current_month': now.month,
            'current_year': now.year,
            'quick_exports': _quick_exports(timezone.now()),
        })

    if fmt not in {'csv', 'excel', 'preview'}:
        fmt = 'csv'

    generator = ReportGenerator(request.user, date_from, date_to)
    report_format = 'csv' if fmt == 'preview' else fmt

    with transaction.atomic():
        Report.objects.create(
            user=request.user,
            report_type='custom',
            format=report_format,
            title=f'Finance report {date_from} to {date_to}',
            date_from=date_from,
            date_to=date_to,
        )

    if fmt == 'csv':
        content = generator.generate_csv()
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="finpilot_{date_from}_{date_to}.csv"'
        return response

    if fmt == 'excel':
        output = generator.generate_excel()
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="finpilot_{date_from}_{date_to}.xlsx"'
        return response

    summary = generator.get_summary()
    return render(request, 'reports/preview.html', {
        'summary': summary,
        'transactions': generator.transactions,
        'date_from': date_from,
        'date_to': date_to,
    })
