from celery import shared_task
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    soft_time_limit=60,
    time_limit=90,
    name='apps.ai_engine.tasks.refresh_user_insights',
)
def refresh_user_insights(self, user_id):
    from apps.ai_engine.engine import InsightEngine
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return 0
    return len(InsightEngine(user).refresh_insights())


@shared_task(
    name='apps.ai_engine.tasks.refresh_all_user_insights',
    soft_time_limit=240,
    time_limit=300,
)
def refresh_all_user_insights():
    """Scheduled task: refresh insights for all active users (runs hourly via Celery Beat)."""
    user_ids = list(
        User.objects.filter(is_active=True).values_list('id', flat=True)
    )
    for user_id in user_ids:
        refresh_user_insights.delay(user_id)
    return len(user_ids)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 2},
    soft_time_limit=120,
    time_limit=180,
    name='apps.ai_engine.tasks.generate_report_async',
)
def generate_report_async(self, user_id, report_id):
    """Generate a report file asynchronously and save to the Report model."""
    from apps.reports.models import Report
    from apps.reports.generator import ReportGenerator
    try:
        report = Report.objects.select_related('user').get(pk=report_id, user_id=user_id)
    except Report.DoesNotExist:
        return
    generator = ReportGenerator(report.user, report.date_from, report.date_to)
    if report.format == 'csv':
        content = generator.generate_csv()
        from django.core.files.base import ContentFile
        report.file.save(f'report_{report_id}.csv', ContentFile(content.encode()), save=True)
    elif report.format == 'excel':
        output = generator.generate_excel()
        from django.core.files.base import ContentFile
        report.file.save(f'report_{report_id}.xlsx', ContentFile(output.read()), save=True)
