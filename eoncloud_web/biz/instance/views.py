#coding=utf-8

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from biz.idc.models import UserDataCenter as UDC
from biz.instance.models import Instance, Flavor
from biz.instance.serializer import InstanceSerializer, FlavorSerializer
from biz.instance.utils import instance_action
from biz.instance.settings import INSTANCE_STATES_DICT, \
                INSTANCE_STATE_RUNNING
from biz.account.utils import check_quota
from biz.account.models import Operation

from cloud.instance_task import instance_create_task

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

