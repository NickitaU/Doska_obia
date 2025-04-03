from .models import Advertisement
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from datetime import datetime
from .forms import AdvertisementForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required,user_passes_test
from django.utils.decorators import method_decorator
from .models import Advertisement, AdvertisementImage, AdvertisementVideo, News, Response
from .forms import AdvertisementForm, ResponseForm, NewsForm
from django.core.files.storage import FileSystemStorage
from django_filters import rest_framework as filters
from .filters import AdvertisementFilter
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'appo/index.html'


class AdList(ListView):    # Страница где показаны все объявления
    model = Advertisement
    ordering = ['-created_at']
    template_name = 'Ads.html'
    context_object_name = 'Advertisements'
    paginate_by = 9

    def get_queryset(self):     # Фильтр
        queryset = super().get_queryset()
        advertisement_filter = AdvertisementFilter(self.request.GET, queryset=queryset)
        return advertisement_filter.qs

    def get_context_data(self, **kwargs):  # Сортировка по дате
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filter'] = AdvertisementFilter(self.request.GET, queryset=self.get_queryset())
        return context


class AdDetail(DetailView):
    model = Advertisement
    template_name = 'AdD.html'
    context_object_name = 'Advertisement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.object.categories.all()
        context['form'] = ResponseForm()
        context['responses'] = self.object.response_set.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ResponseForm(request.POST)

        if form.is_valid():
            response = form.save(commit=False)
            response.user = request.user
            response.advertisement = self.object
            response.save()  # Сигнал отправит уведомление
            return redirect('ad_detail', pk=self.object.pk)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ResponseAcceptView(LoginRequiredMixin, DetailView):   # Одобрение отклика
    model = Response
    template_name = 'response_confirm_accept.html'

    def post(self, request, *args, **kwargs):
        response = self.get_object()
        response.is_accepted = True
        response.save()  # Сигнал отправит уведомление
        return redirect('ad_detail', pk=response.advertisement.pk)


class ResponseDeleteView(LoginRequiredMixin, DeleteView):   # Удаление отклика
    model = Response
    template_name = 'response_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('ad_detail', kwargs={'pk': self.object.advertisement.pk})

    def get_queryset(self):
        return Response.objects.filter(advertisement__author=self.request.user)


@method_decorator(login_required, name='dispatch')
class AdCreate(LoginRequiredMixin, CreateView):     # Создание объявления
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'AdCreate.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        advertisement = form.save(commit=False)
        advertisement.author = self.request.user
        advertisement.save()

        # Обработка изображений
        image_files = self.request.FILES.getlist('image')
        for img in image_files:
            if img:  # Проверяем, что файл не пустой
                AdvertisementImage.objects.create(advertisement=advertisement, image=img)

        # Обработка видео
        video_files = self.request.FILES.getlist('video')
        for vid in video_files:
            if vid:  # Проверяем, что файл не пустой
                AdvertisementVideo.objects.create(advertisement=advertisement, video=vid)

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AdDelete(LoginRequiredMixin, DeleteView):     # Удаление объявления
    model = Advertisement
    template_name = 'AdDelete.html'
    success_url = reverse_lazy('ad_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise Http404("У вас нет прав для удаления этого объявления.")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class AdUpdate(LoginRequiredMixin, UpdateView):     # Обновление объявления
    form_class = AdvertisementForm
    model = Advertisement
    template_name = 'AdCreate.html'

    def form_valid(self, form):
        advertisement = form.save(commit=False)
        advertisement.author = self.request.user
        advertisement.save()

        # Удаляем старые изображения и видео перед добавлением новых
        AdvertisementImage.objects.filter(advertisement=advertisement).delete()
        AdvertisementVideo.objects.filter(advertisement=advertisement).delete()

        # Обработка новых изображений
        image_files = self.request.FILES.getlist('image')
        for img in image_files:
            if img:
                AdvertisementImage.objects.create(advertisement=advertisement, image=img)

        # Обработка новых видео
        video_files = self.request.FILES.getlist('video')
        for vid in video_files:
            if vid:
                AdvertisementVideo.objects.create(advertisement=advertisement, video=vid)

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise Http404("У вас нет прав для редактирования этого объявления.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('ad_detail', kwargs={'pk': self.object.pk})


def is_developer(user):
    return user.groups.filter(name='разработчики').exists()


@login_required
@user_passes_test(is_developer)
def create_news(request):
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news_list')  # Перенаправление на страницу со списком новостей
    else:
        form = NewsForm()
    return render(request, 'create_news.html', {'form': form})


def news_list(request):
    news = News.objects.all()
    is_developer = request.user.groups.filter(name='разработчики').exists()
    return render(request, 'news_list.html', {'news': news, 'is_developer': is_developer})
