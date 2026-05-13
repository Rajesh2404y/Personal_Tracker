from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.budgets.models import Budget
from apps.core.cache import bump_user_cache_version
from apps.goals.models import SavingsGoal
from apps.transactions.models import Transaction


def _invalidate(instance):
    user_id = getattr(instance, 'user_id', None)
    if user_id:
        bump_user_cache_version(user_id)


@receiver([post_save, post_delete], sender=Transaction)
def invalidate_transaction_cache(sender, instance, **kwargs):
    _invalidate(instance)


@receiver([post_save, post_delete], sender=Budget)
def invalidate_budget_cache(sender, instance, **kwargs):
    _invalidate(instance)


@receiver([post_save, post_delete], sender=SavingsGoal)
def invalidate_goal_cache(sender, instance, **kwargs):
    _invalidate(instance)
