# Celery tasks — stubbed for local dev (no broker required)
# To enable async tasks, install celery+redis and uncomment below

# from celery import shared_task
# from django.contrib.auth import get_user_model
# from apps.ai_engine.engine import InsightEngine
#
# @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
# def refresh_user_insights(self, user_id):
#     user = get_user_model().objects.get(pk=user_id)
#     return len(InsightEngine(user).refresh_insights())
