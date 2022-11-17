from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _ # импортируем функцию для перевода


class Author(models.Model):
    '''
    Модель содержащая объекты всех авторов. Поле user имеет связь 1к1 с
    моделью User и поле author_rating отражает общий рейтинг автора
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Author'))
    user_rating = models.IntegerField(default=0, verbose_name='Rating')
    '''
    Метод update_rating() модели Author, который обновляет рейтинг 
    пользователя, переданный в аргумент этого метода.
    Он состоит из следующего:
    суммарный рейтинг каждой статьи автора умножается на 3;
    суммарный рейтинг всех комментариев автора;
    суммарный рейтинг всех комментариев к статьям автора.
    '''
    def update_rating(self):
        self.user_rating = 0
        for post in Post.objects.filter(author__user=self.user):
            self.user_rating += post.post_rating * 3
            for comment in Comment.objects.filter(post=post):
                self.user_rating += comment.comment_rating
        for comment in Comment.objects.filter(user=self.user):
            self.user_rating += comment.comment_rating
        self.save()

    def __str__(self):
        return f'{self.user}'


class Category(models.Model):
    '''
    Категории новостей/постов, темы которые они отображают.
    Имеет поле category_name которое должно быть уникально
    и поле subscribers имеющее связь многие ко многим с моделью User
    '''
    category_name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, through='CategoryUser')

    def __str__(self):
        return f'{self.category_name}'


class CategoryUser(models.Model):
    '''
    Промежуточная модель связывающая юзеров и категории новостей/пост
    на которые они подписаны. 1 юзер может быть подписан на несколько категорий
    '''
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name='Subscription сategory', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}, {self.category}'


class Post(models.Model):
    '''
    Модель содержит статьи и новости которые создают пользователи.
    Каждый объект может иметь 1 или несколько категорий
    Включает следующие поля:
    связь «один ко многим» с моделью Author;
    поле с выбором — «статья» или «новость»;
    автоматически добавляемая дата и время создания;
    связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory);
    заголовок статьи/новости;
    текст статьи/новости;
    рейтинг статьи/новости.
    '''
    post = 'P'
    news = 'N'
    CHOICES = [
        (news, 'News'),
        (post, 'Post')
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Post Author')
    choice_field = models.CharField(max_length=1, choices=CHOICES, default=news)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Publication date'))
    title = models.CharField(max_length=255, verbose_name=_('Post title'))
    article = models.TextField(verbose_name=_('Post text'))
    post_rating = models.IntegerField(default=0, db_column='post_rating', verbose_name='Post rating')
    category = models.ManyToManyField(Category, through='PostCategory', verbose_name=_('Category'))
    '''
    Метод preview() модели Post, который возвращает начало статьи 
    (предварительный просмотр) длиной 124 символа и добавляет многоточие в 
    конце
    '''
    def preview(self):
        return f'{self.article[:124]} ...'

    def like(self, value=1):
        self.post_rating += value
        self.save()

    def dislike(self, value=1):
        self.post_rating -= value
        self.save()

    def __str__(self):
        return f'Post title: {self.title.title()}, Publication date: ' \
               f'{self.pub_date}: Post text: {self.article}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post_detail-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(models.Model):
    '''
    Промежуточная модель связывающая новость/пост и соответствующую категорию
    '''
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'Post: {self.post}\nCategory: {self.category}'


class Comment(models.Model):
    '''
    Под каждой новостью/статьёй можно оставлять комментарии, поэтому необходимо
    организовать их способ хранения тоже.
    Модель будет иметь следующие поля:
    связь «один ко многим» с моделью Post;
    связь «один ко многим» со встроенной моделью User (комментарии может
    оставить любой пользователь, необязательно автор);
    текст комментария;
    дата и время создания комментария;
    рейтинг комментария.
    '''
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_comment = models.TextField(blank=True)
    date_comment = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0, db_column='comment_rating')

    def like(self, value=1):
        self.comment_rating += value
        self.save()

    def dislike(self, value=1):
        self.comment_rating -= value
        self.save()

    def __str__(self):
        return f'{self.post}, {self.user}, {self.text_comment}, {self.comment_rating}'