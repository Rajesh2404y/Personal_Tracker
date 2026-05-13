from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction as db_transaction
from django.db.models import Q, Sum, OuterRef, Subquery, DecimalField, Value
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.transactions.models import Transaction, Category
from apps.budgets.models import Budget
from apps.goals.models import SavingsGoal
from apps.ai_engine.models import AIInsight
from apps.ai_engine.engine import InsightEngine
from apps.analytics.services import AnalyticsService
from apps.core.finance import (
    InsufficientMonthlyBalance,
    InvalidContributionAmount,
    contribute_to_goal,
)
from .serializers import (
    RegisterSerializer, UserSerializer, CategorySerializer,
    TransactionSerializer, BudgetSerializer, SavingsGoalSerializer, AIInsightSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth'


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth'


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return (
            Category.objects
            .filter(Q(user=self.request.user) | Q(is_default=True))
            .only('id', 'name', 'category_type', 'icon', 'color', 'is_default')
        )

    def perform_create(self, serializer):
        with db_transaction.atomic():
            serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['transaction_type', 'category', 'date']
    search_fields = ['description', 'notes', 'tags']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        qs = (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related('category')
            .only(
                'id', 'transaction_type', 'amount', 'description', 'notes',
                'date', 'tags', 'recurrence', 'is_recurring', 'created_at',
                'category__name', 'category__color',
            )
        )
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def perform_create(self, serializer):
        with db_transaction.atomic():
            serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['month', 'year', 'category']

    def get_queryset(self):
        from django.utils import timezone
        now = timezone.now()
        # Annotate each budget with its spent amount — eliminates N+1 on serializer
        spent_subquery = (
            Transaction.objects
            .filter(
                user=self.request.user,
                category=OuterRef('category'),
                transaction_type='expense',
                date__month=OuterRef('month'),
                date__year=OuterRef('year'),
            )
            .values('category')
            .annotate(total=Sum('amount'))
            .values('total')
        )
        return (
            Budget.objects
            .filter(user=self.request.user)
            .select_related('category')
            .annotate(
                _spent_annotated=Coalesce(
                    Subquery(spent_subquery, output_field=DecimalField()),
                    Value(0, output_field=DecimalField()),
                )
            )
        )

    def perform_create(self, serializer):
        with db_transaction.atomic():
            serializer.save(user=self.request.user)


class SavingsGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsGoalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with db_transaction.atomic():
            serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
        try:
            goal, _ = contribute_to_goal(
                user=request.user,
                goal_id=self.get_object().pk,
                amount=request.data.get('amount', 0),
            )
            return Response(SavingsGoalSerializer(goal).data)
        except (InvalidContributionAmount, InsufficientMonthlyBalance) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AIInsightViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AIInsightSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['insight_type', 'severity', 'is_read']

    def get_queryset(self):
        return AIInsight.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        try:
            from apps.ai_engine.tasks import refresh_user_insights
            refresh_user_insights.delay(request.user.id)
            return Response({'status': 'queued'})
        except Exception:
            engine = InsightEngine(request.user)
            insights = engine.refresh_insights()
            return Response({'generated': len(insights)})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        AIInsight.objects.filter(pk=pk, user=request.user).update(is_read=True)
        return Response({'status': 'ok'})


class AnalyticsSummaryView(APIView):
    def get(self, request):
        service = AnalyticsService(request.user)
        summary, monthly_trend, category_breakdown, budget_utilization = service.get_all_dashboard_data()
        return Response({
            'summary': {k: float(v) if hasattr(v, '__float__') else v for k, v in summary.items()},
            'monthly_trend': monthly_trend,
            'category_breakdown': [
                {
                    'name': c['category__name'] or 'Uncategorized',
                    'total': float(c['total']),
                    'color': c['category__color'],
                }
                for c in category_breakdown
            ],
            'budget_utilization': budget_utilization,
        })
