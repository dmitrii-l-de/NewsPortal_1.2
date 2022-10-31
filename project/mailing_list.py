from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from project.models import Post, Category



def new_post_mail(post: Post, category: Category, user: User) -> None:
    # здесь непосредственно происходит отправка сообщения юзеру при появлении новой
    # статьи в категории на которую он подписан
    # при срабатывании сигнала сохранения новой новости, вызывается задача отправки сообщения
    # которая вызывает данную ф-ию
    if user.email == "" or user.email is None:
        return

    html = render_to_string(
        "mail_to_subscriber.html",
        {
            "category": category,
            "post": post,
            "user": user,
        },
    )
    msg = EmailMultiAlternatives(
        subject=f"Новый пост в категории {category.category_name}",
        body=html,
        from_email='gbicfo@yandex.ru',
        to=[user.email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


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