from django.utils.timezone import now
from .models import Post
from django.core.paginator import Paginator


def get_published_posts():
    return Post.objects.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True
    )


def paginate_queryset(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
