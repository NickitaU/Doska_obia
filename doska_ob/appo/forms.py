from .models import Advertisement, Category, AdvertisementVideo, AdvertisementImage
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Response
from .models import News

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Ваш отклик...'})
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = [
            'title',
            'text',
            'categories',
        ]
        widgets = {
            'categories': forms.SelectMultiple(),
            'text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Введите текст объявления...'}),
        }
        labels = {
            'title': 'Название',
            'text': 'Текст объявления',
            'categories': 'Категории',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.all()


class AdvertisementImageForm(forms.ModelForm):
    class Meta:
        model = AdvertisementImage
        fields = ['image']


class AdvertisementVideoForm(forms.ModelForm):
    class Meta:
        model = AdvertisementVideo
        fields = ['video']


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content']