from celery import shared_task
from django.contrib.auth import get_user_model

from apps.reports.generator import ReportGenerator


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def build_report_summary(self, user_id, date_from, date_to):
    user = get_user_model().objects.get(pk=user_id)
    summary = ReportGenerator(user, date_from, date_to).get_summary()
    return {
        'income': str(summary['income']),
        'expense': str(summary['expense']),
        'net': str(summary['net']),
        'category_count': len(summary['by_category']),
    }
