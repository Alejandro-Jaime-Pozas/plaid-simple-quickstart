from functools import wraps
from django.http import JsonResponse

# WRAPPER FUNCTIONS FOR VIEWS

def validate_access_token(view_func):
    """wrapper function that checks if user has a valid access token."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.session.get("access_token")
        # print('got access token from request in wrapper fn:', access_token)
        if not access_token:
            return JsonResponse({'error': 'Access token not available.'}, status=403)
        kwargs["access_token"] = access_token
        return view_func(request, *args, **kwargs)
    return wrapper
