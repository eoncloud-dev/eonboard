#coding=utf-8

import logging

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.utils.translation import ugettext_lazy as _

from biz.instance.models import Instance, Flavor
from biz.instance.serializer import InstanceSerializer, FlavorSerializer
from biz.instance.utils import instance_action
from biz.instance.settings import INSTANCE_STATES_DICT, INSTANCE_STATE_RUNNING
from biz.account.utils import check_quota
from biz.account.models import Operation

from cloud.instance_task import instance_create_task

LOG = logging.getLogger(__name__)


class InstanceList(generics.ListCreateAPIView):
    queryset = Instance.objects.all().filter(deleted=False)
    serializer_class = InstanceSerializer

    def list(self, request):
        try:
            queryset = self.get_queryset().filter(user=request.user)
            serializer = InstanceSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response()

    def create(self, request, *args, **kwargs):
        raise


class FlavorList(generics.ListCreateAPIView):
    queryset = Flavor.objects.all()
    serializer_class = FlavorSerializer


class FlavorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Flavor.objects.all()
    serializer_class = FlavorSerializer


@api_view(["POST"])
def create_flavor(request):
    try:
        serializer = FlavorSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Flavor is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Flavor data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create flavor for unknown reason.')})


@api_view(["POST"])
def update_flavor(request):
    try:

        flavor = Flavor.objects.get(pk=request.data['id'])

        serializer = FlavorSerializer(instance=flavor, data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Flavor is updated successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Flavor data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to update flavor for unknown reason.')})


@api_view(["POST"])
def delete_flavors(request):

    ids = request.data.getlist('ids[]')

    Flavor.objects.filter(pk__in=ids).delete()

    return Response({'success': True, "msg": _('Flavors have been deleted!')}, status=status.HTTP_201_CREATED)


@check_quota(["instance", "vcpu", "memory"])
@api_view(["POST"])
def instance_create_view(request):
    serializer = InstanceSerializer(data=request.data, context={"request": request}) 
    if serializer.is_valid():
        ins = serializer.save()
        Operation.log(ins, obj_name=ins.name, action="launch", result=1)
        instance_create_task.delay(ins, password=request.DATA["password"])
        return Response({"OPERATION_STATUS": 1}, status=status.HTTP_201_CREATED)
    else:
        return Response({"OPERATION_STATUS": 0}, status=status.HTTP_400_BAD_REQUEST) 


@api_view(["POST"])
def instance_action_view(request, pk):
    data = instance_action(request.user, request.DATA)
    return Response(data)


@api_view(["GET"])
def instance_status_view(request):
    return Response(INSTANCE_STATES_DICT)


@api_view(["GET"])
def instance_search_view(request, **kwargs):
    instance_set = Instance.objects.filter(deleted=False, status=INSTANCE_STATE_RUNNING,
                                           user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = InstanceSerializer(instance_set, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def summary(request):
    return Response({"num": Instance.objects.count()})
