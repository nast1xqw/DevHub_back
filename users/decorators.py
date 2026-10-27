from functools import wraps

from django.http import JsonResponse


def login_required_json(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'ok': False, 'errors': {'detail': ['Нужно войти']}}, status=401)
        return view(request, *args, **kwargs)

    return wrapper

def staff_required_json(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'ok': False, 'errors': {'detail': ['Нужно войти']}}, status=401)
        if not request.user.is_staff:
            return JsonResponse({'ok': False, 'errors': {'detail': ['Только для админа']}}, status=403)
        return view(request, *args, **kwargs)
    return wrapper