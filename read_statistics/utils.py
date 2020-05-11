import datetime
from django.db.models import Sum
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from read_statistics.models import ReadNum, ReadDetail


def read_statistics_once_read(request, obj):
    """增加一次阅读量"""
    ct = ContentType.objects.get_for_model(obj)
    key = '%s_%s_read' % (ct.model, obj.pk)

    if not request.COOKIES.get(key):
        # 总阅读数+1
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 当天阅读数+1
        read_detail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=timezone.now().date())
        read_detail.read_num += 1
        read_detail.save()

    return key


def get_week_read_data(content_type):
    """统计一周内每天的阅读量"""
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))  # 使用聚合函数对当天的阅读量进行求和，返回值为字典
        read_nums.append(result['read_num_sum'] or 0)
    return dates, read_nums


def get_today_hot_data(content_type):
    """获取今日热门数据（前7条）"""
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_details[:7]


def get_yesterday_hot_data(content_type):
    """获取昨日热门数据（前7条）"""
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    return read_details[:7]
