from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import JsonResponse

from comment.models import Comment
from comment.forms import CommentForm


def update_comment(request):
    """# 发送此请求的网站
    referer = request.META.get('HTTP_REFERER', reverse('home'))

    # 数据检查
    if not request.user.is_authenticated:
        return render(request, 'error.html', {'message': '用户未登录', 'redirect_to': referer})
    text = request.POST.get('text', '').strip()
    if text == '':
        return render(request, 'error.html', {'message': '评论内容为空', 'redirect_to': referer})

    try:
        content_type = request.POST.get('content_type', '')
        object_id = int(request.POST.get('object_id', ''))
        model_class = ContentType.objects.get(model=content_type).model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except Exception as e:
        return render(request, 'error.html', {'message': '评论对象不存在', 'redirect_to': referer})

    # 检查通过，保存数据
    comment = Comment()
    comment.user = request.user
    comment.text = text
    comment.content_object = model_obj
    comment.save()

    return redirect(referer)"""

    # 发送此请求的网站
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    comment_form = CommentForm(request.POST, user=request.user)
    if comment_form.is_valid():
        # 检查通过，保存数据
        comment = Comment()
        comment.user = comment_form.cleaned_data.get('user')
        comment.text = comment_form.cleaned_data.get('text')
        comment.content_object = comment_form.cleaned_data.get('content_object')

        parent = comment_form.cleaned_data.get('parent')
        if parent is not None:
            comment.parent = parent
            comment.root = parent.root if parent.parent is not None else parent
            comment.reply_to = parent.user
        comment.save()

        # 返回数据
        data = {
            'status': 'success',
            'username': comment.user.get_nickname_or_username(),
            'comment_time': comment.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
            'text': comment.text,
            'content_type': ContentType.objects.get_for_model(comment).model,
            'reply_to': comment.reply_to.get_nickname_or_username() if parent is not None else '',
            'pk': comment.pk,
            'root_pk': comment.root.pk if comment.root is not None else ''
        }

        # return redirect(referer)
    else:
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data = {
            'status': 'error',
            'message': list(comment_form.errors.values())[0][0]
        }
    return JsonResponse(data)
