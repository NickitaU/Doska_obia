from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Category(models.Model):
    name_category = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name_category


class Advertisement(models.Model):  # Объявления
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50, verbose_name='Название')
    text = models.TextField(verbose_name='Текст объявления')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)

    def get_absolute_url(self):
        return settings.SITE_URL + reverse('ad_detail', args=[self.pk])


class AdvertisementVideo(models.Model):
    advertisement = models.ForeignKey(Advertisement, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='advertisement_videos/')


class AdvertisementImage(models.Model):
    advertisement = models.ForeignKey(Advertisement, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='advertisement_images/')


class Response(models.Model):  # Отзывы
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)  # Ссылка на объявление
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)  # Статус отклика


class TemporaryUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(max_length=6)
    code_generated_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128)


class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


