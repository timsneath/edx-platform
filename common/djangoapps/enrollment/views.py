"""
The Enrollment API Views should be simple, lean HTTP endpoints for API access. This should
consist primarily of authentication, request validation, and serialization.

"""
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import RedirectView, View
from rest_framework import status
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from enrollment import api
from student.models import NonExistentCourseError, CourseEnrollmentException
from util.authentication import SessionAuthenticationAllowInactiveUser


class EnrollmentUserThrottle(UserRateThrottle):
    """Limit the number of requests users can make to the enrollment API."""
    # TODO Limit significantly after performance testing.  # pylint: disable=fixme
    rate = '50/second'


class EnrollmentView(APIView):
    """ Enrollment API View for creating, updating, and viewing course enrollments. """

    authentication_classes = OAuth2Authentication, SessionAuthenticationAllowInactiveUser
    permission_classes = permissions.IsAuthenticated,
    throttle_classes = EnrollmentUserThrottle,

    def get(self, request, course_id=None, user=None):
        """Create, read, or update enrollment information for a user.

        HTTP Endpoint for all CRUD operations for a user course enrollment. Allows creation, reading, and
        updates of the current enrollment for a particular course.

        Args:
            request (Request): To get current course enrollment information, a GET request will return
                information for the current user and the specified course.
            course_id (str): URI element specifying the course location. Enrollment information will be
                returned, created, or updated for this particular course.
            user (str): The user username associated with this enrollment request.

        Return:
            A JSON serialized representation of the course enrollment.

        """
        if request.user.username != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            return Response(api.get_enrollment(user, course_id))
        except (NonExistentCourseError, CourseEnrollmentException):
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, course_id=None, user=None):
        """Create a new enrollment"""
        if user != request.user.username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            return Response(api.add_enrollment(user, course_id))
        except api.CourseModeNotFoundError as error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=error.data)
        except (NonExistentCourseError, api.EnrollmentNotFoundError, CourseEnrollmentException):
            return Response(status=status.HTTP_400_BAD_REQUEST)


class EnrollmentCourseDetailView(APIView):
    """ Enrollment API View for viewing course enrollment details. """

    authentication_classes = []
    permission_classes = []
    throttle_classes = EnrollmentUserThrottle,

    def get(self, request, course_id=None):
        """Read enrollment information for a particular course.

        HTTP Endpoint for retrieving course level enrollment information.

        Args:
            request (Request): To get current course enrollment information, a GET request will return
                information for the specified course.
            course_id (str): URI element specifying the course location. Enrollment information will be
                returned.

        Return:
            A JSON serialized representation of the course enrollment details.

        """
        return Response(api.get_course_enrollment_details(course_id))


class EnrollmentListView(APIView):
    """ Enrollment API List View for viewing all course enrollments for a user. """

    authentication_classes = OAuth2Authentication, SessionAuthenticationAllowInactiveUser
    permission_classes = permissions.IsAuthenticated,
    throttle_classes = EnrollmentUserThrottle,

    def get(self, request, user=None):
        """List out all the enrollments for the current user

        Returns a JSON response with all the course enrollments for the current user.

        Args:
            request (Request): The GET request for course enrollment listings.
            user (str): Get all enrollments for the specified user's username.

        Returns:
            A JSON serialized representation of the user's course enrollments.

        """
        if request.user.username != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(api.get_enrollments(user))


class EnrollmentListRedirectView(View):
    """Redirect to the EnrollmentListView when no user is specified in the URL."""

    def get(self, request, *args, **kwargs):
        """Returns the redirect URL with the user's username specified."""
        return redirect(reverse('courseenrollments', args=[request.user.username]))


class EnrollmentRedirectView(RedirectView):
    """Redirect to the EnrollmentView when no user is specified in the URL."""

    def get(self, request, *args, **kwargs):
        """Returns the redirect URL with the user's username specified."""
        return redirect(reverse('courseenrollment', args=[request.user.username, kwargs['course_id']]))
