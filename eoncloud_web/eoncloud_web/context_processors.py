#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

from django.conf import settings


def eoncloud(request):

    return {
        "BRAND": settings.BRAND,
        "ICP_NUMBER": settings.ICP_NUMBER,
        "LDAP_AUTH_ENABLED": settings.LDAP_AUTH_ENABLED,
        "EXTERNAL_URL": settings.EXTERNAL_URL
    }