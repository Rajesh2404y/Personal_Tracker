from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone

from apps.goals.models import SavingsGoal
from apps.transactions.models import Category, Transaction


class InsufficientMonthlyBalance(ValueError):
    pass


class InvalidContributionAmount(ValueError):
    pass


def monthly_transaction_total(user, transaction_type, date_value):
    return (
        Transaction.objects.filter(
            user=user,
            transaction_type=transaction_type,
            date__month=date_value.month,
            date__year=date_value.year,
        ).aggregate(total=Sum('amount'))['total']
        or Decimal('0')
    )


def available_monthly_balance(user, date_value=None):
    date_value = date_value or timezone.localdate()
    income = monthly_transaction_total(user, 'income', date_value)
    expense = monthly_transaction_total(user, 'expense', date_value)
    return income - expense


def get_savings_category(user):
    category, _ = Category.objects.get_or_create(
        user=user,
        name='Savings',
        category_type='expense',
        defaults={'icon': 'bi-piggy-bank', 'color': '#10b981'},
    )
    return category


@transaction.atomic
def create_transaction(*, user, category, transaction_type, amount, description, date, notes='', tags='', recurrence='none', receipt=None):
    return Transaction.objects.create(
        user=user,
        category=category,
        transaction_type=transaction_type,
        amount=amount,
        description=description,
        date=date,
        notes=notes,
        tags=tags,
        recurrence=recurrence,
        receipt=receipt,
    )


@transaction.atomic
def contribute_to_goal(*, user, goal_id, amount, date_value=None):
    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        raise InvalidContributionAmount('Enter a valid contribution amount.')

    if amount <= 0:
        raise InvalidContributionAmount('Contribution amount must be greater than zero.')

    date_value = date_value or timezone.localdate()
    goal = SavingsGoal.objects.select_for_update().get(pk=goal_id, user=user)

    balance = available_monthly_balance(user, date_value)
    if amount > balance:
        raise InsufficientMonthlyBalance(f'Not enough available monthly balance. Available: {balance}.')

    savings_category = get_savings_category(user)
    contribution = Transaction.objects.create(
        user=user,
        category=savings_category,
        transaction_type='expense',
        amount=amount,
        description=f'Contribution to goal: {goal.name}',
        notes='Automatically created from savings goal contribution.',
        date=date_value,
        tags='savings,goal',
    )

    goal.current_amount += amount
    if goal.current_amount >= goal.target_amount:
        goal.status = 'completed'
    goal.save(update_fields=['current_amount', 'status', 'updated_at'])
    return goal, contribution


def user_visible_category_queryset(user):
    return Category.objects.filter(Q(user=user) | Q(is_default=True))
