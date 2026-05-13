from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from apps.transactions.models import Transaction
from apps.budgets.models import Budget
from .models import AIInsight


class InsightEngine:
    """
    Rule-based AI insight engine.
    All budget data is fetched in ONE query with pre-aggregated spend —
    no N+1 loops. Architecture supports future OpenAI integration.
    """

    def __init__(self, user):
        self.user = user
        self.now = timezone.now()

    # ── Public API ────────────────────────────────────────────

    def refresh_insights(self):
        """
        Only regenerate insights once per hour per user.
        Skips all DB writes if insights are fresh.
        """
        from django.utils import timezone as tz
        from datetime import timedelta
        cutoff = tz.now() - timedelta(hours=1)
        if AIInsight.objects.filter(user=self.user, created_at__gte=cutoff).exists():
            return list(AIInsight.objects.filter(user=self.user, is_read=False)[:5])

        new_insights = self.generate_all_insights()
        AIInsight.objects.filter(user=self.user, is_read=False).delete()
        if new_insights:
            AIInsight.objects.bulk_create(new_insights)
        return new_insights

    def generate_all_insights(self):
        insights = []
        # Fetch all data needed in bulk — single pass
        budgets, spent_map = self._fetch_budgets_with_spend()
        income, expense = self._fetch_month_totals()

        insights.extend(self._budget_alerts(budgets, spent_map))
        insights.extend(self._spending_trends())
        insights.extend(self._savings_tips(income, expense))
        insights.extend(self._monthly_summary())
        return insights

    # ── Data fetchers (minimal queries) ──────────────────────

    def _fetch_budgets_with_spend(self):
        """Fetch budgets + their spend in exactly 2 queries."""
        budgets = list(
            Budget.objects.filter(
                user=self.user, month=self.now.month, year=self.now.year
            ).select_related('category')
        )
        if not budgets:
            return budgets, {}

        category_ids = [b.category_id for b in budgets]
        spent_rows = Transaction.objects.filter(
            user=self.user,
            transaction_type='expense',
            date__month=self.now.month,
            date__year=self.now.year,
            category_id__in=category_ids,
        ).values('category_id').annotate(total=Sum('amount'))

        spent_map = {row['category_id']: row['total'] or Decimal('0') for row in spent_rows}
        return budgets, spent_map

    def _fetch_month_totals(self):
        """Fetch income + expense for current month in ONE query."""
        rows = Transaction.objects.filter(
            user=self.user,
            date__month=self.now.month,
            date__year=self.now.year,
        ).values('transaction_type').annotate(total=Sum('amount'))

        totals = {r['transaction_type']: r['total'] or Decimal('0') for r in rows}
        return totals.get('income', Decimal('0')), totals.get('expense', Decimal('0'))

    # ── Insight generators ────────────────────────────────────

    def _budget_alerts(self, budgets, spent_map):
        insights = []
        for budget in budgets:
            spent = spent_map.get(budget.category_id, Decimal('0'))
            if budget.amount == 0:
                continue
            pct = min(int((spent / budget.amount) * 100), 100)
            remaining = budget.amount - spent

            if spent > budget.amount:
                insights.append(AIInsight(
                    user=self.user, insight_type='spending_alert', severity='danger',
                    title=f'Budget Exceeded: {budget.category.name}',
                    message=f'You exceeded your {budget.category.name} budget by ${spent - budget.amount:.2f}.',
                    data={'budget_id': budget.id, 'utilization': pct}
                ))
            elif pct >= budget.alert_threshold:
                insights.append(AIInsight(
                    user=self.user, insight_type='budget_recommendation', severity='warning',
                    title=f'Budget Alert: {budget.category.name}',
                    message=f'You have used {pct}% of your {budget.category.name} budget. ${remaining:.2f} remaining.',
                    data={'budget_id': budget.id, 'utilization': pct}
                ))
        return insights

    def _spending_trends(self):
        """Compare this month vs last month — 2 aggregates in ONE query."""
        last_month = (self.now.replace(day=1) - timezone.timedelta(days=1))
        rows = Transaction.objects.filter(
            user=self.user,
            transaction_type='expense',
            date__year__in=[self.now.year, last_month.year],
        ).values('date__year', 'date__month').annotate(total=Sum('amount'))

        monthly = {(r['date__year'], r['date__month']): r['total'] or Decimal('0') for r in rows}
        current = monthly.get((self.now.year, self.now.month), Decimal('0'))
        previous = monthly.get((last_month.year, last_month.month), Decimal('0'))

        if previous == 0:
            return []

        change_pct = ((current - previous) / previous) * 100
        if change_pct > 20:
            return [AIInsight(
                user=self.user, insight_type='trend_analysis', severity='warning',
                title='Spending Increased This Month',
                message=f'Spending is {change_pct:.1f}% higher than last month (${current:.2f} vs ${previous:.2f}).',
                data={'change_percent': float(change_pct)}
            )]
        elif change_pct < -10:
            return [AIInsight(
                user=self.user, insight_type='trend_analysis', severity='success',
                title='Great Job! Spending Decreased',
                message=f'Spending is {abs(change_pct):.1f}% lower than last month. Keep it up!',
                data={'change_percent': float(change_pct)}
            )]
        return []

    def _savings_tips(self, income, expense):
        if income == 0:
            return []
        savings_rate = ((income - expense) / income) * 100
        if savings_rate < 10:
            return [AIInsight(
                user=self.user, insight_type='savings_tip', severity='warning',
                title='Low Savings Rate',
                message=f'Your savings rate is {savings_rate:.1f}%. Aim for at least 20% of income.',
                data={'savings_rate': float(savings_rate)}
            )]
        elif savings_rate >= 20:
            return [AIInsight(
                user=self.user, insight_type='savings_tip', severity='success',
                title='Excellent Savings Rate!',
                message=f'You are saving {savings_rate:.1f}% of your income. On track for financial health!',
                data={'savings_rate': float(savings_rate)}
            )]
        return []

    def _monthly_summary(self):
        if self.now.day != 1:
            return []
        last_month = self.now.replace(day=1) - timezone.timedelta(days=1)
        rows = Transaction.objects.filter(
            user=self.user,
            date__month=last_month.month,
            date__year=last_month.year,
        ).values('transaction_type').annotate(total=Sum('amount'))
        totals = {r['transaction_type']: r['total'] or Decimal('0') for r in rows}
        income = totals.get('income', Decimal('0'))
        expense = totals.get('expense', Decimal('0'))
        return [AIInsight(
            user=self.user, insight_type='monthly_summary', severity='info',
            title=f'Monthly Summary: {last_month.strftime("%B %Y")}',
            message=f'Income: ${income:.2f} | Expenses: ${expense:.2f} | Net: ${income - expense:.2f}',
            data={'income': float(income), 'expense': float(expense), 'net': float(income - expense)}
        )]
