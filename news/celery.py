# В первую очередь мы импортируем библиотеку для взаимодействия с операционной
# системой и саму библиотеку Celery.
import os
from celery import Celery
# Второй строчкой мы связываем настройки Django с настройками Celery через переменную окружения.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news.settings')
# Далее мы создаём экземпляр приложения Celery и устанавливаем для него файл конфигурации.
# Мы также указываем пространство имён, чтобы Celery сам находил все необходимые настройки в
# общем конфигурационном файле settings.py. Он их будет искать по шаблону «CELERY_***».
app = Celery('news')
app.config_from_object('django.conf:settings', namespace='CELERY')
# Последней строчкой мы указываем Celery автоматически искать задания в файлах tasks.py
# каждого приложения проекта
app.autodiscover_tasks()

# Также, согласно рекомендациям из документации к Celery, мы должны добавить следующие
# строки в файл __init__.py (рядом с settings.py)


app.conf.beat_schedule = {
    'send_mailing_monday_8am': {
        'task': 'project.tasks.send_weekly',
        'schedule': crontab(hour=8, minute=0, day_of_week='mon'),

    },
}

