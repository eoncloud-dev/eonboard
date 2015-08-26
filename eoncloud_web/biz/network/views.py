#coding=utf-8

import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from biz.common.decorators import require_POST
from biz.common.utils import retrieve_params
from biz.instance.models import Instance
from biz.account.models import Operation
from biz.network.models import Network, Subnet, Router, RouterInterface

from biz.network.serializer import (NetworkSerializer, RouterSerializer,
                                    RouterInterfaceSerializer, SubnetSerializer)
from biz.instance.serializer import InstanceSerializer

from cloud.network_task import (router_create_task,
                                router_delete_task,
                                router_add_gateway_task,
                                router_remove_gateway_task)
from cloud import tasks
from biz.network.settings import (NETWORK_STATES_DICT,
                                  NETWORK_STATE_ACTIVE,
                                  NETWORK_STATE_UPDATING,
                                  NETWORK_STATE_DELETING)

LOG = logging.getLogger(__name__)


@api_view(['GET'])
def network_list_view(request):
    network_set = Network.objects.filter(
        deleted=False, user=request.user,
        user_data_center=request.session["UDC_ID"])
    serializer = NetworkSerializer(network_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def network_create_view(request):
    address = request.data['address']
    # 检测地址是否已经占用
    if Subnet.objects.filter(user=request.user,
                             deleted=False,
                             address=address).exists():
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('Network address exists')})

    serializer = NetworkSerializer(data=request.data,
                                   context={"request": request})

    if not serializer.is_valid():
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('The data is not valid')},
                        status=status.HTTP_400_BAD_REQUEST)

    network = serializer.save()
    subnet_name = "%s(%s)" % (network.name, address)
    subnet = Subnet.objects.create(name=subnet_name,
                                   network=network,
                                   address=address,
                                   user=network.user,
                                   user_data_center=network.user_data_center)

    try:
        tasks.create_network_and_subnet.delay(network=network, subnet=subnet)
    except Exception as e:
        subnet.delete()
        network.delete()
        LOG.exception("Failed to create network, msg:[%s]", e)
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('Unkown error happened')})
    else:
        Operation.log(obj=network, obj_name=network.name,
                      action='create', result=1)
        return Response({"OPERATION_STATUS": 1,
                         "MSG": _("Creating network")})


@require_POST
def network_update(request):

    network_id, name = retrieve_params(request.data, 'id', 'name')

    try:
        network = Network.objects.get(pk=network_id, user=request.user)
    except Network.DoesNotExist:
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('The selected network not exist')})
    else:
        network.name = name
        network.save()
        Operation.log(obj=network, obj_name=network.name, action='update')
        return Response({"OPERATION_STATUS": 1,
                         "MSG": _('Update network success')})


@require_POST
def delete_network(request):

    try:
        network = Network.objects.get(pk=request.data["network_id"],
                                      user=request.user)
    except Network.DoesNotExist:
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('The selected network does not exist')})

    # Defalut network can not be deleted
    if network.is_default:
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('Default network can not be deleted')})

    # Was unable to delete the network when it is being used
    if network.is_in_use:
        return Response({
            "OPERATION_STATUS": 0,
            "MSG": _('This network is being used!')})

    network.change_status(NETWORK_STATE_DELETING)

    try:
        tasks.delete_network.delay(network)
    except Exception as e:
        network.change_status(NETWORK_STATE_ACTIVE)
        LOG.exception("Failed to delete network[%s], reason:[%s] ",
                      network.name, e)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Network deleted error')})
    else:
        Operation.log(obj=network, obj_name=network.name,
                      action='terminate', result=1)
        return Response({"OPERATION_STATUS": 1,
                         "MSG": _('Network deleted success')})


@api_view(['GET'])
def network_status_view(request):
    return Response(NETWORK_STATES_DICT)


