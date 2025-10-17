from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('personal_login/', views.personal_login, name='personal_login'),
    path('ong_login/', views.ong_login, name='ong_login'),
    path('feed/', views.feed, name='feed'),
    path('create_post/', views.create_post, name='create_post'),
]