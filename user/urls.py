from django.urls import path

from .views import main_view, register_view, login_view, login_by_photo

urlpatterns = [
    path('', main_view, name='main'),
    path('register', register_view, name='register'),
    path('login', login_view, name='login'),
    path('login_by_photo/', login_by_photo, name='login_by_photo'),
]