@require_POST
def attach_network_to_router(request):
    """ 现在是单子网 操作连接和断开操作传入network_id 取第一个子网操作，
        如果改为多子网，则需要页面传入指定子网进行连接和断开操作
        :param request:
        :return:
    """

    network_id = request.data['network_id']
    router_id = request.data['router_id']

    if not router_id:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Unkown router')})

    network = Network.objects.get(pk=network_id)
    subnet = network.subnet_set.all()[0]

    if check_router_isexits_subnet(subnet):
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('network exist address , not operation')})

    network.change_status(NETWORK_STATE_UPDATING)

    Operation.log(obj=network,
                  obj_name=network.name,
                  action='attach_router')

    try:
        tasks.attach_network_to_router.delay(network_id, router_id, subnet.id)
        return Response({"OPERATION_STATUS": 1,
                         "MSG": _('Link router success')})
    except Exception as e:
        LOG.exception("Attach router error, msg: %s", e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Link router error')})


@require_POST
def detach_network_from_router(request):

    network_id = request.data['network_id']
    network = Network.objects.get(pk=network_id)

    network.change_status(NETWORK_STATE_UPDATING)

    tasks.detach_network_from_router.delay(network_id)

    Operation.log(obj=network, obj_name=network.name,
                  action='attach_router', result=1)

    return Response({"OPERATION_STATUS": 1, "MSG": _('Leave router success ')})


@api_view(['GET'])
def subnet_list_view(request):
    query_set = Subnet.objects.filter(deleted=False, network__deleted=False, user=request.user,
                                      user_data_center=request.session["UDC_ID"], status=NETWORK_STATE_ACTIVE)

    serializer = SubnetSerializer(query_set, many=True)
    return Response(serializer.data)


def check_router_isexits_subnet(subnet):
    interface_set = RouterInterface.objects.filter(user=subnet.user, deleted=False, subnet__address=subnet.address)
    if interface_set:
        return True
    return False


@api_view(['GET', 'POST'])
def router_list_view(request):
    router_set = Router.objects.filter(deleted=False,  user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = RouterSerializer(router_set,many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def router_create_view(request):
    data = request.data
    if (not request.POST.get('id', '')) and \
            settings.SITE_CONFIG.get("MULTI_ROUTER_ENABLED", False):
        try:
            serializer = RouterSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                router = serializer.save()
                router_create_task.delay(router)
                Operation.log(obj=router, obj_name=router.name, action='create', result=1)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Create router success')})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Valid Router fail')})
        except Exception as e:
            LOG.error("Create router error ,msg:%s" % e)
            return Response({"OPERATION_STATUS": 0, "MSG": _('Create router fail')})
    else:
        router = Router.objects.get(pk=data.get('id'))
        if router is None:
            return Response({"OPERATION_STATUS": 0, "MSG": _('The selected router not exist')})
        router.name = data.get('name')
        router.deleted = False
        Operation.log(obj=router, obj_name=router.name, action='update', result=1)
        if not router.is_gateway and request.POST.get('is_gateway') == u'true':
            router.status = NETWORK_STATE_UPDATING
            router.save()
            router_add_gateway_task.delay(router)
        elif router.is_gateway and request.POST.get('is_gateway') == u'false':
            router.status = NETWORK_STATE_UPDATING
            router.save()
            router_remove_gateway_task.delay(router)
        else:
            router.save()
        return Response({"OPERATION_STATUS": 1, "MSG": _('Update router success')})


@api_view(['GET', 'POST'])
def router_delete_view(request):

    if not settings.MULTI_ROUTER_ENABLED:
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('Cannot delete router '
                                  'under single router mode.')})

    router_id = request.data['router_id']

    try:
        router = Router.objects.get(pk=router_id)
    except Router.DoesNotExist:
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('The selected router does not exist')})

    if router.is_default:
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('Default Router can not be deleted')})

    if router.is_in_use:
        return Response({"OPERATION_STATUS": 0,
                         "MSG": _('This router is being used.')})

    router.fake_delete()
    Operation.log(obj=router, obj_name=router.name, action='terminate')
    router_delete_task.delay(router)

    return Response({"OPERATION_STATUS": 1, "MSG": _('Router deleted success')})


@api_view(['GET'])
def router_search_view(request):
    router_set = Router.living.filter(status=NETWORK_STATE_ACTIVE,
                                      deleted=False, user=request.user,
                                      user_data_center=request.session["UDC_ID"])
    serializer = RouterSerializer(router_set, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def network_topology_data_view(request):
    routers = Router.objects.filter(deleted=False,  user=request.user, user_data_center=request.session["UDC_ID"])

    router_interface = RouterInterface.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    networks = Network.objects.filter(deleted=False,  user=request.user, user_data_center=request.session["UDC_ID"])
    instances = Instance.objects.filter(deleted=False,  user=request.user, user_data_center=request.session["UDC_ID"])
    network_data = dict()
    network_data['routers'] = RouterSerializer(routers, many=True).data
    network_data['networks'] = NetworkSerializer(networks, many=True).data
    network_data['router_interfaces'] = RouterInterfaceSerializer(router_interface, many=True).data
    network_data['instances'] = InstanceSerializer(instances, many=True).data
    return Response(network_data)
