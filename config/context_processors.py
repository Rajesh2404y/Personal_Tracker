from django.conf import settings


def global_context(request):
    return {
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '$'),
        'CURRENCY_CODE': getattr(settings, 'CURRENCY_CODE', 'USD'),
        'APP_NAME': 'FinPilot',
    }
