from django.contrib import admin
from comment.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'text', 'comment_time', 'user', 'parent', 'root')
