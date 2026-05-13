from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/data/', views.analytics_api, name='analytics_api'),
    path('api/kpis/', views.dashboard_kpis, name='dashboard_kpis'),
]
