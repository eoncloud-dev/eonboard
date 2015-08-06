#coding=utf-8


from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.response import Response

from biz.account.models import Operation
from biz.idc.models import UserDataCenter
from biz.floating.models import Floating
from biz.floating.serializer import FloatingSerializer
from biz.floating.settings import FLOATING_STATUS_DICT, FLOATING_ALLOCATE, FLOATING_APPLYING
from biz.floating.utils import floating_action
from biz.account.utils import check_quota
from biz.workflow.settings import ResourceType
from biz.workflow.models import Workflow, FlowInstance
from cloud.tasks import allocate_floating_task


@api_view(["GET"])
def list_view(request):
    floatings = Floating.objects.filter(user=request.user,
                                        user_data_center=request.session["UDC_ID"],
                                        deleted=False)
    serializer = FloatingSerializer(floatings, many=True)
    return Response(serializer.data)


@check_quota(["floating_ip"])
@api_view(["POST"])
def create_view(request):
    floating = Floating.objects.create(
        ip="N/A",
        status=FLOATING_ALLOCATE,
        bandwidth=int(request.POST["bandwidth"]),
        user=request.user,
        user_data_center=UserDataCenter.objects.get(pk=request.session["UDC_ID"])
    )

    Operation.log(floating, obj_name=floating.ip, action='allocate', result=1)

    workflow = Workflow.get_default(ResourceType.FLOATING)

    if settings.SITE_CONFIG['WORKFLOW_ENABLED'] and workflow:

        floating.status = FLOATING_APPLYING
        floating.save()

        FlowInstance.create(floating, request.user, workflow, None)
        msg = _("Your application for %(bandwidth)d Mbps floating ip is successful, "
                "please waiting for approval result!") % {'bandwidth': floating.bandwidth}
    else:
        msg = _("Your operation is successful, please wait for allocation.")
        allocate_floating_task.delay(floating)

    return Response({"OPERATION_STATUS": 1, 'msg': msg})


@api_view(["POST"])
def floating_action_view(request):
    data = floating_action(request.user, request.DATA)
    return Response(data)


@api_view(["GET"])
def floating_status_view(request):
    return Response(FLOATING_STATUS_DICT)


@api_view(['GET'])
def floating_ip_target_list_view(request):
    from biz.instance.models import Instance
    instance_set = Instance.objects.filter(public_ip=None, deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    from biz.lbaas.models import BalancerPool
    pool_set = BalancerPool.objects.filter(vip__public_address=None, deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])

    instance_reource = []
    if len(instance_set) >0 :
        for instance in instance_set:
            instance_reource.append({"name": "server:" + instance.name, "id": instance.id, "resource_type": "INSTANCE"})
    if len(pool_set) > 0:
        for pool in pool_set:
            instance_reource.append({"name": "lb-vip:"+pool.name, "id": pool.id, "resource_type": "LOADBALANCER"})

    return Response(instance_reource)
