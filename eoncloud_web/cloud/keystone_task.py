#-*-coding=utf-8-*-

import datetime
import logging
import random

from django.conf import settings

from celery import app
from api import keystone
from biz.account.models import Contract
from biz.idc.models import UserDataCenter
from cloud.cloud_utils import create_rc_by_dc
from cloud.network_task import edit_default_security_group

LOG = logging.getLogger("cloud.tasks")


@app.task
def link_user_to_dc_task(user, datacenter):
    LOG.info("New user: Start action [%s]" % user.username)
    rc = create_rc_by_dc(datacenter)
    tenant_name = "%s-%04d" % (settings.OS_NAME_PREFIX, user.id)
    try:
        keystone_user = "%s-%04d-%s" % (settings.OS_NAME_PREFIX,
                                        user.id, user.username.split('@')[0])
    except:
        keystone_user = "%s-%04d-MOCK" % (settings.OS_NAME_PREFIX,
                                          user.id)
    pwd = "cloud!@#%s" % random.randrange(100000, 999999)
    t = keystone.tenant_create(rc,
                               name=tenant_name,
                               description=user.username)
    LOG.info("New user: create tanant [%s][tid:%s]" % (user.username, t.id))
    u = keystone.user_create(rc,
                             name=keystone_user,
                             email=user.email,
                             password=pwd,
                             project=t.id)

    LOG.info("New user: create user [%s][uid:%s]" % (user.username, u.id))
    roles = keystone.role_list(rc)
    admin_role = filter(lambda r: r.name.lower() == "admin", roles)[0]
    keystone.add_tenant_user_role(rc, project=t.id, user=u.id,
                                  role=admin_role.id)
    LOG.info(
        "New user: add role [%s][role:%s]" % (user.username, admin_role.id))

    udc = UserDataCenter.objects.create(
        data_center=datacenter,
        user=user,
        tenant_name=tenant_name,
        tenant_uuid=t.id,
        keystone_user=keystone_user,
        keystone_password=pwd,
    )
    LOG.info(
        "New user: link to datacenter [%s][udc:%s]" % (user.username, udc.id))

    try:
        edit_default_security_group(user, udc)
    except Exception as ex:
        LOG.exception(ex)

    try:
        Contract.objects.create(
            user=user,
            udc=udc,
            name=user.username,
            customer=user.username,
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now(),
            deleted=False
        )
    except Exception as ex:
        LOG.exception(ex)
    return u

