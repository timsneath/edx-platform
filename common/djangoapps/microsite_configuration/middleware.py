"""
This file implements the Middleware support for the Open edX platform.
A microsite enables the following features:

1) Mapping of sub-domain name to a 'brand', e.g. foo-university.edx.org
2) Present a landing page with a listing of courses that are specific to the 'brand'
3) Ability to swap out some branding elements in the website
"""
import time

from django.conf import settings
from django.utils.http import cookie_date

from django.contrib.sessions.middleware import SessionMiddleware
from microsite_configuration import microsite
from django.utils.cache import patch_vary_headers


class MicrositeMiddleware(object):
    """
    Middleware class which will bind configuration information regarding 'microsites' on a per request basis.
    The actual configuration information is taken from Django settings information
    """

    def process_request(self, request):
        """
        Middleware entry point on every request processing. This will associate a request's domain name
        with a 'University' and any corresponding microsite configuration information
        """
        microsite.clear()

        domain = request.META.get('HTTP_HOST', None)

        microsite.set_by_domain(domain)

        return None

    def process_response(self, request, response):
        """
        Middleware entry point for request completion.
        """
        microsite.clear()
        return response


class MicrositeAwareSessionMiddleware(SessionMiddleware):
    """
    Special subclass of the standard Django SessionMiddleware which
    looks to see if a request is in a microsite and to give the ability to
    define a custom COOKIE domain to better isolate login SessionStore
    between Microsite.

    IMPORTANT: This implementation assumes that the ordering of MIDDLEWARE in
    the settings files is such that MicrsoiteAwareSessionMiddleware is listed
    *after* MicrositeMiddleware so that process_response() on MicrositeAwareSessionMiddleware is
    called before process_response on MicrositeMiddleware
    """
    def process_response(self, request, response):
        """
        Look to see if request is in a microsite, and - if so - then
        take the cookie configuration settings from the Microsite
        configuration rather than the global settings
        """

        # Calling has_override_value will always return False if we are not
        # running in a Microsite. Also this will return false if the override
        # is not present in a Microsite
        if not microsite.has_override_value('SESSION_COOKIE_DOMAIN'):
            # use existing Django session middleware, which we subclass
            return super(MicrositeAwareSessionMiddleware, self).process_response(request, response)

        # if we are in a Microsite that wishes to override the COOKIE_DOMAIN
        # then we do basically what Django django.contrib.session.middleware does,
        # except for allowing the SESSION_COOKIE_DOMAIN to come from the
        # Microsite configuration.
        #
        # This code is copied/modified from the Django code base (v.1.4.16)
        #

        try:
            accessed = request.session.accessed
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                # Save the session data and refresh the client cookie.
                request.session.save()
                response.set_cookie(
                    settings.SESSION_COOKIE_NAME,
                    request.session.session_key,
                    max_age=max_age,
                    expires=expires,
                    domain=microsite.get_value('SESSION_COOKIE_DOMAIN', settings.SESSION_COOKIE_DOMAIN),
                    path=settings.SESSION_COOKIE_PATH,
                    secure=settings.SESSION_COOKIE_SECURE or None,
                    httponly=settings.SESSION_COOKIE_HTTPONLY or None
                )

        return response
