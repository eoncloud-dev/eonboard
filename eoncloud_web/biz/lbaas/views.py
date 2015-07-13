import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _


from .models import BalancerPool, BalancerMember, BalancerVIP, BalancerMonitor, BalancerPoolMonitor
from .serializer import BalancerPoolSerializer, BalancerMemberSerializer, BalancerVIPSerializer, BalancerMonitorSerializer
from .settings import POOL_ERROR, POOL_ACTIVE, POOL_CREATING, POOL_DELETING, \
    POOL_UPDATING, PROTOCOL_CHOICES, LB_METHOD_CHOICES, MONITOR_TYPE, POOL_STATES_DICT, SESSION_PER_CHOICES
from biz.instance.models import Instance
from biz.floating.models import Floating
from cloud.loadbalancer_task import pool_create_task, pool_update_task, pool_delete_task, pool_vip_create_task, pool_vip_update_task, pool_vip_delete_task,\
    pool_member_create_task, pool_member_update, pool_member_delete_task, pool_monitor_create, pool_monitor_update, \
    pool_monitor_delete, pool_monitor_association_create, pool_monitor_association_delete,vip_associate_floating_ip ,vip_disassociate_floating_ip

from biz.account.models import Operation
LOG = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
def pool_list_view(request, **kwargs):
    query_set = BalancerPool.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = BalancerPoolSerializer(query_set, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def pool_get_view(request, pk=None,**kwargs):
    try:
        pool = BalancerPool.objects.get(pk=pk, user=request.user)
        serializer = BalancerPoolSerializer(pool)
        return Response(serializer.data)
    except Exception as e:
        LOG.error(e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer no exists')})



@api_view(['POST'])
def pool_create_view(request, **kwargs):
    serializer = BalancerPoolSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        pool_id = request.POST.get("pool_id", '')
        '''
        if pool_id is '' add pool ,else update pool
        '''
        if pool_id == '':
            pool = serializer.save()
            pool_create_task.delay(pool)
            Operation.log(pool, obj_name=pool.name, action='create', result=1)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Create balancer pool success')})
        else:
            try:
                pool = BalancerPool.objects.get(pk=pool_id, user=request.user)
                pool.lb_method = request.POST.get("lb_method", pool.lb_method)
                pool.name = request.POST.get("name", pool.name)
                pool.description = request.POST.get('description', pool.description)
                pool.status = POOL_UPDATING
                pool.save()
                pool_update_task.delay(pool)
                Operation.log(pool, obj_name=pool.name, action='update', result=1)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Update balancer pool success')})
            except Exception as e:
                LOG.error(e)
                return Response({"OPERATION_STATUS": 0, "MSG": _('Selected balancer no exist')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer data valid no pass')})


@api_view(['POST'])
def pool_delete_view(request, **kwargs):
    pool_id = request.POST.get('pool_id', '')
    pool = BalancerPool.objects.get(pk=pool_id, user=request.user, user_data_center=request.session["UDC_ID"])
    if pool:
        pool.status = POOL_DELETING
        pool.save()
        pool_delete_task.delay(pool)
        Operation.log(pool, obj_name=pool.name, action='delete', result=1)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Delete balancer pool')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer pool no exist')})


@api_view(['POST'])
def pool_vip_create_view(request, **kwargs):
    serializer = BalancerVIPSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        pool_id = request.POST.get("pool", "")
        pool = BalancerPool.objects.get(pk=pool_id, user=request.user, user_data_center=request.session["UDC_ID"])
        if pool_id and pool:
            '''
            if vip_id is '' add vip ,else update vip
            '''
            vip_id = request.POST.get("vip_id", '')
            if vip_id == '':
                vip = serializer.save()
                pool_vip_create_task(vip)
                pool.vip = vip
                pool.save()
                Operation.log(vip, obj_name=vip.name, action='create', result=1)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Create balancer vip success')})
            else:
                try:
                    vip = BalancerVIP.objects.get(pk=vip_id, user=request.user)

                    vip.session_persistence = request.POST.get('session_persistence', vip.session_persistence)
                    vip.name = request.POST.get('name', vip.name)
                    vip.description = request.POST.get('description', vip.description)
                    vip = BalancerVIP.objects.get(pk=vip_id, user=request.user)

                    v = pool_vip_update_task(vip)
                    Operation.log(vip, obj_name=vip.name, action='update', result=1)
                    if v:
                        vip.save()
                        return Response({"OPERATION_STATUS": 1, "MSG": _('Vip update success')})
                    else:
                        return Response({"OPERATION_STATUS": 0, "MSG": _('Vip update fail')})
                except Exception as e:
                    LOG.error(e)
                    return Response({"OPERATION_STATUS": 0, "MSG": _('Vip no exist')})


        else:
            return Response({"OPERATION_STATUS": 0, "MSG": _('No select balancer pool')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Vip data valid no pass')})


@api_view(['POST'])
def pool_vip_delete_view(request, **kwargs):
    vip_id = request.POST.get('vip_id', '')
    vip = BalancerVIP.objects.get(pk=vip_id, user=request.user, user_data_center=request.session["UDC_ID"])
    if vip:
        vip.status = POOL_DELETING
        vip.save()
        pool_vip_delete_task(vip)
        Operation.log(vip, obj_name=vip.name, action='delete', result=1)
        pool = BalancerPool.objects.get(pk=vip.pool.id)
        if pool:
            pool.vip = None
            pool.save()
        return Response({"OPERATION_STATUS": 1, "MSG": _('Delete balancer vip')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer Vip no exits')})


@api_view(['POST'])
def pool_vip_associate_view(request, **kwargs):
    vip_id = request.POST.get("vip_id", "")
    float_ip_id = request.POST.get("floating_ip_id", "")
    action = request.POST.get("action", '')
    if vip_id == '' or float_ip_id == '':
        return Response({"OPERATION_STATUS": 0, "MSG": _('No select float ip or vip')})
    try:
        vip = BalancerVIP.objects.get(pk=vip_id, user=request.user)
        floating = Floating.objects.get(pk=float_ip_id, user=request.user)

        if action == 'bind':
            p = vip_associate_floating_ip(vip, floating.uuid)
            Operation.log(vip, obj_name=vip.name, action='associate', result=1)
            if p:
                vip.public_address = floating.ip
                vip.save()
                return Response({"OPERATION_STATUS": 1, "MSG": _('Vip association floating success')})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Vip association floating fail')})

        elif action == 'unbind':
            p = vip_disassociate_floating_ip(vip, floating.uuid)
            if p:
                vip.public_address = ''
                vip.save()
                return Response({"OPERATION_STATUS": 1, "MSG": _('Vip disassociation floating success')})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Vip disassociation floating fail')})
    except Exception as e:
        LOG.error(e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Vip or Floating no exist')})


@api_view(['POST'])
def pool_monitor_association_option_view(request, **kwargs):
    pool_id = request.POST.get("pool_id", "")
    monitor_id = request.POST.get("monitor_id", "")
    action = request.POST.get("action", '')
    if pool_id == '' or monitor_id == '':
        return Response({"OPERATION_STATUS": 0, "MSG": _('No select balancer or monitor')})

    try:
        pool = BalancerPool.objects.get(pk=pool_id, user=request.user)
        monitor = BalancerMonitor.objects.get(pk=monitor_id, user=request.user)

        if action =='attach':
            p = pool_monitor_association_create(pool, monitor.monitor_uuid)
            Operation.log(pool, obj_name=pool.name, action='attach', result=1)
            if p:
                BalancerPoolMonitor.objects.create(pool=pool, monitor=monitor)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Balancer monitor association success')})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer monitor association fail')})

        elif action == 'detach':
            p = pool_monitor_association_delete(pool, monitor.monitor_uuid)
            Operation.log(pool, obj_name=pool.name, action='detach', result=1)
            if p:
                pool_monitor_set = BalancerPoolMonitor.objects.filter(pool=pool.id, monitor=monitor.id)
                for pool_monitor in pool_monitor_set:
                    pool_monitor.delete()
                return Response({"OPERATION_STATUS": 1, "MSG": _('Balancer monitor cancel association success')})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer monitor cancel association fail')})
    except Exception as e:
        LOG.error(e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('balancer or monitor no exist')})


@api_view(['GET', 'POST'])
def pool_member_list_view(request, balancer_id=None, **kwargs):
    query_set = BalancerMember.objects.filter(deleted=False, pool=balancer_id, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = BalancerMemberSerializer(query_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def pool_member_create_view(request, **kwargs):
    members = request.POST.get("members")
    serializer = BalancerMemberSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        member_id = request.POST.get("member_id", '')
        pool_id = request.POST.get("pool", '')
        try:
            pool = BalancerPool.objects.get(pk=pool_id, user=request.user)
        except Exception as e:
            LOG.error(e)
            return Response({"OPERATION_STATUS": 0, "MSG": _('Selected balancer no exists')})
        '''
        if member_id is '' add member ,else update member
        '''
        if member_id == "":
            memberA = members.split(',')
            if len(memberA) > 0:
                for m in memberA:
                    member = serializer.save()
                    instance = Instance.objects.get(pk=int(m), user=request.user)
                    member.instance = instance
                    member.save()
                    pool_member_create_task.delay(member)
                    Operation.log(member, obj_name=instance.name, action='create', result=1)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Add member success')})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('No select member')})
        else:
            member = BalancerMember.objects.get(pk=member_id, user=request.user)
            if not member:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Member no exists')})
            member.weight = request.POST.get("weight",'')
            m = pool_member_update(member)
            Operation.log(member, obj_name=member.instance.name, action='update', result=1)
            if m:
                member.save()
                return Response({"OPERATION_STATUS": 1, "MSG": _('Member update success')})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Update member fail')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Member data valid no pass')})


@api_view(['POST'])
def pool_member_delete_view(request, **kwargs):
    member_id = request.POST.get('member_id', '')
    member = BalancerMember.objects.get(pk=member_id)
    if member:
        if member.member_uuid:
            member.status = POOL_DELETING
            member.save()
            pool_member_delete_task.delay(member)
        else:
            member.deleted = True
            member.save()
        Operation.log(member, obj_name=member.instance.name, action='delete', result=1)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Delete balancer member success')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer member no exist')})


