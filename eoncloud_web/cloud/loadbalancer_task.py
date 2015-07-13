#-*-coding=utf-8-*- 

import datetime
import logging
import time

from django.conf import settings

from celery import app
from cloud_utils import create_rc_by_balancer_pool, \
    create_rc_by_balancer_vip, create_rc_by_balancer_member,\
    create_rc_by_balancer_monitor

from biz.lbaas.settings import POOL_ACTIVE, POOL_ERROR, POOL_DOWN
from biz.lbaas.models import BalancerMember, BalancerPoolMonitor, BalancerVIP

from biz.lbaas.settings import SESSION_PER_CHOICES

from api import lbaas, network

LOG = logging.getLogger("cloud.tasks")


def pool_create(pool=None):
    rc = create_rc_by_balancer_pool(pool)
    try:
        p = lbaas.pool_create(rc,
                                 name="balancer-pool-%04d%04d" % (
                                     pool.user.id, pool.id),
                                 description=pool.description,
                                 subnet_id=pool.subnet.subnet_id,
                                 protocol=pool.get_protocol_display(),
                                 lb_method=pool.get_lb_method_display(),
                                 admin_state_up=pool.admin_state_up,
                                 provider=pool.get_provider_display()
                                 )
        print p
        return p
    except Exception as e:
        LOG.exception(e)
        return None


def pool_update(pool=None):
    rc = create_rc_by_balancer_pool(pool)
    try:
        params = {'pool': {'description': pool.description,
                           'lb_method': pool.get_lb_method_display()
                           }}
        p = lbaas.pool_update(rc, pool_id=pool.pool_uuid, **params)
        print p
        return p
    except Exception as e:
        LOG.exception(e)
        return None


def pool_get(pool=None):
    rc = create_rc_by_balancer_pool(pool)
    try:
        p = lbaas.pool_get(rc,pool_id=pool.pool_uuid)
        return p
    except Exception as e:
        LOG.exception(e)
        return False


def pool_delete(pool=None):
    rc = create_rc_by_balancer_pool(pool)
    try:
        lbaas.pool_delete(rc, pool.pool_uuid)
        return True
    except Exception as e:
        LOG.exception(e)
        return False


def pool_member_create(member=None):
    rc = create_rc_by_balancer_member(member)
    try:
        m = lbaas.member_create(rc,
                                     pool_id=member.pool.pool_uuid,
                                     address=member.instance.private_ip,
                                     protocol_port=member.protocol_port,
                                     weight=member.weight,
                                     admin_state_up=member.admin_state_up
                                     )
        return m
    except Exception as e:
        LOG.exception(e)
        return False


def pool_member_update(member=None):
    rc = create_rc_by_balancer_member(member)
    try:
        params = {"member": {
            "weight":member.weight
        }}
        m = lbaas.member_update(rc, member_id=member.member_uuid, **params)
        return m
    except Exception as e:
        LOG.exception(e)
        return False


def pool_member_get(member=None):
    rc = create_rc_by_balancer_member(member)
    try:
        m = lbaas.member_get(rc,member_id=member.member_uuid)
        return m
    except Exception as e:
        LOG.exception(e)
        return e


def pool_member_delete(member=None):
    rc = create_rc_by_balancer_member(member)
    try:
        lbaas.member_delete(rc,member.member_uuid)
        return True
    except Exception as e:
        LOG.exception(e)
        return False


def pool_vip_create(vip=None):
    rc = create_rc_by_balancer_vip(vip)
    try:
        session_persistence = {}
        if vip.session_persistence != '' and vip.session_persistence is not None:
            session_persistence = {'type': vip.session_persistence_desc}

        v = lbaas.vip_create(rc,
                               name="balancer-vip-%04d%04d" % (
                                   vip.user.id, vip.id),
                               description=vip.description,
                               subnet_id=vip.subnet.subnet_id,
                               protocol_port=vip.protocol_port,
                               protocol=vip.get_protocol_display(),
                               pool_id=vip.pool.pool_uuid,
                               session_persistence=session_persistence,
                               admin_state_up=vip.admin_state_up,
                               connection_limit=vip.connection_limit,
                               address=vip.address
                               )
        return v
    except Exception as e:
        LOG.exception(e)
        return False


