from .views import AdList, AdDetail, AdCreate, AdUpdate, AdDelete, IndexView, ResponseAcceptView, ResponseDeleteView, create_news, news_list
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
   path('', IndexView.as_view()),
   path('Advertisements/', AdList.as_view(), name='ad_list'),
   path('Advertisements/<int:pk>', AdDetail.as_view(), name='ad_detail'),
   path('Advertisements/create/', AdCreate.as_view(), name='ad_create'),
   path('Advertisements/<int:pk>/update/', AdUpdate.as_view(), name='ad_update'),
   path('Advertisements/<int:pk>/delete/', AdDelete.as_view(), name='ad_delete'),
   path('ckeditor/', include('ckeditor_uploader.urls')),
   path('responses/accept/<int:pk>/', ResponseAcceptView.as_view(), name='response_accept'),
   path('responses/delete/<int:pk>/', ResponseDeleteView.as_view(), name='response_delete'),
   path('news/create/', create_news, name='create_news'),
   path('news/', news_list, name='news_list'),
   ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
