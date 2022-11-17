from urllib import request

from django.core.exceptions import PermissionDenied
from django.db.models.signals import pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.forms import model_to_dict

from .models import Post, User, PostCategory
from datetime import datetime, timedelta
from .tasks import send_new_post_mail


@receiver(m2m_changed, sender=Post.category.through)
# Здесь реализована отправка сообщения юзеру подписаному на определенную категорию
# если пост созранен вызывается ф-ия из tasks
def post_save_mail(sender, instance, action="post_add", *args, **kwargs, ):
    if action == "post_add":
        send_new_post_mail(instance.id)


@receiver(pre_save, sender=Post)
# Здесь реализована функция запрета публикации более 3 постов в день
def check_daily_rate(sender, instance, **kwargs):
    post_count = Post.objects.filter(
        author=instance.author,
        pub_date__gte=datetime.now() - timedelta(days=1),
    ).count()
    if post_count > 3:
        raise PermissionDenied("Вы не можете публиковать более 3 постов в день")


@receiver(post_delete, sender=Post)
# Здесь реализация отправки письма админу при удалении поста
def send_delete_mail(sender, instance, **kwargs) -> None:
    admin = User.objects.get(username="admin")
    send_mail(
        subject=f"Удаление поста пользователем",
        message=f"Пост был удален:\n {instance.preview}",
        from_email='gbicfo@yandex.ru',
        recipient_list=[admin.email],
    )

