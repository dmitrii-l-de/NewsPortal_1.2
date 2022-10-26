import logging
from datetime import datetime, timedelta
from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from project.models import Category

logger = logging.getLogger(__name__)


def send_weekly_mail(post, category) -> None:
    # Реализация переодической еженедельной рассылки всех новостей из категорий на которые
    # подписан пользователь
    # собираем аудиторию подписчиков
    for user in category.subscribers.all():
        if user.email == "" or user.email is None:
            return

        html = render_to_string(
            "weekly_posts.html",
            {
                "category": category,
                "post": post,
                "user": user,
            },
        )

        msg = EmailMultiAlternatives(
            subject=f"Новые посты в категории {category.category_name} за прошлую неделю.",
            body=html,
            from_email='gbicfo@yandex.ru',
            to=[user.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()


def my_job():
    # задача по еженедельной рассылке
    for category in Category.objects.all():
        # собираем все посты в промежутке недели
        posts = category.post_set.filter(pub_date__gte=datetime.now() - timedelta(minutes=604800))
        if posts.count() != 0:
            send_weekly_mail(posts, category)
    print("job done")

# # наша задача по выводу текста на экран
# def my_job():
#     #  Your job processing logic here...
#     print('hello from job')
#
#
# # функция, которая будет удалять неактуальные задачи
# def delete_old_job_executions(max_age=604_800):
#     """This job deletes all apscheduler job executions older than `max_age` from the database."""
#     DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/10"), # здесь выставляем время повторения задачи
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")
        #
        # scheduler.add_job(
        #     delete_old_job_executions,
        #     trigger=CronTrigger(
        #         day_of_week="mon", hour="00", minute="00"
        #     ),
        #     # Каждую неделю будут удаляться старые задачи, которые либо не удалось
        #     выполнить, либо уже выполнять не надо.
        #     id="delete_old_job_executions",
        #     max_instances=1,
        #     replace_existing=True,
        # )
        # logger.info(
        #     "Added weekly job: 'delete_old_job_executions'."
        # )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")