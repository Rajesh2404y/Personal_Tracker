from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    CATEGORY_TYPES = [('income', 'Income'), ('expense', 'Expense')]
    ICON_CHOICES = [
        ('bi-cart', 'Shopping'), ('bi-house', 'Housing'), ('bi-car-front', 'Transport'),
        ('bi-heart-pulse', 'Health'), ('bi-mortarboard', 'Education'), ('bi-controller', 'Entertainment'),
        ('bi-cup-hot', 'Food & Dining'), ('bi-briefcase', 'Business'), ('bi-piggy-bank', 'Savings'),
        ('bi-cash-stack', 'Income'), ('bi-three-dots', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, default='bi-three-dots')
    color = models.CharField(max_length=7, default='#6366f1')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        indexes = [models.Index(fields=['user', 'category_type'])]
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.category_type})'


class Transaction(models.Model):
    TRANSACTION_TYPES = [('income', 'Income'), ('expense', 'Expense')]
    RECURRENCE_CHOICES = [
        ('none', 'None'), ('daily', 'Daily'), ('weekly', 'Weekly'),
        ('monthly', 'Monthly'), ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    date = models.DateField()
    receipt = models.ImageField(upload_to='receipts/%Y/%m/', null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'transaction_type', 'date'], name='txn_user_type_date_idx'),
            models.Index(fields=['user', 'category', 'date'], name='txn_user_cat_date_idx'),
            models.Index(fields=['user', 'date', 'created_at'], name='txn_user_date_created_idx'),
        ]
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.transaction_type}: {self.amount} - {self.description}'

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]
