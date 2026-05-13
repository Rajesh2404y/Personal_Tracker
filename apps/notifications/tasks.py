from celery import shared_task

from apps.notifications.models import Notification


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def create_notification(self, user_id, notification_type, title, message):
    notification = Notification.objects.create(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
    )
    return notification.pk
