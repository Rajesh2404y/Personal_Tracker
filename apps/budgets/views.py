from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction as db_transaction
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Budget
from apps.transactions.models import Category, Transaction


@login_required
def budget_list(request):
    now = timezone.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))

    budgets = list(
        Budget.objects.filter(user=request.user, month=month, year=year)
        .select_related('category')
        .only('id', 'amount', 'month', 'year', 'alert_threshold',
              'category__id', 'category__name', 'category__color', 'category__icon')
    )

    # Single aggregation query for all spend — no per-budget queries
    if budgets:
        spent_rows = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            date__month=month,
            date__year=year,
            category_id__in=[b.category_id for b in budgets],
        ).values('category_id').annotate(total=Sum('amount'))
        spent_map = {r['category_id']: r['total'] or 0 for r in spent_rows}
        for budget in budgets:
            budget.spent_amount = spent_map.get(budget.category_id, 0)

    categories = list(
        Category.objects.filter(category_type='expense')
        .filter(Q(user=request.user) | Q(is_default=True))
        .only('id', 'name')
    )
    return render(request, 'budgets/list.html', {
        'budgets': budgets,
        'month': month,
        'year': year,
        'categories': categories,
        'months': range(1, 13),
        'years': range(now.year - 2, now.year + 2),
    })


@login_required
def budget_create(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        month = request.POST.get('month')
        year = request.POST.get('year')
        alert_threshold = request.POST.get('alert_threshold', 80)
        category = get_object_or_404(
            Category.objects.filter(category_type='expense').filter(Q(user=request.user) | Q(is_default=True)),
            pk=category_id,
        )
        with db_transaction.atomic():
            budget, created = Budget.objects.update_or_create(
                user=request.user, category=category, month=month, year=year,
                defaults={'amount': amount, 'alert_threshold': alert_threshold}
            )
        messages.success(request, f'Budget {"created" if created else "updated"} successfully.')
    return redirect('budget_list')


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        with db_transaction.atomic():
            budget.delete()
        messages.success(request, 'Budget deleted.')
    return redirect('budget_list')
