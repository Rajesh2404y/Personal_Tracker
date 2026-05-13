from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='api-category')
router.register('transactions', views.TransactionViewSet, basename='api-transaction')
router.register('budgets', views.BudgetViewSet, basename='api-budget')
router.register('goals', views.SavingsGoalViewSet, basename='api-goal')
router.register('insights', views.AIInsightViewSet, basename='api-insight')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='api-register'),
    path('auth/login/', views.LoginView.as_view(), name='api-token-obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='api-token-blacklist'),
    path('auth/me/', views.MeView.as_view(), name='api-me'),
    path('analytics/', views.AnalyticsSummaryView.as_view(), name='api-analytics'),
    path('', include(router.urls)),
]
