#!/usr/bin/env python
# coding=utf8

__author__ = 'bluven'


import logging

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from biz.idc.models import UserDataCenter
from biz.idc.serializer import UserDataCenterSerializer

LOG = logging.getLogger(__name__)


class UserDataCenterList(generics.ListAPIView):

    queryset = UserDataCenter.objects.all()

    serializer_class = UserDataCenterSerializer

    def list(self, request):

        user_id = request.query_params['user']

        serializer = self.serializer_class(self.queryset.filter(user=user_id), many=True)

        return Response(serializer.data)
