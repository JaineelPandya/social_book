from django.conf import settings
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    """Middleware that requires a user to be authenticated to view any page
    except for the paths listed in settings.LOGIN_EXEMPT_URLS.

    Configure exemptions in `social_book/settings.py` via `LOGIN_EXEMPT_URLS`.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = getattr(settings, 'LOGIN_EXEMPT_URLS', [])
        # Ensure login and logout paths are exempt if present
        try:
            login = settings.LOGIN_URL
        except Exception:
            login = '/accounts/login/'
        if login not in self.exempt_urls:
            self.exempt_urls.append(login)

    def __call__(self, request):
        # Allow if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self.get_response(request)

        # Allow exempt URLs (path startswith)
        path = request.path
        for ex in self.exempt_urls:
            if path.startswith(ex):
                return self.get_response(request)

        # Allow common public resources
        if path.startswith('/static/') or path.startswith('/media/') or path.startswith('/api/auth/') or path.startswith('/api/') or path.startswith('/admin/'):
            return self.get_response(request)

        # Redirect to login page (not API endpoint)
        return redirect(f"/accounts/login/?next={request.path}")