def pool_vip_update(vip=None):
    rc = create_rc_by_balancer_vip(vip)
    try:
        session_persistence = {}
        if vip.session_persistence != '' and vip.session_persistence is not None:
            session_persistence = {'type': vip.session_persistence_desc}
        params = {"vip": {
            'description': vip.description,
            'session_persistence': session_persistence
        }}
        v = lbaas.vip_update(rc, vip_id=vip.vip_uuid, **params)
        return v
    except Exception as e:
        LOG.exception(e)
        return False


def pool_vip_get(vip=None):
    rc = create_rc_by_balancer_vip(vip)
    try:
        v = lbaas.vip_get(rc,vip.vip_uuid)
        return v
    except Exception as e:
        LOG.exception(e)
        return False


def pool_vip_delete(vip=None):
    rc = create_rc_by_balancer_vip(vip)
    try:
        lbaas.vip_delete(rc, vip.vip_uuid)
        return True
    except Exception as e:
        LOG.exception(e)
        return False


def vip_associate_floating_ip(vip=None, float_ip_uuid=None):
    rc = create_rc_by_balancer_vip(vip)
    try:
        LOG.info("vip associate floating ip ,float_ip[%s] port[%s]" % (float_ip_uuid, vip.port_id))
        network.floating_ip_associate(rc, float_ip_uuid, vip.port_id+"_"+vip.address)
        return True
    except Exception as e:
        LOG.exception(e)
        return False


def vip_disassociate_floating_ip(vip=None, float_ip_uuid=None):
    rc = create_rc_by_balancer_vip(vip)
    try:
        network.floating_ip_disassociate(rc, float_ip_uuid, vip.port_id)
        return True
    except Exception as e:
        LOG.exception(e)
        return False


def pool_monitor_create(monitor=None):
    rc = create_rc_by_balancer_monitor(monitor)
    try:
        m = lbaas.pool_health_monitor_create(rc,
                                         type=monitor.get_type_display(),
                                         delay=monitor.delay,
                                         timeout=monitor.timeout,
                                         max_retries=monitor.max_retries,
                                         admin_state_up=monitor.admin_state_up,
                                         http_method=monitor.http_method,
                                         url_path=monitor.url_path,
                                         expected_codes=monitor.expected_codes
                                         )
        return m
    except Exception as e:
        LOG.exception(e)
        return False


def pool_monitor_update(monitor=None):
    rc = create_rc_by_balancer_monitor(monitor)
    try:
        params = {"health_monitor": {
                "delay": monitor.delay,
                "timeout": monitor.timeout,
                "max_retries": monitor.max_retries
        }}
        m = lbaas.pool_health_monitor_update(rc, monitor_id=monitor.monitor_uuid,**params)
        return m
    except Exception as e:
        LOG.exception(e)
        return False


def pool_monitor_delete(monitor=None):
    rc = create_rc_by_balancer_monitor(monitor)
    try:
        lbaas.pool_health_monitor_delete(rc,mon_id=monitor.monitor_uuid)
        return True
    except Exception as e:
        LOG.exception(e)
        return False


def pool_monitor_association_create(pool, monitor_uuid):
    rc = create_rc_by_balancer_pool(pool)
    try:
        lbaas.pool_monitor_association_create(rc, pool_id=pool.pool_uuid, monitor_id=monitor_uuid)
        return True
    except Exception as e:
        LOG.exception(e)
        return False


def pool_monitor_association_delete(pool, monitor_uuid):
    rc = create_rc_by_balancer_pool(pool)
    try:
        lbaas.pool_monitor_association_delete(rc, pool_id=pool.pool_uuid, monitor_id=monitor_uuid)
        return True
    except Exception as e:
        LOG.exception(e)
        return False

@app.task
def pool_create_task(pool=None):
    if not pool:
        return False
    LOG.info("begin create balancer pool, id[%s]" % pool.id)
    p = pool_create(pool)
    if p:
        LOG.info("create balancer pool success, id[%s],uuid[%s]" % (pool.id, p.id))
        pool.pool_uuid = p.id
        pool.status = POOL_ACTIVE
        pool.save()
        return True
    else:
        LOG.info("create balancer pool fail, id[%s]" % (pool.id))
        pool.status = POOL_ERROR
        pool.save()
        return False


@app.task
def pool_update_task(pool=None):
    if not pool:
        return False
    LOG.info("begin update balancer pool, id[%s]" % pool.id)
    p = pool_update(pool)
    if p:
        LOG.info("update balancer pool success, id[%s],uuid[%s]" % (pool.id, p.id))
        pool.status = POOL_ACTIVE
        pool.save()
        return True
    else:
        LOG.info("update balancer pool fail, id[%s]" % (pool.id))
        pool.status = POOL_ERROR
        pool.save()
        return False


