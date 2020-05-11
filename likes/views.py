from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from likes.models import LikeCount, LikeRecord


def success_response(liked_num):
    data = {
        'status': 'success',
        'liked_num': liked_num
    }
    return JsonResponse(data)


def error_response(code, message):
    data = {
        'status': 'error',
        'code': code,
        'message': message
    }
    return JsonResponse(data)


def like_change(request):
    # 获取数据
    user = request.user
    if not user.is_authenticated:
        return error_response(401, '您尚未登录')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))

    # 验证博客是否存在
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return error_response(404, '对象不存在')

    # 处理数据
    if request.GET.get('is_like') == 'true':
        # 要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id,
                                                                user=user)
        if created:
            # 未点赞过
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return success_response(like_count.liked_num)
        else:
            # 已点赞过，不能重复点赞
            return error_response(402, '您已点赞过，不能重复点赞')
    else:
        # 要取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数-1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return success_response(like_count.liked_num)
            else:
                return error_response(404, '数据错误')

        else:
            # 没点赞过，不能取消
            return error_response(402, '您没有点赞过，不能取消点赞')
