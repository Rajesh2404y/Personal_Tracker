from django.db.models import Q
from .models import Transaction, Category


class TransactionRepository:
    @staticmethod
    def get_user_transactions(user, filters=None):
        qs = Transaction.objects.filter(user=user).select_related('category')
        if not filters:
            return qs
        if filters.get('transaction_type'):
            qs = qs.filter(transaction_type=filters['transaction_type'])
        if filters.get('category'):
            qs = qs.filter(category_id=filters['category'])
        if filters.get('date_from'):
            qs = qs.filter(date__gte=filters['date_from'])
        if filters.get('date_to'):
            qs = qs.filter(date__lte=filters['date_to'])
        if filters.get('search'):
            qs = qs.filter(
                Q(description__icontains=filters['search']) |
                Q(notes__icontains=filters['search']) |
                Q(tags__icontains=filters['search'])
            )
        return qs

    @staticmethod
    def get_categories(user):
        return Category.objects.filter(Q(user=user) | Q(is_default=True))
