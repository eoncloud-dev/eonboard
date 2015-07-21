#coding=utf-8

import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.decorators import api_view
from rest_framework import status

from biz.instance.models import Instance
from biz.account.models import Operation
from biz.network.models import Network, Subnet, Router, RouterInterface

from biz.network.serializer import SubnetSerializer
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from biz.network.serializer import NetworkSerializer, RouterSerializer, RouterInterfaceSerializer
from biz.instance.serializer import InstanceSerializer

from cloud.network_task import network_and_subnet_create_task, network_delete_task, router_create_task, router_delete_task, \
    network_link_router_task, router_remove_interface_task, router_add_gateway_task, router_remove_gateway_task
from .settings import NETWORK_STATES_DICT, NETWORK_STATE_ACTIVE, NETWORK_STATE_UPDATING, NETWORK_STATE_DELETING

LOG = logging.getLogger(__name__)


@api_view(['GET'])
def network_list_view(request):
    network_set = Network.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = NetworkSerializer(network_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def network_create_view(request):
    network_id = request.POST.get('id', '')
    if not network_id:
        address = request.POST.get('address', '')
        # 检测地址是否已经占用
        if check_address_exist(request,address):
            return Response({"OPERATION_STATUS": 0, "MSG": _('Network address exists')})
        serializer = NetworkSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            network = serializer.save()
            subnet = Subnet.objects.create(name=network.name+"("+address+")",
                                           network=network,
                                           address=address,
                                           ip_version=4,
                                           status=0,
                                           user=network.user,
                                           user_data_center=network.user_data_center)
            try:
                network_and_subnet_create_task.delay(network=network, subnet=subnet)
                Operation.log(obj=network, obj_name=network.name, action='create', result=1)
                return Response({"OPERATION_STATUS": 1, "MSG": _("Create network success")})
            except Exception as e:
                subnet.delete()
                network.delete()
                LOG.error("create network  error ,msg:[%s]" % e)
                return Response({"OPERATION_STATUS": 0, "MSG": _('Create network error')})
        else:
            return Response({"OPERATION_STATUS": 0, "MSG": _('Data valid error')}, status=status.HTTP_400_BAD_REQUEST)
    else:
        network = Network.objects.get(pk=network_id, user=request.user)
        if not network:
            return Response({"OPERATION_STATUS": 0, "MSG": _('The selected network not exist')})
        network.name = request.POST.get("name", '')
        network.deleted = False
        network.save()
        Operation.log(obj=network, obj_name=network.name, action='update', result=1)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Update network success')})


@api_view(['POST', 'GET'])
def delete_action(request):
    try:
        network = Network.objects.get(pk=request.POST.get("network_id", ''), user=request.user)

        # Defalut network can not be deleted
        if network.is_default:
            return Response({"OPERATION_STATUS": 0, "MSG": _('Default network can not be deleted')})
        # Was unable to delete the use of the network
        if check_network_is_use(network.id):
            return Response({"OPERATION_STATUS": 0, "MSG": _('Was unable to delete the use of the network')})
        if not network.network_id:
            network.deleted = True
            network.save()
            return Response({"OPERATION_STATUS": 1, "MSG": _('Network deleted success')})

        network.status = NETWORK_STATE_DELETING
        network.save()
        try:
            network_delete_task.delay(network)
            Operation.log(obj=network, obj_name=network.name, action='terminate', result=1)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Network deleted success')})
        except Exception as e:
            network.status = NETWORK_STATE_ACTIVE
            network.save()
            LOG.error(e)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Network deleted error')})
    except Network.DoesNotExist:
        return Response({"OPERATION_STATUS": 0, "MSG": _('The selected network does not exist')})


@api_view(['GET'])
def network_status_view(request):
    return Response(NETWORK_STATES_DICT)

'''
    现在是单子网 操作连接和断开操作传入network_id 取第一个子网操作，如果改为多子网，则需要页面传入指定子网进行连接和断开操作
    :param request:
    :return:
'''


@api_view(['POST'])
def network_attach_router_view(request):
    action = request.POST.get('action', '')
    network_id = request.POST.get('network_id', '')
    router_id = request.POST.get('router_id', '')
    subnet_set = Subnet.objects.filter(network=network_id, user=request.user, deleted=False)
    # 控制是否存在子网
    if not subnet_set:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Unkown operation')})

    subnet = subnet_set[0]
    if action:
        return network_router_link_operation(subnet, action, router_id)
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Unkown operation')})


def network_router_link_operation(subnet, action, router_id=None):
    # network attach router or detach router function, appoint subnet
    # 1、创建关联关系
    # 2、执行任务
    try:
        if action == 'attach':
            if not router_id:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Unkown router')})
            # check address is exist, exist return or not exist continue
            if check_router_isexits_subnet(subnet):
                return Response({"OPERATION_STATUS": 0, "MSG": _('network exist address , not operation')})

            router = Router.objects.get(pk=router_id,  user=subnet.user, deleted=False)

            router_interface = RouterInterface.objects.create(network_id=subnet.network.id, router=router,
                                                              subnet=subnet, deleted=False,
                                                              user=subnet.user,
                                                              user_data_center=subnet.user_data_center)
            '''
            update router status to updating
            '''
            router.status = NETWORK_STATE_UPDATING
            router.save()
            Operation.log(obj=subnet.network, obj_name=subnet.network.name, action='attach_router', result=1)
            try:
                network_link_router_task.delay(router=router, subnet=subnet, router_interface=router_interface)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Link router success')})
            except Exception as e:
                router_interface.delete()
                router.status = NETWORK_STATE_ACTIVE
                router.save()
                LOG.error("Attach router error, msg: %s " % e)
                return Response({"OPERATION_STATUS": 0, "MSG": _('Link router error')})

        elif action == 'detach':
            router_interface_set = RouterInterface.objects.filter(network_id=subnet.network.id, subnet=subnet)
            for router_interface in router_interface_set:
                router_interface.deleted = True
                router_interface.save()
                router = Router.objects.get(pk=router_interface.router.id, user=subnet.user)
                router.status = NETWORK_STATE_UPDATING
                router.save()
                try:
                    router_remove_interface_task.delay(router=router_interface.router, subnet=subnet, router_interface=router_interface)
                except Exception as e:
                    LOG.error("Detach router error, msg: %s " % e)
                    router_interface.deleted = False
                    router_interface.save()
                    return Response({"OPERATION_STATUS": 0, "MSG": _('Network operation error')})
            Operation.log(obj=subnet.network, obj_name=subnet.network.name, action='attach_router', result=1)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Leave router success ')})
    except Exception as e:
        LOG.info('Network operation error ,%s' % e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Network operation error')})


@api_view(['GET'])
def subnet_list_view(request):
    query_set = Subnet.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"],
                                          status=NETWORK_STATE_ACTIVE)

    serializer = SubnetSerializer(query_set, many=True)
    return Response(serializer.data)


def check_network_is_use(network_id):
    interface_set = RouterInterface.objects.filter(network_id=network_id, deleted=False)
    instance_set = Instance.objects.filter(network_id=network_id, deleted=False)
    if interface_set or instance_set:
        return True
    return False


def check_is_add_router(network_id):
    subnet_set = Subnet.objects.filter(network=network_id, deleted=False)
    if subnet_set is None:
        return True
    return False


def check_router_isexits_subnet(subnet):
    interface_set = RouterInterface.objects.filter(user=subnet.user, deleted=False, subnet__address=subnet.address)
    if interface_set:
        return True
    return False


def check_address_exist(request, address):
    subnet_set = Subnet.objects.filter(user=request.user, deleted=False, address=address)
    if subnet_set:
        return True
    return False
'''
==========================network operation end =============
'''


'''
==========================router============
'''

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
    data = request.data
    if request.POST.get("router_id", '') and \
            settings.SITE_CONFIG.get("MULTI_ROUTER_ENABLED", False):
        router = Router.objects.get(pk=data.get('router_id'))
        if router.is_default:
            return Response({"OPERATION_STATUS": 0, "MSG": _('Default Router can not be deleted')})
        '''
        Router used not deleted
        '''
        if check_router_is_use(router.id):
            return Response({"OPERATION_STATUS": 0, "MSG": _('Router used can not deleted')})
        router.deleted = True
        router.save()
        Operation.log(obj=router, obj_name=router.name, action='terminate', result=1)
        router_delete_task.delay(router)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Router deleted success')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('The selected router does not exist')})


@api_view(['GET'])
def router_search_view(request):
    router_set = Router.objects.filter(status=NETWORK_STATE_ACTIVE, deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = RouterSerializer(router_set, many=True)
    return Response(serializer.data)


def check_router_is_use(router_id):
    router_interface_set = RouterInterface.objects.filter(deleted=False, router=router_id)
    if router_interface_set is None:
        return True
    return False


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
