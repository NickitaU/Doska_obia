from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from appo.forms import RegistrationForm
import random
from django.utils import timezone
from datetime import timedelta
from appo.models import TemporaryUser


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


def clean_up_old_users():
    threshold_time = timezone.now() - timedelta(minutes=5)
    TemporaryUser.objects.filter(code_generated_at__lt=threshold_time).delete()


def register(request):
    clean_up_old_users()  # Очистка устаревших пользователей перед регистрацией

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            confirmation_code = str(random.randint(100000, 999999))

            # Проверяем, существует ли уже пользователь с этим email
            if TemporaryUser.objects.filter(email=email).exists():
                return render(request, 'sign/register.html',
                              {'form': form, 'error': 'Пользователь с таким email уже существует.'})

            temp_user = TemporaryUser.objects.create(
                username=username,
                email=email,
                password=password,  # Сохраняем пароль
                confirmation_code=confirmation_code
            )

            send_mail(
                'Ваш код подтверждения',
                f'Ваш код подтверждения: {confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return redirect('confirm_code')
    else:
        form = RegistrationForm()

    return render(request, 'sign/register.html', {'form': form})


def confirm_code(request):
    clean_up_old_users()

    if request.method == 'POST':
        code = request.POST.get('code')
        temp_user = TemporaryUser.objects.filter(confirmation_code=code).first()

        if temp_user:
            if timezone.now() <= temp_user.code_generated_at + timedelta(minutes=5):
                user = User.objects.create_user(
                    username=temp_user.username,
                    email=temp_user.email,
                    password=temp_user.password,
                )
                temp_user.delete()  # Удаляем временного пользователя
                return redirect('login')  # Переход на страницу входа
            else:
                return render(request, 'sign/confirm_code.html', {'error': 'Код истек'})
        else:
            return render(request, 'sign/confirm_code.html', {'error': 'Неверный код'})

    return render(request, 'sign/confirm_code.html')
