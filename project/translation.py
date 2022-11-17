from .models import *
from modeltranslation.translator import register, TranslationOptions  # импортируем декоратор для перевода и класс настроек, от которого будем наследоваться


# регистрируем наши модели для перевода
@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('category_name',)


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'article', 'pub_date', 'post_rating',)

