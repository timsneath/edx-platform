""""Common utilities in the Enrollment API"""
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.templatetags.rest_framework import replace_query_param


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
        page_size = request.GET.get('page_size', 10)  # TODO preferences for page, page_size
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
