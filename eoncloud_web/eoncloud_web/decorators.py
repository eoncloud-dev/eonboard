#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view


def superuser_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in and is super user, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


require_GET = api_view(["GET"])
require_POST = api_view(["POST"])
require_DELETE = api_view(["DELETE"])
require_PUT = api_view(["PUT"])
