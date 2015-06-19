#coding=utf-8


from rest_framework.decorators import api_view
from rest_framework.response import Response

from biz.idc.models import UserDataCenter
from biz.floating.models import Floating
from biz.floating.serializer import FloatingSerializer
from biz.floating.settings import FLOATING_STATUS_DICT, FLOATING_ALLOCATE
from biz.floating.utils import allocate_floating, floating_action
from biz.account.utils import check_quota

@api_view(["GET"])
def list_view(request):
    floatings = Floating.objects.filter(user=request.user,
                                        user_data_center=request.session["UDC_ID"],
                                        deleted=0)
    serializer = FloatingSerializer(floatings, many=True)
    return Response(serializer.data)


@check_quota(["floating_ip"])
@api_view(["POST"])
def create_view(request):
    floating = Floating.objects.create(
        ip="N/A",
        status=FLOATING_ALLOCATE,
        bandwidth=request.POST["bandwidth"],
        user=request.user,
        user_data_center=UserDataCenter.objects.get(pk=request.session["UDC_ID"])
    )
    return Response(allocate_floating(floating))

@api_view(["POST"])
def floating_action_view(request):
    data = floating_action(request.user, request.DATA)
    return Response(data)


@api_view(["GET"])
def floating_status_view(request):
    return Response(FLOATING_STATUS_DICT)
