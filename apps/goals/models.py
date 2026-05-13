from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class SavingsGoal(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('completed', 'Completed'), ('paused', 'Paused')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    target_date = models.DateField(null=True, blank=True)
    icon = models.CharField(max_length=50, default='bi-piggy-bank')
    color = models.CharField(max_length=7, default='#10b981')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'savings_goals'
        indexes = [models.Index(fields=['user', 'status'])]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.user.email})'

    @property
    def progress_percent(self):
        if self.target_amount == 0:
            return 0
        return min(int((self.current_amount / self.target_amount) * 100), 100)

    @property
    def remaining_amount(self):
        return max(self.target_amount - self.current_amount, Decimal('0'))

    @property
    def is_completed(self):
        return self.current_amount >= self.target_amount
