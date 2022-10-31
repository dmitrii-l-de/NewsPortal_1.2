from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from datetime import datetime, timedelta

from .mailing_list import new_post_mail
from .models import Category, Post, CategoryUser
import time
from .mailing_list import send_weekly_mail


@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")


@shared_task
def printer(N):
    for i in range(N):
        time.sleep(1)
        print(i+1)


@shared_task
def send_new_post_mail(post_id: int) -> None:
    # данная ф-ия вызывается по сигналу из signals
    # здесь инициализируются все объекты и передаются в ф-ию отправки сообщений
    # в mailing_list, где и происходит сама отправка
    post = Post.objects.get(pk=post_id)
    if post is None:
        return
    for category in post.category.all():
        for user in category.subscribers.all():
            new_post_mail(post, category, user)


@shared_task
def send_weekly():
    for category in Category.objects.all():
        # собираем все посты в промежутке недели
        posts = category.post_set.filter(pub_date__gte=datetime.now() - timedelta(minutes=604800))
        if posts.count() != 0:
            send_weekly_mail(posts, category)
