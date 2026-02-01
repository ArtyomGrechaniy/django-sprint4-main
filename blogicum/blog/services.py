from django.db.models import Count
from django.utils import timezone

from .models import Post


def filter_posts_by_publication(base_qs=Post.objects.all()):
    return base_qs.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related(
        'author', 'location', 'category'
    ).annotate(
        comment_count=Count('comments')
    )
