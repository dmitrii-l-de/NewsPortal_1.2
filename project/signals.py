from urllib import request

from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_save, post_init, pre_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from .models import Post, PostCategory, User, CategoryUser


@receiver(post_init, sender=PostCategory)
def save_new_post(sender, instance, *args, **kwargs):
   post = instance
   print('TEST')
   print(f'Это айди категории созданного поста {instance.category_id}')
   print(f'Это айди поста {instance.post_id}')
   send_post = Post.objects.filter(id=instance.post_id).values('title')[0]['title']
   send_text = Post.objects.filter(id=instance.post_id).values('article')[0]['article']
   send_url = Post.objects.filter(id=instance.post_id)[0].get_absolute_url()
   print(f'ссылка на пост {send_url}')
   list_user = User.objects.all()
   list_category_user = CategoryUser.objects.all()
   print(f'Список всех юзеров{list_user}')
   print(f'Количество всех юзеров{len(list_user)}')
   add_post_cat = post.category_id
   for user in list_user:
       for category in list_category_user:
           #print(f'Список модели КатегориЮзер {category.category_id}, {category.user_id}')
           if user.id == category.user_id:
               if add_post_cat == category.category_id:
                   print(f'Почты юзеров для отправки : {user.email}')
                   send_post = str(send_post)
                   send_post_id = int(instance.post_id)
                   send_text = str(send_text[:30])

                   print(send_post, send_text)

                   html = render_to_string(
                       # передаем в шаблон переменные
                       'mail_to_subscriber.html', {'post_object': post.category, 'send_post': send_post,
                                                   'send_text': send_text, 'post_id': send_post_id},
                   )

                   msg = EmailMultiAlternatives(
                       subject='Уважаемый {user.first_name} {user.last_name} появилась новая статья!',
                       from_email='gbicfo@yandex.ru',
                       to=[user.email], # отправка необходимым людям
                   )
                   msg.attach_alternative(html, 'text/html')
                   msg.send()
   return redirect('posts_list')


@receiver(pre_save, sender=Post)
# Здесь реализована функция запрета публикации более 3 постов в день
def check_daily_rate(sender, instance, **kwargs):
    post_count = Post.objects.filter(
        author=instance.author,
        pub_date__gte=datetime.now() - timedelta(days=1),
    ).count()
    if post_count > 3:
        raise PermissionDenied("you can not publish more than 3 posts")


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