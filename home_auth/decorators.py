from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow a view only for logged-in users whose role is in `roles`.

    Usage: @role_required('admin') or @role_required('admin', 'teacher')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied  # shows templates/403.html
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
