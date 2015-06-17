#coding=utf-8


from django.contrib import auth
from django.contrib.auth import middleware
from django.contrib.auth.models import AnonymousUser

def middleware_get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = get_user(request)
    return request._cached_user


def get_user(request):
    try:
        user_id = request.session[auth.SESSION_KEY]
        backend_path = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_path)
        backend.request = request
        user = backend.get_user(user_id) or AnonymousUser()
    except KeyError:
        user = AnonymousUser()
    return user


def patch_middleware_get_user():
    middleware.get_user = middleware_get_user
    auth.get_user = get_user

