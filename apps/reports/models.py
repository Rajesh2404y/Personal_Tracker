from django.db import models
from django.conf import settings


class Report(models.Model):
    REPORT_TYPES = [('monthly', 'Monthly'), ('yearly', 'Yearly'), ('custom', 'Custom')]
    FORMAT_CHOICES = [('pdf', 'PDF'), ('csv', 'CSV'), ('excel', 'Excel')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    format = models.CharField(max_length=5, choices=FORMAT_CHOICES)
    title = models.CharField(max_length=200)
    date_from = models.DateField()
    date_to = models.DateField()
    file = models.FileField(upload_to='reports/%Y/%m/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports'
        indexes = [
            models.Index(fields=['user', 'created_at'], name='report_user_created_idx'),
            models.Index(fields=['user', 'date_from', 'date_to'], name='report_user_range_idx'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.format})'
