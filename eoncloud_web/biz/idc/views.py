#-*- coding=utf-8 -*-

__author__ = 'bluven'


import logging

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils.translation import ugettext_lazy as _

from biz.idc.models import DataCenter, UserDataCenter
from biz.account.models import Contract
from biz.idc.serializer import DataCenterSerializer, UserDataCenterSerializer

LOG = logging.getLogger(__name__)


class DataCenterList(generics.ListAPIView):

    queryset = DataCenter.objects.all()

    serializer_class = DataCenterSerializer

    def list(self, request):

        serializer = self.serializer_class(self.queryset, many=True)

        return Response(serializer.data)


class UserDataCenterList(generics.ListAPIView):

    queryset = UserDataCenter.objects.all()

    serializer_class = UserDataCenterSerializer

    def list(self, request):

        queryset = self.get_queryset()

        # If there is user id, retrive user data center which have no contract associated
        if 'user' in request.query_params:
            user_id = request.query_params['user']
            queryset = queryset.filter(user=user_id).exclude(
                contract__in=Contract.objects.filter(user=user_id, deleted=False))

        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)


class UserDataCenterDetail(generics.RetrieveAPIView):

    queryset = UserDataCenter.objects.all()

    serializer_class = UserDataCenterSerializer


@api_view(['POST'])
def create_data_center(request):
    try:
        serializer = DataCenterSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True,
                             "msg": _('Data Center is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False,
                             "msg": _('Data Center data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create data center, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create data center for unknown reason.')})


@api_view(['POST'])
def update_data_center(request):
    try:

        pk = request.data['id']

        host = request.data['host']

        if DataCenter.objects.filter(host=host).exclude(pk=pk).exists():
            return Response({"success": False, "msg": _('This host has been used by other data center.')},
                            status=status.HTTP_400_BAD_REQUEST)

        data_center = DataCenter.objects.get(pk=pk)

        for field, value in request.data.items():

            setattr(data_center, field, value)

        data_center.save()

        return Response({'success': True, "msg": _('Data Center is updated successfully!')},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Failed to create data center, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create data center for unknown reason.')})


@api_view(['POST'])
def delete_data_centers(request):
    try:

        ids = request.data.getlist('ids[]')

        DataCenter.objects.filter(pk__in=ids).delete()

        return Response({'success': True, "msg": _('Data centers have been deleted!')}, status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to delete data centers, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to delete data centers for unknown reason.')})


@api_view(['GET'])
def is_host_unique(request):

    host = request.query_params['host']

    pk = request.query_params.get('pk', None)

    queryset = DataCenter.objects.filter(host=host)

    # If pk is not empty, then user must be editing other than creating a data center
    if pk:
        queryset = queryset.exclude(pk=pk)

    return Response(not queryset.exists())
