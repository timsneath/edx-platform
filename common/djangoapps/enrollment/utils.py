""""Common utilities in the Enrollment API"""
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.templatetags.rest_framework import replace_query_param
from django.conf import settings


def paginate(func):
    """Utility Decorator for paginating on list return values.

    Builds a convention around how we handle pagination across RESTful interfaces.  Wraps a
    list return value in a page, reducing the contents to fit the specified page and page size.



    """
    def wrapper(self, request, **kwargs):

        ret = func(self, request, **kwargs)
        if type(ret) != list:
            return ret

        page_num = int(request.GET.get('page', 1))
        paginate_by_param = getattr(settings.REST_FRAMEWORK, 'PAGINATE_BY_PARAM', 'page_size')
        page_size = request.GET.get(paginate_by_param, getattr(settings.REST_FRAMEWORK, 'PAGINATE_BY', 10))
        max_page_size = getattr(settings.REST_FRAMEWORK, 'MAX_PAGINATE_BY', 100)
        page_size = page_size if page_size > max_page_size else max_page_size

        paginator = Paginator(ret, page_size)

        # Ensure the minimum page is one, maximum is the last page.
        if page_num <= 0:
            page_num = 1
        elif page_num > paginator.num_pages:
            page_num = paginator.num_pages

        page = paginator.page(page_num)

        base_uri = request.build_absolute_uri()
        previous = replace_query_param(base_uri, 'page', page_num-1) if page_num > 1 else ''
        next = replace_query_param(base_uri, 'page', page_num+1) if page_num < paginator.num_pages else ''
        serializable_page = {
            'results': page.object_list,
            'count': paginator.num_pages,
            'next': next,
            'previous': previous,
        }
        return Response(serializable_page)
    return wrapper