@app.task
def pool_delete_task(pool=None):
    if not pool:
        return False
    LOG.info("begin delete balancer pool, id[%s],uuid[%s]" % (pool.id, pool.pool_uuid))
    '''
    delete member
    '''
    LOG.info("Begin delete pool member, id[%s]" % (pool.id))
    members = BalancerMember.objects.filter(deleted=False, pool=pool.id)
    if members:
        for member in members:
            pool_member_delete(member)
            member.deleted = True
            member.save()
    '''
    delete vip
    '''
    if pool.vip:
        LOG.info("Begin delete pool vip, pool_id[%s],vip_id[%s]" % (pool.id, pool.vip))
        vip = BalancerVIP.objects.get(pk=pool.vip.id)
        if vip:
            pool_vip_delete(vip)
            vip.deleted = True
            vip.save()
    '''
    unbind monitor
    '''
    LOG.info("Begin delete pool monitor, id[%s]" % (pool.id))
    pool_monitors = BalancerPoolMonitor.objects.filter(pool=pool.id)
    if pool_monitors:
        for pool_monitor in pool_monitors:
            pool_monitor.delete()

    if pool.pool_uuid:
        b = pool_delete(pool)
        if b:
            LOG.info("Delete balancer pool success, id[%s],uuid[%s]" % (pool.id, pool.pool_uuid))
            pool.pool_uuid = ''
            pool.status = POOL_DOWN
            pool.deleted = True
            pool.save()
            return True
        else:
            pool.status =POOL_ERROR
            pool.save()
            return False
    else:
        pool.deleted = True
        pool.save()
        return True


@app.task
def pool_vip_create_task(vip=None):
    if not vip:
        return False
    LOG.info("Begin create balancer vip,id[%s]"% vip.id)
    v = pool_vip_create(vip)
    if v:
        LOG.info("Create balancer vip seuuce, id[%s],uuid[%s]" % (vip.id, v.id))
        print v
        vip.status = POOL_ACTIVE
        vip.vip_uuid = v.id
        vip.address = v.address
        vip.port_id = v.port_id
        vip.save()
    else:
        LOG.error("Create balancer vip fail,id[%s]" % vip.id)
        vip.status = POOL_ERROR
        vip.save()

@app.task
def pool_vip_update_task(vip=None):
    if not vip:
        return False
    LOG.info("Begin update balancer vip,id[%s]"% vip.id)
    v = pool_vip_update(vip)
    if v:
        LOG.info("Update balancer vip seuuce, id[%s],uuid[%s]" % (vip.id, v.id))
        print v
        vip.status = POOL_ACTIVE
        vip.save()
        return v
    else:
        LOG.error("Update balancer vip fail,id[%s]" % vip.id)
        vip.status = POOL_ERROR
        vip.save()
        return False


@app.task
def pool_vip_delete_task(vip=None):
    if not vip:
        return False
    LOG.info("Begin delete balancer vip, id[%s]" % vip.id)
    b = pool_vip_delete(vip)
    if b:
        LOG.info("Delete balancer vip success, id[%s]" % vip.id)
        vip.vip_uuid = ''
        vip.deleted = True
        vip.save()
    else:
        LOG.error("Delete balancer vip fail ,id[%s]" % vip.id)
        vip.status = POOL_ERROR
        vip.save()


@app.task
def pool_member_create_task(member=None):
    if not member:
        return False
    LOG.info("Begin create balancer member, id[%s]" % member.id)
    m = pool_member_create(member)
    if m:
        print m
        LOG.info("Create balancer member success,id[%s],uuid[%s]" % (member.id, m.id))
        member.member_uuid = m.id
        member.status = POOL_ACTIVE
        member.address = m.address
        member.save()
    else:
        LOG.error("Create balancer member fail,id[%s]" % member.id)
        member.status = POOL_ERROR
        member.save()


@app.task
def pool_member_delete_task(member=None):
    if not member:
        return False
    LOG.info("Begin delete balancer member,id[%s]" % member.id)
    b = pool_member_delete(member)
    if b:
        LOG.info("Delete balancer member success, id[%s]" % member.id)
        member.member_uuid = ''
        member.deleted = True
        member.save()
    else:
        LOG.error("Delete balancer member fail ,id[%s]" % member.id)
        member.status = POOL_ERROR
        member.save()



