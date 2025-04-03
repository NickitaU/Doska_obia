from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Response, News, User


@receiver(post_save, sender=Response)
def send_response_notification(sender, instance, created, **kwargs):
    if created:  # Если отклик был создан
        subject = 'Новый отклик на ваше объявление!'
        message = f'На ваше объявление "{instance.advertisement.title}" поступил новый отклик.\n' \
                  f'Посмотреть отклик можно по ссылке: {instance.advertisement.get_absolute_url()}'
        recipient_list = [instance.advertisement.author.email]  # Email создателя объявления
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    if instance.is_accepted:  # Если отклик принят
        subject = 'Ваш отклик принят'
        message = f'Ваш отклик на объявление "{instance.advertisement.title}" принят!\n' \
                  f'Объявление: {instance.advertisement.get_absolute_url()}'
        recipient_list = [instance.user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


@receiver(post_save, sender=News)
def send_news_notification(sender, instance, created, **kwargs):
    if created:
        users = User.objects.exclude(email='')  # Получаем всех пользователей с заполненным email
        for user in users:
            try:
                send_mail(
                    'Новая новость: ' + instance.title,
                    instance.content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Логируйте ошибки
                print(f'Ошибка отправки почты для {user.email}: {str(e)}')
