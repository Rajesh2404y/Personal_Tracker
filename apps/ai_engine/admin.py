from django.contrib import admin
from .models import AIInsight


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'insight_type', 'title', 'severity', 'is_read', 'created_at')
    list_filter = ('insight_type', 'severity', 'is_read')
    search_fields = ('user__email', 'title')
