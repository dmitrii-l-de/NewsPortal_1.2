from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group, User

from .forms import PostForm, UserForm
from .models import Post, Author, PostCategory, CategoryUser
from .filters import PostFilter
from django.core.cache import cache # импортируем наш кэш


class BaseView(TemplateView):
    template_name = 'default.html'


class PostList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    # сортировка по дате публикации
    ordering = '-pub_date'
    # queryset = Post.objects.order_by('-pub_date')
    # также можно использовать сортировку queryset чтобы вывод был по условию:
    # queryset = Post.objects.filter(price__lt = 300).order_by('name') или
    # queryset = Post.objects.order_by('-name') в обратном направлении
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts_list'
    paginate_by = 2

    # Переопределяем функцию получения списка новостей
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — post.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'post_detail'

    # Здесь реализовано, может ли пользователь подписаться на категорию
    # если он не подписан на категорию, то кнопка кликабельна, если уже подписан, то нет
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        context_post = kwargs['object']
        print(context_post)
        context_PostCategory = (PostCategory.objects.filter(post_id=context_post.id))[0]
        list_categoryuser = CategoryUser.objects.all()
        if len(list_categoryuser) == 0:
            context['is_not_subscribe'] = True
        for next_categoryuser in list_categoryuser:
            if next_categoryuser.user_id == self.request.user.id and\
                    next_categoryuser.category_id == context_PostCategory.category_id:
                context['is_not_subscribe'] = False
                break
            else:
                context['is_not_subscribe'] = True
        return context

    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта,
        # как ни странно
        obj = cache.get(f'post_detail-{self.kwargs["pk"]}',None)  # кэш очень похож на
        # словарь, и метод get действует так же. Он забирает значение по ключу,
        # если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post_detail-{self.kwargs["pk"]}', obj)

        return obj


class NewsSearch(ListView):
    model = Post
    ordering = '-pub_date'
    template_name = 'search.html'
    context_object_name = 'news_search'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


class NewsCreate(PermissionRequiredMixin, CreateView):
    # login_url = '/accounts/login/'
    form_class = PostForm
    model = Post
    permission_required = ('project.add_post',)
    template_name = 'news_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.choice_field = 'news'
        post.author = Author.objects.get(user=self.request.user)
        return super().form_valid(form)


class ArticlesCreate(PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    permission_required = ('project.add_post',)
    template_name = 'articles_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.choice_field = 'post'
        post.author = Author.objects.get(user=self.request.user)
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    permission_required = ('project.change_post',)
    template_name = 'post_update.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    permission_required = ('project.delete_post',)
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')


class UserUpdate(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    permission_required = ('project.add_post', 'project.change_post', 'project.change_user')
    template_name = 'user_update.html'
    success_url = reverse_lazy('user_detail')


class UserDetail(LoginRequiredMixin, TemplateView):
    template_name = 'user_detail.html'

    # данная ф-ия проверяет, является ли пользователь автором. Если нет, то в его лк
    # есть кнопка "стать автором", если он автор, то кнопки нет(это условие прописано
    # в шаблоне)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
# В этом листинге кода мы получили объект текущего пользователя из переменной запроса.
# Вытащили premium-группу(авторов) из модели Group. Дальше мы проверяем, находится ли
# пользователь в этой группе (вдруг кто-то решил перейти по этому URL, уже имея
# Premium). И если он всё-таки ещё не в ней — смело добавляем
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
        Author.objects.create(user=user)
    return redirect('user_detail')


@login_required
# Здесь реализована отправка письма со страницы user_detail.html
def sending_me(request):
    admin = User.objects.get(username="admin")
    obj = request.GET # получаем данные из запраса которые переданы(в шаблоне)через ссылку
    obj_name = obj['q'] # инициализируем эти данные
    obj_email = obj['email'] # инициализируем эти данные
    send_mail(
        f'Письмо от пользователя: {obj_name}, адрес для ответа: {obj_email}',
        'Here is the message. - Привет.',
        'gbicfo@yandex.ru',
        [admin.email],
        fail_silently=False,
    )
    return redirect('posts_list')


@login_required
# здесь реализована подписка на категорию новостей на странице новости
def subscribe_me(request):
    user = request.user.pk
    print(user)
    # Все категории на которые подписан юзер
    us_cats = CategoryUser.objects.filter(user_id=user).values('category_id')
    print(us_cats)
    get_obj = request.GET # получаем данные из запраса
    print(get_obj)
    get_obj_pk = int(get_obj['query']) # инициализируем эти данные
    print(get_obj_pk)
    # инициализируем категорию новости которую будем передавать в CategoryUser
    needed_cat_id = ((PostCategory.objects.filter(post_id=get_obj_pk)).
                     values('category_id'))[0]['category_id']
    print(needed_cat_id)
    # создаем объект модели CategoryUser присваивая данные из запроса

    CategoryUser.objects.create(user_id=request.user.pk, category_id=needed_cat_id)
    # после создания перенаправляем на главную
    return redirect('posts_list')


# Здесь реализована рассылка приветственного письма зарегиным пользователям
@receiver(post_save, sender=User)
def new_user_appointment(sender, instance, created, **kwargs):
    print('Test')
    print(instance)
    user = User.objects.get(username=instance.username)
    print(user)
    print(user.email)

    send_mail(
        'Добро пожаловать на наш портал!',
        f'Приветствуем тебя, {user}',
        'gbicfo@yandex.ru',
        [user.email],
        fail_silently=False,
    )
    print('Сообщение отправлено')
    return redirect('posts_list')