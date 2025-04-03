from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register, confirm_code

urlpatterns = [
    path('login/',
         LoginView.as_view(template_name='sign/login.html'),
         name='login'),
    path('logout/',
         LogoutView.as_view(template_name='sign/logout.html'),
         name='logout'),
    path('signup/', register, name='signup'),
    path('confirm_code/', confirm_code, name='confirm_code'),
]