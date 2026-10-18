import json

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from users.forms import AvatarForm, LoginForm, RegisterForm

User = get_user_model()


def user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar': user.avatar.url if user.avatar else None,
        'is_staff': user.is_staff,
    }


def get_data(request):
    try:
        return json.loads(request.body)
    except ValueError:
        return {}


def errors_response(form):
    errors = {field: list(msgs) for field, msgs in form.errors.items()}
    return JsonResponse({'ok': False, 'errors': errors}, status=400)


@ensure_csrf_cookie
def csrf_view(request):
    return JsonResponse({'ok': True})


def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    form = RegisterForm(get_data(request))
    if not form.is_valid():
        return errors_response(form)

    user = User.objects.create_user(
        username=form.cleaned_data['username'],
        email=form.cleaned_data['email'],
        password=form.cleaned_data['password'],
    )
    login(request, user)
    return JsonResponse({'ok': True, 'user': user_to_dict(user)}, status=201)


def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    form = LoginForm(get_data(request))
    if not form.is_valid():
        return errors_response(form)

    user = authenticate(
        request,
        username=form.cleaned_data['username'],
        password=form.cleaned_data['password'],
    )
    if user is None:
        return JsonResponse(
            {'ok': False, 'errors': {'detail': ['Неверное имя пользователя или пароль']}},
            status=400,
        )
    login(request, user)
    return JsonResponse({'ok': True, 'user': user_to_dict(user)})


def logout_view(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    logout(request)
    return JsonResponse({'ok': True})


def me_view(request):
    if request.user.is_authenticated:
        return JsonResponse({'ok': True, 'user': user_to_dict(request.user)})
    return JsonResponse({'ok': True, 'user': None})


def profile_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'errors': {'detail': ['Нужно войти']}}, status=401)

    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if not form.is_valid():
            return errors_response(form)
        form.save()

    return JsonResponse({'ok': True, 'user': user_to_dict(request.user)})