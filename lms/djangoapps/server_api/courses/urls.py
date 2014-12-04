"""
Courses API URI specification
The order of the URIs really matters here, due to the slash characters present in the identifiers
"""
from django.conf import settings
from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from server_api.courses import views as courses_views


CONTENT_ID_PATTERN = r'(?P<content_id>[\.a-zA-Z0-9_+\/:-]+)'
TAB_ID_PATTERN = r'(?P<tab_id>[a-zA-Z0-9_+\/:-]+)'
COURSE_ID_PATTERN = settings.COURSE_ID_PATTERN

# pylint: disable=invalid-name
course_specific_patterns = patterns(
    '',
    url(r'^$', courses_views.CoursesDetail.as_view(), name='detail'),
    url(r'^content/$', courses_views.CourseContentList.as_view(), name='content_list'),
    # Note: The child pattern must come first; otherwise, the content_id pattern will need to be
    # modified to filter out the word children.
    url(r'^content/{}/children/$'.format(CONTENT_ID_PATTERN), courses_views.CourseContentList.as_view(), name='content_children_list'),
    url(r'^content/{}/$'.format(CONTENT_ID_PATTERN), courses_views.CourseContentDetail.as_view(), name='content_detail'),
    url(r'^overview/$', courses_views.CoursesOverview.as_view(), name='overview'),
    url(r'^static_tabs/$', courses_views.CoursesStaticTabsList.as_view(), name='static_tabs_list'),
    url(r'^static_tabs/{}/$'.format(TAB_ID_PATTERN), courses_views.CoursesStaticTabsDetail.as_view(), name='static_tabs_detail'),
    url(r'^updates/$', courses_views.CoursesUpdates.as_view(), name='updates'),
)

urlpatterns = patterns(
    '',
    url(r'^$', courses_views.CoursesList.as_view(), name='list'),
    url(r'^{}/'.format(COURSE_ID_PATTERN), include(course_specific_patterns))
)

urlpatterns = format_suffix_patterns(urlpatterns)
