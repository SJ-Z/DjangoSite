from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin
from notifications.models import Notification


class NotificationMiddleware(MiddlewareMixin):
    """修改通知消息为已读"""
    def process_request(self, request):
        notification_id = request.GET.get('notification_id', '')
        if notification_id != '':
            notification = get_object_or_404(Notification, pk=notification_id)
            notification.unread = False
            notification.save()
