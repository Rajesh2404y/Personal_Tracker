from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction as db_transaction
from .models import Transaction, Category
from .forms import TransactionForm
from .repository import TransactionRepository


@login_required
def transaction_list(request):
    filters = {
        'transaction_type': request.GET.get('type'),
        'category': request.GET.get('category'),
        'date_from': request.GET.get('date_from'),
        'date_to': request.GET.get('date_to'),
        'search': request.GET.get('search'),
    }
    transactions = TransactionRepository.get_user_transactions(request.user, filters)
    paginator = Paginator(transactions, 20)
    page = paginator.get_page(request.GET.get('page'))
    categories = list(TransactionRepository.get_categories(request.user).only('id', 'name', 'category_type'))
    return render(request, 'transactions/list.html', {
        'page_obj': page,
        'categories': categories,
        'filters': filters,
    })


@login_required
def transaction_create(request):
    form = TransactionForm(request.user, request.POST or None, request.FILES or None)
    if form.is_valid():
        with db_transaction.atomic():
            txn = form.save(commit=False)
            txn.user = request.user
            txn.save()
        messages.success(request, 'Transaction added successfully.')
        if request.headers.get('HX-Request'):
            return render(request, 'partials/transaction_row.html', {'transaction': txn})
        return redirect('transaction_list')
    return render(request, 'transactions/form.html', {'form': form, 'title': 'Add Transaction'})


@login_required
def transaction_edit(request, pk):
    txn = get_object_or_404(Transaction.objects.select_related('category'), pk=pk, user=request.user)
    form = TransactionForm(request.user, request.POST or None, request.FILES or None, instance=txn)
    if form.is_valid():
        with db_transaction.atomic():
            form.save()
        messages.success(request, 'Transaction updated.')
        return redirect('transaction_list')
    return render(request, 'transactions/form.html', {'form': form, 'title': 'Edit Transaction', 'transaction': txn})


@login_required
def transaction_delete(request, pk):
    txn = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        with db_transaction.atomic():
            txn.delete()
        messages.success(request, 'Transaction deleted.')
        if request.headers.get('HX-Request'):
            return render(request, 'partials/empty.html')
        return redirect('transaction_list')
    return render(request, 'transactions/confirm_delete.html', {'transaction': txn})


@login_required
def category_list(request):
    categories = TransactionRepository.get_categories(request.user)
    return render(request, 'transactions/categories.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_type = request.POST.get('category_type')
        color = request.POST.get('color', '#6366f1')
        icon = request.POST.get('icon', 'bi-three-dots')
        if name and category_type in ('income', 'expense'):
            Category.objects.create(
                user=request.user, name=name,
                category_type=category_type, color=color, icon=icon
            )
            messages.success(request, f'Category "{name}" created.')
        else:
            messages.error(request, 'Name and type are required.')
    return redirect('category_list')
