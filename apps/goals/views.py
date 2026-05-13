from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SavingsGoal
from apps.core.finance import (
    InsufficientMonthlyBalance,
    InvalidContributionAmount,
    contribute_to_goal,
)


@login_required
def goal_list(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    active = goals.filter(status='active')
    completed = goals.filter(status='completed')
    return render(request, 'goals/list.html', {'active_goals': active, 'completed_goals': completed})


@login_required
def goal_create(request):
    if request.method == 'POST':
        SavingsGoal.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            target_amount=request.POST.get('target_amount'),
            target_date=request.POST.get('target_date') or None,
            icon=request.POST.get('icon', 'bi-piggy-bank'),
            color=request.POST.get('color', '#10b981'),
        )
        messages.success(request, 'Savings goal created!')
        return redirect('goal_list')
    return render(request, 'goals/form.html', {'title': 'Create Goal'})


@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.name = request.POST.get('name', goal.name)
        goal.description = request.POST.get('description', goal.description)
        goal.target_amount = request.POST.get('target_amount', goal.target_amount)
        goal.target_date = request.POST.get('target_date') or None
        goal.icon = request.POST.get('icon', goal.icon)
        goal.color = request.POST.get('color', goal.color)
        goal.save()
        messages.success(request, 'Goal updated.')
        return redirect('goal_list')
    return render(request, 'goals/form.html', {'title': 'Edit Goal', 'goal': goal})


@login_required
def goal_contribute(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            updated_goal, contribution = contribute_to_goal(
                user=request.user,
                goal_id=goal.pk,
                amount=request.POST.get('amount', '0'),
            )
        except (InvalidContributionAmount, InsufficientMonthlyBalance) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(
                request,
                f'Added {contribution.amount} to {updated_goal.name} and deducted it from monthly balance.'
            )
    return redirect('goal_list')


@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted.')
    return redirect('goal_list')
