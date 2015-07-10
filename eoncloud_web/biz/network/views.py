#coding=utf-8

import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from biz.instance.models import Instance
from biz.account.models import Operation
from biz.network.models import Network, Subnet, Router, RouterInterface

from biz.network.serializer import  SubnetSerializer
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from biz.network.serializer import NetworkSerializer, RouterSerializer, RouterInterfaceSerializer
from biz.instance.serializer import InstanceSerializer

from cloud.network_task import network_create_task, network_delete_task,\
    router_create_task, router_delete_task, network_link_router_task, router_remove_interface_task,\
    router_add_gateway_task, router_remove_gateway_task
from .settings import NETWORK_STATES_DICT, NETWORK_STATE_ACTIVE,NETWORK_STATE_UPDATING

LOG = logging.getLogger(__name__)


@api_view(['GET'])
def network_list_view(request,**kwargs):
    network_set = Network.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = NetworkSerializer(network_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def network_create_view(request, **kwargs):
    data = request.data
    if data.get('id') is None or data.get('id') == '':
        try:
            serializer = NetworkSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                network = serializer.save()
                Operation.log(obj=network, obj_name=network.name, action='create', result=1)
                network_create_task.delay(network=network)
                return Response({"OPERATION_STATUS": 1, "MSG": _("Create network success")})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Data valid error')}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            LOG.error("create network  error ,msg:[%s]" % e)
            return Response({"OPERATION_STATUS": 0, "MSG": _('Create network error')})
    else:
        network = Network.objects.get(pk=data.get('id'))
        if network is None:
            return Response({"OPERATION_STATUS": 0, "MSG": _('The selected network not exist')})
        network.name = data.get('name')
        network.deleted = False
        network.save()
        Operation.log(obj=network, obj_name=network.name, action='update', result=1)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Update network success')})


@api_view(['POST', 'GET'])
def delete_action(request, **kwargs):
    data = request.data
    if data.get("network_id") is not None:
        network = Network.objects.get(pk=data.get('network_id'))
        # Defalut network can not be deleted
        if network.is_default:
            return Response({"OPERATION_STATUS": 0, "MSG": _('Default network can not be deleted')})
        # Was unable to delete the use of the network
        if not check_network_is_use:
            return Response({"OPERATION_STATUS": 0, "MSG": _('Was unable to delete the use of the network')})
        network.deleted = True
        network.save()
        Operation.log(obj=network, obj_name=network.name, action='terminate', result=1)
        network_delete_task.delay(network)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Network deleted success')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('The selected network does not exist')})


@api_view(['GET'])
def network_status_view(request, format=None):
    return Response(NETWORK_STATES_DICT)


@api_view(['POST'])
def network_attach_router_view(request, **kwargs):
    '''
    1、create subnet
    2、创建关联关系
    3、执行任务
    '''
    try:
        data = request.data
        network_id = data.get('network_id')
        address = data.get('address')
        network = Network.objects.get(pk=network_id)
        action = data.get('action')
        '''
        default not allowed operation
        '''
        if network.is_default:
            return Response({"OPERATION_STATUS": 0, "MSG": _('Default network not allow operation')})

        if action == 'attach':
            '''
            check address is exist, exist return or not exist continue
            '''
            if check_subnet_address(network_id, address):
                return Response({"OPERATION_STATUS": 0, "MSG": _('network exist address , not operation')})
            router_id = data.get('router_id')
            router = Router.objects.get(pk=router_id)
            subnet = Subnet.objects.create(name="subnet-00",
                                           network=network,
                                           address=address,
                                           ip_version=4,
                                           status=0,
                                           user=network.user,
                                           user_data_center=network.user_data_center)
            router_interface = RouterInterface.objects.create(network_id=network_id, router=router,
                                                              subnet=subnet, deleted=False,
                                                              user=network.user,
                                                              user_data_center=network.user_data_center)
            '''
            update router status to updating
            '''
            router.status = NETWORK_STATE_UPDATING
            router.save()
            Operation.log(obj=network, obj_name=network.name, action='attach_router', result=1)
            network_link_router_task.delay(router=router, subnet=subnet, router_interface=router_interface)

            return Response({"OPERATION_STATUS": 1, "MSG": _('Link router success')})
        elif action == 'detach':
            Operation.log(obj=network, obj_name=network.name, action='detach_router', result=1)
            if check_is_add_router(network_id):
                return Response({"OPERATION_STATUS": 0, "MSG": _('Network not add subnet ,not operation ')})
            subnet_set = Subnet.objects.filter(network_id=network_id, deleted=False)
            for subnet in subnet_set:
                subnet.deleted = True
                subnet.save()
                router_interface_set = RouterInterface.objects.filter(network_id=network_id, subnet=subnet)
                for router_interface in router_interface_set:
                    router_interface.deleted = True
                    router_interface.save()
                    router_remove_interface_task.delay(router=router_interface.router, subnet=subnet, router_interface=router_interface)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Leave router success ')})
    except Exception as e:
        LOG.info('Network operation error ,%s' % e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Network operation error')})

@api_view(['GET'])
def subnet_list_view(request, **kwargs):
    query_set = Subnet.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"], status=NETWORK_STATE_ACTIVE)
    serializer = SubnetSerializer(query_set,many=True)
    return Response(serializer.data)


def check_network_is_use(network_id):
    subnet_set = Subnet.objects.filter(network=network_id, deleted=False)
    instance_set = Instance.objects.filter(network_id=network_id, deleted=False)
    if subnet_set is None or instance_set is None:
        return True
    return False


def check_is_add_router(network_id):
    subnet_set = Subnet.objects.filter(network=network_id, deleted=False)
    if subnet_set is None:
        return True
    return False


def check_subnet_address(network_id, address):
    subnet_set = Subnet.objects.filter(network=network_id, deleted=False, address=address)
    if subnet_set is None:
        return True
    return False
'''
==========================network operation end =============
'''


'''
==========================router============
'''

@api_view(['GET', 'POST'])
def router_list_view(request, **kwargs):
    router_set = Router.objects.filter(deleted=False,  user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = RouterSerializer(router_set,many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def router_create_view(request, **kwargs):
    data = request.data
    if (data.get('id') is None or data.get('id') == '') and \
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
def router_delete_view(request, **kwargs):
    data = request.data
    if data.get("router_id") is not None and \
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
def router_search_view(request, **kwargs):
    router_set = Router.objects.filter(status=NETWORK_STATE_ACTIVE, deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = RouterSerializer(router_set, many=True)
    return Response(serializer.data)


def check_router_is_use(router_id):
    router_interface_set = RouterInterface.objects.filter(deleted=False, router=router_id)
    if router_interface_set is None:
        return True
    return False


@api_view(['GET'])
def network_topology_data_view(request, **kwargs):
    routers = Router.objects.filter(deleted=False,  user=request.user, user_data_center=request.session["UDC_ID"])

    router_interface = RouterInterface.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    networks =Network.objects.filter(deleted=False,  user=request.user, user_data_center=request.session["UDC_ID"])
    instances = Instance.objects.filter(deleted=False,  user=request.user, user_data_center=request.session["UDC_ID"])
    network_data = {}
    network_data['routers'] = RouterSerializer(routers, many=True).data
    network_data['networks'] = NetworkSerializer(networks, many=True).data
    network_data['router_interfaces'] = RouterInterfaceSerializer(router_interface, many=True).data
    network_data['instances'] = InstanceSerializer(instances, many=True).data
    return Response(network_data)
