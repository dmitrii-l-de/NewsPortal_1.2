from django import forms
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from .models import Post, User


class PostForm(forms.ModelForm):
    title = forms.CharField(min_length=10)

    class Meta:
        model = Post
        fields = [
            'title',
            'article',
            'category',
        ]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        text = cleaned_data.get("article")

        if title == text:
            raise ValidationError(
                "The title should not be identical to the text of the article"
            )
        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
           'email',
           'username',
           'first_name',
           'last_name',
        ]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        username = cleaned_data.get("username")
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')


class CommonSignupForm(SignupForm):
    '''
    Здесь мы импортировали класс формы, который предоставляет allauth, а также
    модель групп. В кастомизированном классе формы, в котором мы хотим добавлять
    пользователя в группу, мы должны переопределить только метод save(), который
    выполняется при успешном заполнении формы регистрации
    '''
    def save(self, request):
        user = super(CommonSignupForm, self).save(request) #вызываем этот же метод
        # класса-родителя, чтобы необходимые проверки и сохранение в модель User
        # были выполнены
        common_group = Group.objects.get(name='common') #получаем объект модели группы common
        common_group.user_set.add(user) #через атрибут user_set, возвращающий список всех пользователей этой
        # группы, мы добавляем нового пользователя в эту группу.
        return user #Обязательным требованием метода save() является возвращение
        # объекта модели User по итогу выполнения функции