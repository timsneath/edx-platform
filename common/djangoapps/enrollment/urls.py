"""
URLs for the Enrollment API

"""
from django.conf import settings
from django.conf.urls import patterns, url

from .views import (
    EnrollmentView,
    EnrollmentListView,
    EnrollmentListRedirectView,
    EnrollmentRedirectView,
    EnrollmentCourseDetailView
)

urlpatterns = []
USER_PATTERN = '(?P<user>[\w.+-]+)'

if settings.FEATURES.get('ENABLE_COMBINED_LOGIN_REGISTRATION'):
    urlpatterns += patterns(
        'enrollment.views',
        url(r'^user/{user}$'.format(user=USER_PATTERN), EnrollmentListView.as_view(), name='courseenrollments'),
        url(r'^user', EnrollmentListRedirectView.as_view(), name='courseenrollmentsredirect'),
        url(
            r'^user/{user}/course/{course_key}$'.format(course_key=settings.COURSE_ID_PATTERN, user=USER_PATTERN),
            EnrollmentView.as_view(),
            name='courseenrollment'
        ),
        url(
            r'^course/{course_key}$'.format(course_key=settings.COURSE_ID_PATTERN),
            EnrollmentRedirectView.as_view(),
            name='courseenrollmentredirect'
        ),
        url(
            r'^course/{course_key}/details$'.format(course_key=settings.COURSE_ID_PATTERN),
            EnrollmentCourseDetailView.as_view(),
            name='courseenrollment'
        ),
    )
