from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone
from django.core.cache import cache

from blog.models import Blog
from read_statistics.utils import get_week_read_data, get_today_hot_data, get_yesterday_hot_data


def get_week_hot_data():
    """获取一周内热门数据（前7条）"""
    today = timezone.now().date()
    date = today - timezone.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__gte=date)\
                        .values('id', 'title')\
                        .annotate(read_num_sum=Sum('read_details__read_num'))\
                        .order_by('-read_num_sum')
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_week_read_data(blog_content_type)

    # 获取近一周热门博客的缓存数据
    week_hot_blogs = cache.get('week_hot_blogs')
    if week_hot_blogs is None:
        week_hot_blogs = get_week_hot_data()
        cache.set('week_hot_blogs', week_hot_blogs, 3600)

    context = {
        'dates': dates,
        'read_nums': read_nums,
        'today_hot_data': get_today_hot_data(blog_content_type),
        'yesterday_hot_data': get_yesterday_hot_data(blog_content_type),
        'week_hot_blogs': week_hot_blogs,
    }
    return render(request, 'home.html', context)
