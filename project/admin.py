from django.contrib import admin

from .models import Author, Post, Category, CategoryUser, Comment, PostCategory
from modeltranslation.admin import TranslationAdmin # импортируем модель амдинки
# (вспоминаем модуль про переопределение стандартных админ-инструментов)


# создаём новый класс для представления постов в админке
class PostAdmin(TranslationAdmin, admin.ModelAdmin):
    model = Post
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице
    # с товарами в админке
    # list_display = [field.name for field in Post._meta.get_fields()]  # генерируем список имён
    # всех полей для более красивого отображения
    list_display = ('choice_field', 'pub_date', 'title', 'article') # генерируем список
    # необходиых полей для отображения
    list_filter = ('choice_field', 'pub_date', 'title', 'article') # добавляем примитивные
    # фильтры в нашу админку
    search_fields = ('choice_field', 'pub_date', 'title', 'article') # тут всё очень похоже на
    # фильтры из запросов в базу. Сверху в админке у нас появилась строка, ищущая на
    # совпадения параметры, которые вы укажите в поле search_fields


class CategoryAdmin(TranslationAdmin):
    model = Category


class AuthorAdmin(admin.ModelAdmin):
    model = Author
    list_display = ('user', 'user_rating')
    list_filter = ('user', 'user_rating')
    search_fields = ('user', 'user_rating')


class CategoryUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'category')
    list_filter = ('user', 'category')
    search_fields = ('user', 'category')


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'post')
    list_filter = ('category', 'post')
    search_fields = ('category', 'post')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_comment', 'text_comment', 'comment_rating', 'post')
    list_filter = ('user', 'date_comment', 'text_comment', 'comment_rating', 'post')
    search_fields = ('user', 'date_comment', 'text_comment', 'comment_rating', 'post')


admin.site.register(Author, AuthorAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(CategoryUser, CategoryUserAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)