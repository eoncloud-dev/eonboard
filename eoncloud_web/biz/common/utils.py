#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

from django.utils.translation import ugettext_lazy as _

from rest_framework.response import Response
from rest_framework import status


def retrieve_params(data, *keys):
    return tuple(data[key] for key in keys)


def retrieve_list_params(data, *keys):
    return tuple(data.getlist(key) for key in keys)


def fail(msg='', status=status.HTTP_200_OK):
    return Response({'success': False, 'msg': msg}, status=status)


def success(msg, status=status.HTTP_200_OK):
    return Response({'success': True, 'msg': msg}, status=status)


def error(msg=_('Operation failed. Unknown error happened!'),
          status=status.HTTP_500_INTERNAL_SERVER_ERROR):
    return Response({'success': False, 'msg': msg}, status=status)

