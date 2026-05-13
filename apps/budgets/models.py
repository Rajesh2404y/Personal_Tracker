from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Budget(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('exceeded', 'Exceeded'), ('completed', 'Completed')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey('transactions.Category', on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    alert_threshold = models.PositiveIntegerField(default=80, help_text='Alert when % of budget is used')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'budgets'
        unique_together = ('user', 'category', 'month', 'year')
        indexes = [
            models.Index(fields=['user', 'year', 'month']),
            models.Index(fields=['user', 'category', 'year', 'month'], name='budget_user_cat_ym_idx'),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.category.name} ({self.month}/{self.year})'

    @property
    def spent(self):
        # Use pre-annotated value if available (avoids N+1 when bulk-fetched)
        if hasattr(self, '_spent_annotated'):
            return self._spent_annotated or Decimal('0')
        from apps.transactions.models import Transaction
        from django.db.models import Sum
        result = Transaction.objects.filter(
            user=self.user, category=self.category,
            transaction_type='expense',
            date__month=self.month, date__year=self.year,
        ).aggregate(total=Sum('amount'))['total']
        return result or Decimal('0')

    @property
    def remaining(self):
        return self.amount - self.spent

    @property
    def utilization_percent(self):
        if self.amount == 0:
            return 0
        return min(int((self.spent / self.amount) * 100), 100)

    @property
    def is_exceeded(self):
        return self.spent > self.amount
