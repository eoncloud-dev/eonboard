#!/usr/bin/env python
# coding=utf8

__author__ = 'bluven'


import logging

from rest_framework import generics
from rest_framework.response import Response

from biz.idc.models import UserDataCenter
from biz.account.models import Contract
from biz.idc.serializer import UserDataCenterSerializer

LOG = logging.getLogger(__name__)


class UserDataCenterList(generics.ListAPIView):

    queryset = UserDataCenter.objects.all()

    serializer_class = UserDataCenterSerializer

    def list(self, request):

        queryset = self.get_queryset()

        if 'user' in request.query_params:
            user_id = request.query_params['user']
            queryset = queryset.filter(user=user_id).exclude(
                contract__in=Contract.objects.filter(user=user_id))

        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)


class UserDataDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = UserDataCenter.objects.all()

    serializer_class = UserDataCenterSerializer
