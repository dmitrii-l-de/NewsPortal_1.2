from .celery import app as celery_app
# Также, согласно рекомендациям из документации к Celery, мы должны добавить следующие
# строки в файл __init__.py (рядом с settings.py):
__all__ = ('celery_app',)