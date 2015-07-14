from django.shortcuts import render

import logging
from rest_framework import status
from rest_framework.decorators import api_view

from biz.firewall.models import Firewall
from biz.instance.models import Instance
from biz.account.models import Operation
from rest_framework.response import Response
from .settings import SECURITY_GROUP_RULES
from .serializer import *
from django.utils.translation import ugettext_lazy as _
from cloud.network_task import security_group_create_task, security_group_delete_task,\
    security_group_rule_delete_task, security_group_rule_create_task, server_update_security_groups_task

LOG = logging.getLogger(__name__)


@api_view(['POST', 'GET'])
def firewall_list_view(request ,**kwargs):
    firewall_set = Firewall.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = FirewallSerializer(firewall_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def firewall_create_view(request, **kwargs):
    serializer = FirewallSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        firewall = serializer.save()
        Operation.log(firewall, obj_name=firewall.name, action="create", result=1)
        try:
            security_group_create_task.delay(firewall)
        except Exception as e:
            firewall.delete()
            LOG.error("Create firewall error, msg:%s" % e)
            return Response({"OPERATION_STATUS": 0, "MSG": _('Firewall create error')})
        return Response({"OPERATION_STATUS": 1, "MSG": _('Creating firewall')}, status=status.HTTP_201_CREATED)
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Data valid error')}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def firewall_delete_view(request, **kwargs):
    data = request.data
    if data.get('id') is None or data.get('id') == '':
        return Response({"OPERATION_STATUS": 0, "MSG": _('Not selected Firewall')})
    firewall = Firewall.objects.get(pk=data.get('id'))
    if firewall is None:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Firewall not exists')})
    if firewall.is_default:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Firewall default can not delete')})
    if check_firewall_use(request, firewall.id):
        return Response({"OPERATION_STATUS": 0, "MSG": _('Firewall used can not delete')})
    else:
        if firewall.firewall_id:
            try:
                security_group_delete_task.delay(firewall)
            except Exception as e:
                LOG.error("Delete firewall error, msg:%s" % e)
                return Response({"OPERATION_STATUS": 0, "MSG": _('Firewall delete error')})
            firewall.deleted = True
            firewall.save()
            Operation.log(firewall, obj_name=firewall.name, action="terminate", result=1)
        else:
            firewall.deleted = True
            firewall.save()
    return Response({"OPERATION_STATUS": 1, "MSG": _('Firewall delete success')})


@api_view(['GET', 'POST'])
def firewall_rule_list_view(request, firewall_id):
    rule_set = FirewallRules.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"],
                                            firewall=firewall_id)
    serializer = FirewallRulesSerializer(rule_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def firewall_rule_create_view(request):
    data =request.data
    firewall_id = data.get('firewall')
    if not firewall_id:
        return Response({'OPERATION_STATUS': 0, 'MSG': _('no selected security group')})
    serializer = FirewallRulesSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        firewall_rule = serializer.save()
        Operation.log(firewall_rule, obj_name=firewall_rule.direction + firewall_rule.protocol, action="create", result=1)
        try:
            security_group_rule_create_task.delay(firewall_rule)
        except Exception as e:
            firewall_rule.delete()
            LOG.error("Create firewall rule error,msg: %s" % e)
            return Response({'OPERATION_STATUS': 0, 'MSG': _('Create firewall rule error')})
        return Response({'OPERATION_STATUS': 1, 'MSG': _('Create firewall rule success')})
    return Response({'OPERATION_STATUS': 0, 'MSG': _('Valid firewall rule nopass')})

@api_view(['POST'])
def firewall_rule_delete_view(request):
    data = request.data
    if data.get('id') is None or data.get('id') == '':
        return Response({"OPERATION_STATUS": 0, "MSG": _('Not selected Firewall rule')})
    firewall_rule = FirewallRules.objects.get(pk=data.get('id'))
    if firewall_rule is None:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Firewall rule not exists')})
    try:
        security_group_rule_delete_task.delay(firewall_rule)
        firewall_rule.deleted = True
        firewall_rule.save()
        Operation.log(firewall_rule, obj_name=firewall_rule.direction + firewall_rule.protocol, action="terminate", result=1)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Firewall rule delete success')})
    except Exception as e:
        LOG.error("Firewall rule delete error ,msg: %s" % e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Firewall rule delete error')})


@api_view(['GET'])
def firewall_rule_view(request):
    return Response(SECURITY_GROUP_RULES)


@api_view(['POST'])
def instance_change_firewall_view(request, **kwargs):
    data = request.data
    if data.get('instance_id') is None:
        return Response({"OPERATION_STATUS": 0, 'MSG': 'No Select Instance'}, status=status.HTTP_200_OK)
    if data.get("firewall_id") is None:
        return Response({"OPERATION_STATUS": 0, 'MSG': 'No Select Firewall'}, status=status.HTTP_200_OK)
    try:
        instance = Instance.objects.get(pk=data.get('instance_id'))
    except Exception as e:
        LOG.error("No find Instance,msg: %s" % e)
        return Response({"OPERATION_STATUS": 0, 'MSG': 'No find Instance'}, status=status.HTTP_200_OK)
    try:
        firewall = Firewall.objects.get(pk=data.get('firewall_id'))
    except Exception as e:
        LOG.error("No find Firewall,msg: %s" % e)
        return Response({"OPERATION_STATUS": 0, 'MSG': 'No find Firewall'}, status=status.HTTP_200_OK)
    try:
        server_update_security_groups_task.delay(instance, firewall)
        instance.firewall_group = firewall
        instance.save()
        Operation.log(instance, obj_name=instance.name, action="change_firewall", result=1)
        return Response({"OPERATION_STATUS": 1, 'MSG': 'Security update firewall success'}, status=status.HTTP_200_OK)
    except Exception as e:
        LOG.error("Server update security group error,msg: %s" % e)
        return Response({"OPERATION_STATUS": 0, 'MSG': 'No find Firewall'}, status=status.HTTP_200_OK)


def check_firewall_use(request,firewall_id):
    instance_set = Instance.objects.filter(deleted=False, user=request.user,
                                           user_data_center=request.session["UDC_ID"], firewall_group=firewall_id)
    if instance_set:
        return True
    return False






