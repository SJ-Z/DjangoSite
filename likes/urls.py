from django.urls import path

from likes import views

urlpatterns = [
    path('like_change', views.like_change, name='like_change'),
]
