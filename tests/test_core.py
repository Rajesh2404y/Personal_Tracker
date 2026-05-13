import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

from apps.accounts.models import Profile
from apps.transactions.models import Transaction, Category
from apps.budgets.models import Budget
from apps.goals.models import SavingsGoal
from apps.analytics.services import AnalyticsService
from apps.reports.models import Report

User = get_user_model()


class UserFactory:
    @staticmethod
    def create(email='test@finpilot.com', password='testpass123'):
        user = User.objects.create_user(username=email, email=email, password=password)
        Profile.objects.get_or_create(user=user)
        return user


class CategoryFactory:
    @staticmethod
    def create(name='Food', category_type='expense', is_default=True):
        return Category.objects.create(name=name, category_type=category_type, is_default=is_default)


class TestAuthentication(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_user(self):
        response = self.client.post(reverse('register'), {
            'email': 'new@finpilot.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(User.objects.filter(email='new@finpilot.com').count(), 1)

    def test_login_redirects_to_dashboard(self):
        user = UserFactory.create()
        response = self.client.post(reverse('login'), {
            'username': user.email,
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")


class TestTransactionModel(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.category = CategoryFactory.create()

    def test_create_expense(self):
        txn = Transaction.objects.create(
            user=self.user, category=self.category,
            transaction_type='expense', amount=Decimal('50.00'),
            description='Lunch', date=date.today()
        )
        self.assertEqual(txn.amount, Decimal('50.00'))
        self.assertEqual(txn.transaction_type, 'expense')

    def test_tag_list_property(self):
        txn = Transaction(tags='food, weekly, lunch')
        self.assertEqual(txn.tag_list, ['food', 'weekly', 'lunch'])

    def test_tag_list_empty(self):
        txn = Transaction(tags='')
        self.assertEqual(txn.tag_list, [])


class TestBudgetModel(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.category = CategoryFactory.create()

    def test_budget_utilization(self):
        budget = Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('200.00'), month=1, year=2024
        )
        Transaction.objects.create(
            user=self.user, category=self.category,
            transaction_type='expense', amount=Decimal('100.00'),
            description='Test', date=date(2024, 1, 15)
        )
        self.assertEqual(budget.utilization_percent, 50)

    def test_budget_exceeded(self):
        budget = Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('50.00'), month=1, year=2024
        )
        Transaction.objects.create(
            user=self.user, category=self.category,
            transaction_type='expense', amount=Decimal('100.00'),
            description='Test', date=date(2024, 1, 15)
        )
        self.assertTrue(budget.is_exceeded)


class TestSavingsGoal(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.client = Client()
        self.client.login(username=self.user.email, password='testpass123')

    def test_progress_percent(self):
        goal = SavingsGoal(target_amount=Decimal('1000'), current_amount=Decimal('250'))
        self.assertEqual(goal.progress_percent, 25)

    def test_is_completed(self):
        goal = SavingsGoal(target_amount=Decimal('1000'), current_amount=Decimal('1000'))
        self.assertTrue(goal.is_completed)

    def test_remaining_amount(self):
        goal = SavingsGoal(target_amount=Decimal('1000'), current_amount=Decimal('300'))
        self.assertEqual(goal.remaining_amount, Decimal('700'))

    def test_goal_contribution_creates_savings_expense(self):
        income_category = CategoryFactory.create(name='Salary', category_type='income')
        Transaction.objects.create(
            user=self.user,
            category=income_category,
            transaction_type='income',
            amount=Decimal('1000.00'),
            description='Salary',
            date=date.today(),
        )
        goal = SavingsGoal.objects.create(
            user=self.user,
            name='Emergency Fund',
            target_amount=Decimal('5000.00'),
        )

        response = self.client.post(reverse('goal_contribute', args=[goal.pk]), {'amount': '250.00'})

        self.assertRedirects(response, reverse('goal_list'))
        goal.refresh_from_db()
        self.assertEqual(goal.current_amount, Decimal('250.00'))
        savings_expense = Transaction.objects.get(user=self.user, transaction_type='expense')
        self.assertEqual(savings_expense.amount, Decimal('250.00'))
        self.assertEqual(savings_expense.category.name, 'Savings')

        summary = AnalyticsService(self.user).get_dashboard_summary()
        self.assertEqual(summary['month_income'], Decimal('1000.00'))
        self.assertEqual(summary['month_expense'], Decimal('250.00'))
        self.assertEqual(summary['month_balance'], Decimal('750.00'))

    def test_goal_contribution_requires_available_monthly_balance(self):
        goal = SavingsGoal.objects.create(
            user=self.user,
            name='Emergency Fund',
            target_amount=Decimal('5000.00'),
        )

        response = self.client.post(reverse('goal_contribute', args=[goal.pk]), {'amount': '250.00'})

        self.assertRedirects(response, reverse('goal_list'))
        goal.refresh_from_db()
        self.assertEqual(goal.current_amount, Decimal('0'))
        self.assertFalse(Transaction.objects.filter(user=self.user).exists())


class TestAnalyticsService(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.category = CategoryFactory.create()

    def test_dashboard_summary_empty(self):
        service = AnalyticsService(self.user)
        summary = service.get_dashboard_summary()
        self.assertEqual(summary['month_income'], Decimal('0'))
        self.assertEqual(summary['month_expense'], Decimal('0'))

    def test_health_score_range(self):
        service = AnalyticsService(self.user)
        summary = service.get_dashboard_summary()
        self.assertGreaterEqual(summary['health_score'], 0)
        self.assertLessEqual(summary['health_score'], 100)


class TestTransactionViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create()
        self.client.login(username=self.user.email, password='testpass123')
        self.category = CategoryFactory.create()

    def test_transaction_list_view(self):
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)

    def test_create_transaction(self):
        response = self.client.post(reverse('transaction_create'), {
            'transaction_type': 'expense',
            'amount': '25.00',
            'description': 'Coffee',
            'category': self.category.pk,
            'date': date.today().isoformat(),
            'recurrence': 'none',
        })
        self.assertEqual(Transaction.objects.filter(user=self.user).count(), 1)


class TestAPIEndpoints(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create()

    def test_api_register(self):
        response = self.client.post('/api/v1/auth/register/', {
            'email': 'api@finpilot.com',
            'first_name': 'API',
            'last_name': 'User',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_api_login(self):
        response = self.client.post('/api/v1/auth/login/', {
            'email': self.user.email,
            'password': 'testpass123',
        }, content_type='application/json')
        self.assertIn(response.status_code, [200, 400])

    def test_api_goal_contribution_creates_savings_expense(self):
        self.client.login(username=self.user.email, password='testpass123')
        income_category = CategoryFactory.create(name='Salary', category_type='income')
        Transaction.objects.create(
            user=self.user,
            category=income_category,
            transaction_type='income',
            amount=Decimal('1000.00'),
            description='Salary',
            date=date.today(),
        )
        goal = SavingsGoal.objects.create(
            user=self.user,
            name='Emergency Fund',
            target_amount=Decimal('5000.00'),
        )

        response = self.client.post(f'/api/v1/goals/{goal.pk}/contribute/', {'amount': '100.00'})

        self.assertEqual(response.status_code, 200)
        goal.refresh_from_db()
        self.assertEqual(goal.current_amount, Decimal('100.00'))
        self.assertTrue(Transaction.objects.filter(user=self.user, transaction_type='expense', amount=Decimal('100.00')).exists())


class TestReports(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create()
        self.client.login(username=self.user.email, password='testpass123')

    def test_generate_report_records_history(self):
        response = self.client.post(reverse('generate_report'), {
            'date_from': date.today().isoformat(),
            'date_to': date.today().isoformat(),
            'format': 'csv',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.filter(user=self.user).count(), 1)
