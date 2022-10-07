from django_filters import FilterSet, DateFilter
from .models import Post
import django.forms


# Создаем свой набор фильтров для модели Post.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.
class PostFilter(FilterSet):
    pub_date = DateFilter(
        lookup_expr='gte',
        widget=django.forms.DateInput(
            attrs={
                'type': 'date'
            }
        ))

    class Meta:
        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Post
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
            'title': ['icontains'],
            'category': ['exact'],
        }
