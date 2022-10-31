"""news URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from project.views import (BaseView, PostList, PostDetail, NewsCreate, ArticlesCreate,
                            PostUpdate, PostDelete, UserDetail, upgrade_me, sending_me,
                           UserUpdate, subscribe_me)
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', BaseView.as_view()),
    # path('', IndexView.as_view()),
    path('news/', cache_page(60)(PostList.as_view()), name='posts_list'), #указываем name для обращения к ссылке в шаблоне
    path('news/<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('articles/create/', ArticlesCreate.as_view(), name='articles_create'),
    path('news/<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('accounts/', include('allauth.urls')),
    path('user_detail/', UserDetail.as_view(), name='user_detail'),
    path('user_detail/upgrade/', upgrade_me, name='upgrade'),
    path('user_detail/sending_me/', sending_me, name='sending'),
    path('user_update/<int:pk>/', UserUpdate.as_view(), name='user_update'),
    path('subscribe_me/', subscribe_me, name='subscribe'),
]