@api_view(['GET', 'POST'])
def pool_monitor_list_view(request, **kwargs):
    query_set = BalancerMonitor.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = BalancerMonitorSerializer(query_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def pool_monitor_create_view(request, **kwargs):
    serializer = BalancerMonitorSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        monitor_id = request.POST.get('monitor_id','')
        '''
        if monitor_id is '' add monitor ,else update monitor
        '''
        if monitor_id == '':
            monitor = serializer.save()
            m = pool_monitor_create(monitor)

            if m:
                monitor.monitor_uuid = m.id
                monitor.save()
                Operation.log(monitor, obj_name=monitor.get_type_display(), action='create', result=1)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Create balancer monitor success')})
            else:
                monitor.delete()
                return Response({"OPERATION_STATUS": 0, "MSG": _('Create balancer monitor Fail')})
        else:
            monitor = BalancerMonitor.objects.get(pk=monitor_id, user=request.user)
            if not monitor:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Monitor no exists')})
            monitor.delay = request.POST.get('delay', monitor.delay)
            monitor.timeout = request.POST.get('timeout', monitor.timeout)
            monitor.max_retries = request.POST.get('max_retries', monitor.max_retries)
            m = pool_monitor_update(monitor)
            if m:
                monitor.save()
                Operation.log(monitor, obj_name=monitor.get_type_display(), action='update', result=1)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Update balancer monitor success')})
            else:
                return Response({"OPERATION_STATUS": 0, "MSG": _('Update balancer monitor Fail')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Monitor data valid no pass')})


@api_view(['POST'])
def pool_monitor_delete_view(request, **kwargs):
    monitor_id = request.POST.get('monitor_id', '')
    monitor = BalancerMonitor.objects.get(pk=monitor_id, user=request.user)
    pool_monitor = BalancerPoolMonitor.objects.filter(monitor=monitor_id)
    if len(pool_monitor) > 0:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Monitor is used,can\'t deleted')})
    if monitor:
        pool_monitor_delete(monitor)
        monitor.deleted = True
        monitor.save()
        Operation.log(monitor, obj_name=monitor.get_type_display(), action='delete', result=1)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Delete balancer monitor success')})
    else:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer monitor no exist')})


@api_view(['GET'])
def get_constant_view(request, **kwargs):
    return Response({'protocol': PROTOCOL_CHOICES, 'lb_method': LB_METHOD_CHOICES, "monitor_type": MONITOR_TYPE,
                     "session_per": SESSION_PER_CHOICES})


@api_view(['GET'])
def get_status_view(request, **kwargs):
    return Response(POOL_STATES_DICT)


@api_view(['POST'])
def get_av_monitor_view(request, pool_id, **kwargs):
    action = request.POST.get("action", '')
    if action == 'attach':
        monitors = BalancerMonitor.objects.filter(deleted=False, user=request.user).exclude(monitor_re__pool=pool_id)
        serializer = BalancerMonitorSerializer(monitors, many=True)
        return Response(serializer.data)
    elif action == 'detach':
        monitors = BalancerMonitor.objects.filter(deleted=False, user=request.user).filter(monitor_re__pool=pool_id)
        serializer = BalancerMonitorSerializer(monitors, many=True)
        return Response(serializer.data)