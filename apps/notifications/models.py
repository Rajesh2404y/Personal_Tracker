from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('budget_alert', 'Budget Alert'),
        ('goal_milestone', 'Goal Milestone'),
        ('monthly_summary', 'Monthly Summary'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        indexes = [models.Index(fields=['user', 'is_read'])]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.notification_type}: {self.title}'
