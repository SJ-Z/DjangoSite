from django.urls import path

from my_notifications import views

urlpatterns = [
    path('', views.my_notifications, name='my_notifications'),
    path('delete_my_read_notifications', views.delete_my_read_notifications, name='delete_my_read_notifications'),
]
