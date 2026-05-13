from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from apps.analytics.views import home


def health_check(request):
    """Lightweight health check for Docker/load balancer probes."""
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('', home, name='home'),
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.analytics.urls')),
    path('transactions/', include('apps.transactions.urls')),
    path('budgets/', include('apps.budgets.urls')),
    path('goals/', include('apps.goals.urls')),
    path('reports/', include('apps.reports.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('api/v1/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
