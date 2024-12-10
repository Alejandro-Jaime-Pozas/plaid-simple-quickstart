from functools import wraps
from django.http import JsonResponse


# WRAPPER FUNCTIONS FOR VIEWS

def validate_access_token(view_func):
    """wrapper function that checks if user has a valid access token."""
    @wraps(view_func)
    def wrapper(request, access_token, *args, **kwargs):
        if not access_token:
            return JsonResponse({'error': 'Access token not available.'}, status=403)

        return view_func(request, access_token, *args, **kwargs)

    return wrapper
