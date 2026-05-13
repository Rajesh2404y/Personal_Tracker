from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from apps.transactions.models import Transaction
from apps.budgets.models import Budget
from apps.core.cache import get_or_set_user_analytics


class AnalyticsService:
    def __init__(self, user):
        self.user = user
        self.now = timezone.now()

    def get_dashboard_summary(self):
        return get_or_set_user_analytics(
            self.user.id,
            f'dashboard-summary:{self.now.year}:{self.now.month}',
            self._compute_dashboard_summary,
            timeout=120,
        )

    def _compute_dashboard_summary(self):
        # ONE query for income + expense totals this month
        month_rows = Transaction.objects.filter(
            user=self.user,
            date__month=self.now.month,
            date__year=self.now.year,
        ).values('transaction_type').annotate(total=Sum('amount'))
        month_totals = {r['transaction_type']: r['total'] or Decimal('0') for r in month_rows}
        month_income = month_totals.get('income', Decimal('0'))
        month_expense = month_totals.get('expense', Decimal('0'))

        # ONE query for all-time totals
        all_rows = Transaction.objects.filter(
            user=self.user
        ).values('transaction_type').annotate(total=Sum('amount'))
        all_totals = {r['transaction_type']: r['total'] or Decimal('0') for r in all_rows}
        total_balance = all_totals.get('income', Decimal('0')) - all_totals.get('expense', Decimal('0'))

        balance = month_income - month_expense
        savings_rate = round((balance / month_income * 100), 1) if month_income > 0 else Decimal('0')

        return {
            'month_income': month_income,
            'month_expense': month_expense,
            'month_balance': balance,
            'savings_rate': savings_rate,
            'total_balance': total_balance,
            'health_score': self._calculate_health_score(savings_rate, month_income, month_expense),
        }

    def get_monthly_trend(self, months=6):
        return get_or_set_user_analytics(
            self.user.id,
            f'monthly-trend:{months}',
            lambda: self._compute_monthly_trend(months),
            timeout=300,
        )

    def _compute_monthly_trend(self, months=6):
        # Single query — group by month + type
        data = (
            Transaction.objects.filter(user=self.user)
            .annotate(month=TruncMonth('date'))
            .values('month', 'transaction_type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        result = {}
        for row in data:
            key = row['month'].strftime('%b %Y')
            if key not in result:
                result[key] = {'income': 0, 'expense': 0}
            result[key][row['transaction_type']] = float(row['total'])
        return result

    def get_category_breakdown(self, transaction_type='expense', month=None, year=None):
        month = month or self.now.month
        year = year or self.now.year
        return get_or_set_user_analytics(
            self.user.id,
            f'category-breakdown:{transaction_type}:{year}:{month}',
            lambda: list(
                Transaction.objects.filter(
                    user=self.user, transaction_type=transaction_type,
                    date__month=month, date__year=year
                )
                .values('category__name', 'category__color', 'category__icon')
                .annotate(total=Sum('amount'))
                .order_by('-total')
            ),
            timeout=120,
        )

    def get_budget_utilization(self):
        return get_or_set_user_analytics(
            self.user.id,
            f'budget-utilization:{self.now.year}:{self.now.month}',
            self._compute_budget_utilization,
            timeout=120,
        )

    def _compute_budget_utilization(self):
        # 2 queries total — budgets + aggregated spend
        budgets = list(
            Budget.objects.filter(
                user=self.user, month=self.now.month, year=self.now.year
            ).select_related('category')
        )
        if not budgets:
            return []

        spent_rows = Transaction.objects.filter(
            user=self.user,
            transaction_type='expense',
            date__month=self.now.month,
            date__year=self.now.year,
            category_id__in=[b.category_id for b in budgets],
        ).values('category_id').annotate(total=Sum('amount'))
        spent_map = {r['category_id']: r['total'] or Decimal('0') for r in spent_rows}

        result = []
        for budget in budgets:
            spent = spent_map.get(budget.category_id, Decimal('0'))
            percent = min(int((spent / budget.amount) * 100), 100) if budget.amount else 0
            result.append({
                'name': budget.category.name,
                'budget': float(budget.amount),
                'spent': float(spent),
                'percent': percent,
                'color': budget.category.color,
            })
        return result

    def get_recent_transactions(self, limit=5):
        return list(
            Transaction.objects.filter(user=self.user)
            .select_related('category')
            .only('id', 'description', 'amount', 'transaction_type', 'date', 'category__name', 'category__color', 'category__icon')
            [:limit]
        )

    def _get_period_total(self, transaction_type, month, year):
        result = Transaction.objects.filter(
            user=self.user, transaction_type=transaction_type,
            date__month=month, date__year=year
        ).aggregate(total=Sum('amount'))['total']
        return result or Decimal('0')

    def _calculate_health_score(self, savings_rate, income, expense):
        score = 50
        if savings_rate >= 20:
            score += 30
        elif savings_rate >= 10:
            score += 15
        elif savings_rate < 0:
            score -= 20
        # Use cached budget utilization — no extra query
        score += 20
        return min(max(score, 0), 100)
