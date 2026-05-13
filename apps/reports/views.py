import re
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


def _safe_filename(value):
    """Strip non-alphanumeric chars to prevent header injection (CWE-79)."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '', str(value))


def _quick_exports(now):
    month_start = now.replace(day=1).date()
    month_end = now.replace(day=monthrange(now.year, now.month)[1]).date()
    last = now.replace(day=1) - timezone.timedelta(days=1)
    last_start = last.replace(day=1).date()
    last_end = last.replace(day=monthrange(last.year, last.month)[1]).date()
    return [
        ('This Month', month_start, month_end),
        ('Last Month', last_start, last_end),
        ('This Year', date(now.year, 1, 1), now.date()),
        ('Last Year', date(now.year - 1, 1, 1), date(now.year - 1, 12, 31)),
    ]


def _parse_dates(post):
    """Parse and validate date_from / date_to from POST data."""
    try:
        date_from = date.fromisoformat(post.get('date_from', ''))
        date_to = date.fromisoformat(post.get('date_to', ''))
    except (ValueError, TypeError):
        now = timezone.now()
        date_from = now.replace(day=1).date()
        date_to = now.date()
    return date_from, date_to


def _build_csv_response(generator, date_from, date_to):
    content = generator.generate_csv()
    fname = f"finpilot_{_safe_filename(date_from)}_{_safe_filename(date_to)}.csv"
    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return response


def _build_excel_response(generator, date_from, date_to):
    output = generator.generate_excel()
    fname = f"finpilot_{_safe_filename(date_from)}_{_safe_filename(date_to)}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return response


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

    date_from, date_to = _parse_dates(request.POST)
    fmt = request.POST.get('format', 'csv')

    if date_from > date_to:
        messages.error(request, 'Report start date must be before end date.')
        now = timezone.now()
        return render(request, 'reports/dashboard.html', {
            'reports': Report.objects.filter(user=request.user)[:10],
            'current_month': now.month,
            'current_year': now.year,
            'quick_exports': _quick_exports(now),
        })

    if fmt not in {'csv', 'excel', 'preview'}:
        fmt = 'csv'

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

    generator = ReportGenerator(request.user, date_from, date_to)

    if fmt == 'csv':
        return _build_csv_response(generator, date_from, date_to)

    if fmt == 'excel':
        return _build_excel_response(generator, date_from, date_to)

    return render(request, 'reports/preview.html', {
        'summary': generator.get_summary(),
        'transactions': generator.transactions,
        'date_from': date_from,
        'date_to': date_to,
    })
