from django.shortcuts import render, redirect
from django.urls import reverse


def my_notifications(request):
    return render(request, 'my_notifications/my_notifications.html')


def delete_my_read_notifications(request):
    notifications = request.user.notifications.read()
    notifications.delete()
    return redirect(reverse('my_notifications'))
