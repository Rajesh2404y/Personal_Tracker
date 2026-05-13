from django.db import models
from django.conf import settings


class AIInsight(models.Model):
    INSIGHT_TYPES = [
        ('spending_alert', 'Spending Alert'),
        ('budget_recommendation', 'Budget Recommendation'),
        ('savings_tip', 'Savings Tip'),
        ('monthly_summary', 'Monthly Summary'),
        ('trend_analysis', 'Trend Analysis'),
    ]
    SEVERITY_CHOICES = [('info', 'Info'), ('warning', 'Warning'), ('success', 'Success'), ('danger', 'Danger')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_insights'
        indexes = [models.Index(fields=['user', 'is_read', 'created_at'])]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.insight_type}: {self.title}'
