#-*-coding=utf-8-*- 

import logging
import time
import traceback

from django.conf import settings

from celery import app

from biz.instance.models import Instance
from biz.instance.settings import INSTANCE_STATE_RUNNING, \
            INSTANCE_STATE_BOOTING, INSTANCE_STATE_ERROR, INSTANCE_ACTIONS_DICT, \
            INSTANCE_STATE_DELETE, INSTANCE_STATE_POWEROFF, INSTANCE_STATE_PAUSED
from biz.volume.settings import VOLUME_STATE_AVAILABLE, VOLUME_STATE_IN_USE,\
            VOLUME_STATE_ERROR
from biz.network.models import Network, Subnet
from biz.firewall.models import Firewall
from biz.image.settings import WINDOWS, LINUX

from cloud_utils import create_rc_by_instance
from network_task import create_default_private_network
from cloud import volume_task
from cloud import backup_task

from api import nova

LOG = logging.getLogger("cloud.tasks")

def flavor_create(instance=None):
    rc = create_rc_by_instance(instance)
    try:
        flavor = nova.flavor_create(rc,
                                 name="flavor-%04d%04d" % (
                                     instance.user.id, instance.id),
                                 memory=instance.memory,
                                 vcpu=instance.cpu,
                                 disk=instance.sys_disk,
                                 is_public=False)
        return flavor
    except Exception as e:
        LOG.exception(e)
        return False


def flavor_delete(instance):
    rc = create_rc_by_instance(instance)
    try:
        nova.flavor_delete(rc, instance.flavor_id)
        return True
    except Exception as e:
        LOG.exception(e)
        return False


def instance_create(instance, password):
    user_data_format = "#cloud-config\npassword: %s\nchpasswd: { expire: False }\nssh_pwauth: True\n"
    user_data = user_data_format % password
    rc = create_rc_by_instance(instance)
    try:
        if instance.image.os_type ==  LINUX:
            server = nova.server_create(rc,
                    name=instance.name,
                    image=instance.image.uuid,
                    flavor=instance.flavor_id,
                    key_name=None,
                    security_groups=[],
                    nics = [{"net-id": instance.network.network_id, "v4-fixed-ip": ""}],
                    user_data = user_data
                ) 
        elif instance.image.os_type == WINDOWS:
            server = nova.server_create(rc,
                    name=instance.name,
                    image=instance.image.uuid,
                    flavor=instance.flavor_id,
                    key_name=None,
                    user_data=None,
                    security_groups=[],
                    nics = [{"net-id": instance.network.network_id, "v4-fixed-ip": ""}],
                    meta = {"admin_pass": password},
                )
        else:
            raise Exception("unknown image os type.")
        return server
    except Exception as e:
        LOG.exception(e)
        return False

def instance_get(instance):
    rc = create_rc_by_instance(instance)
    try:
        return nova.server_get(rc, instance.uuid)
    except nova.nova_exceptions.NotFound as e:
        return None
    except Exception as e:
        LOG.exception(e)
        return None


def instance_get_vnc_console(instance):
    rc = create_rc_by_instance(instance)
    try:
        return nova.server_vnc_console(rc, instance_id=instance.uuid)
    except Exception as e:
        LOG.exception(e)
        return None


def instance_get_console_log(instance, tail_length=None):
    rc = create_rc_by_instance(instance)
    try:
        return nova.server_console_output(rc, instance.uuid, tail_length=tail_length)
    except Exception as e:
        LOG.exception(e)
        return None
        

def instance_deleted_release_resource(instance):
    # floatings
    from biz.floating.models import Floating
    from biz.floating.settings import FLOATING_AVAILABLE
    floatings = Floating.objects.filter(instance=instance, deleted=0) 
    for f in floatings:
        LOG.info('Release instance floating:[%s][%s][floating:%s]' % (
                    instance.id, instance.name, f.ip))
        f.instance = None
        f.status = FLOATING_AVAILABLE
        f.save()

    # volumes
    from biz.volume.models import Volume
    volumes = Volume.objects.filter(instance=instance, deleted=0)
    for vol in volumes:
        LOG.info('Release instance volume:[%s][%s][volume:%s]' % (
                    instance.id, instance.name, vol.name))
        vol.instance = None
        vol.status = VOLUME_STATE_AVAILABLE
        vol.save()

    # release backup
    from biz.backup.models import Backup, BackupItem
    for item in BackupItem.objects.filter(
                    resource_id=instance.id,
                    resource_type="Instance",
                    deleted=False):
        LOG.info('Release instance backup:[%s][%s][backup:%s]' % (
                    instance.id, instance.name, item.backup.name))
        item.backup.mark_delete()
        backup_task.backup_action_task(item.backup, "delete")

@app.task
def instance_create_task(instance, **kwargs):
    password = kwargs.get("password", None)
    if not instance or not password:
        return

    LOG.info('begin to start create instance:[%s][%s][pwd:%s]' % (
                    instance.id, instance.name, password))
     
    # create flavor
    flavor = flavor_create(instance)
    if not flavor:
        LOG.error('create flavor error!!! instance:[%s][%s]' % (
                    instance.id, instance.name))
        return
    
    instance.flavor_id = flavor.id
    LOG.info('flavor ok instance:[%s][%s]' % (instance.id, instance.name))
 
    # get default private network
    if instance.network_id == 0:
        network = create_default_private_network(instance)
        instance.network_id = network.id

    if not instance.firewall_group:
        f = Firewall.objects.filter(is_default=True,
                            user=instance.user,
                            user_data_center=instance.user_data_center,
                            deleted=False)
        if len(f) > 0:
            instance.firewall_group = f[0]

    instance.save() 
    LOG.info('network ok instance:[%s][%s]' % (instance.id, instance.name))
    
    # create instance  
    server = instance_create(instance, password)
    if not server:
        LOG.info('server create error instance:[%s][%s]' % (instance.id, instance.name))
        return

    instance.uuid = server.id
    instance.status = INSTANCE_STATE_BOOTING
    instance.save()

    count = 0
    while True:
        time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
        srv = instance_get(instance)
        st = srv.status.upper()
        LOG.info('server status rsync instance:[%s][%s][status: %s]' % (instance.id, instance.name, st))
        if st == "ACTIVE":
            instance.status = INSTANCE_STATE_RUNNING
            instance.private_ip = srv.addresses["network-%s" % instance.network.id][0].\
                                        get("addr", "---")
            instance.save()
            count = settings.MAX_COUNT_SYNC + 1
        elif st == "ERROR":
            instance.status = INSTANCE_STATE_ERROR
            instance.save()
            count = settings.MAX_COUNT_SYNC + 1
        elif st == "BUILD":
            pass
        
        count += 1
        if count > settings.MAX_COUNT_SYNC:
            break

    r = flavor_delete(instance)
    LOG.info("delete flavor instance:[%s][%s][result: %s]" % (instance.id, instance.name, r))


@app.task
def instance_action_task(instance, action, **kwargs):
    LOG.info("instance: [%s][%s] - Start action [%s]" % (instance.id, instance.name, action))
    rc = create_rc_by_instance(instance)
    try:
        if action == INSTANCE_ACTIONS_DICT["POWER_OFF"]:
            nova.server_stop(rc, instance_id=instance.uuid)
        elif action == INSTANCE_ACTIONS_DICT["POWER_ON"]:
            nova.server_start(rc, instance_id=instance.uuid)
        elif action == INSTANCE_ACTIONS_DICT["REBOOT"]:
            nova.server_reboot(rc, instance_id=instance.uuid)
        elif action == INSTANCE_ACTIONS_DICT["PAUSE"]:
            nova.server_pause(rc, instance_id=instance.uuid)
        elif action == INSTANCE_ACTIONS_DICT["RESTORE"]:
            nova.server_unpause(rc, instance_id=instance.uuid)
        elif action == INSTANCE_ACTIONS_DICT["TERMINATE"]:
            nova.server_delete(rc, instance.uuid)
        else:
            LOG.error("instance: [%s][%s] - unsupported action [%s]" % (instance.id, instance.name, action))
            return
    except:
        LOG.error("instance: [%s][%s] - error for action [%s] : %s" % (instance.id, instance.name, action,
                                                                     traceback.format_exc()))
        instance.status = INSTANCE_STATE_ERROR
        instance.save()

    count = 0
    while True:
        time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
        server = instance_get(instance)

        if server and server.status == u'ERROR':
            instance.status = INSTANCE_STATE_ERROR
            instance.save()
            LOG.error("instance: [%s][%s] - error for action %s" % (instance.id, instance.name, action))
            break

        if server and server.status == u'ACTIVE':
            if action == INSTANCE_ACTIONS_DICT["POWER_ON"] or \
                action == INSTANCE_ACTIONS_DICT["REBOOT"] or \
                action == INSTANCE_ACTIONS_DICT["RESTORE"]:
                instance.status = INSTANCE_STATE_RUNNING
                instance.save()
                LOG.info("instance: [%s][%s] - successfully for action: [%s]" % (instance.id, instance.name, action))
                break

        if server and server.status == u'SHUTOFF':
            if action == INSTANCE_ACTIONS_DICT["POWER_OFF"]:
                instance.status = INSTANCE_STATE_POWEROFF
                instance.save()
                LOG.info("instance: [%s][%s] - successfully for action: [%s]" % (instance.id, instance.name, action))
                break

        if server and server.status == u'PAUSED':
            if action  == INSTANCE_ACTIONS_DICT["PAUSE"]:
                instance.status = INSTANCE_STATE_PAUSED
                instance.save()
                LOG.info("instance: [%s][%s] - successfully for action: [%s]" % (instance.id, instance.name, action))
                break
    
        if not server and action == INSTANCE_ACTIONS_DICT["TERMINATE"]:
            instance.status = INSTANCE_STATE_DELETE
            instance.deleted = 1
            instance.save()
            LOG.info("instance: [%s][%s] - successfully for action: [%s]" % (instance.id, instance.name, action))
            instance_deleted_release_resource(instance)
            break

        count += 1
        if count > settings.MAX_COUNT_SYNC:
            LOG.info("instance: [%s][%s] - timeout for action: [%s]" % (instance.id, instance.name, action))
            break

    return True


@app.task
def volume_attach_or_detach_task(instance, volume, action, **kwargs):

    if not instance:
        return False
    if not volume:
        return False
    rc = create_rc_by_instance(instance)
    LOG.info("volume attach or detach operation,instance: [%s][%s] - volume: [%s][%s] - action:[%s]" % (instance.id, instance.name, volume.id, volume.name, action))

    '''
    action ==‘attach’ attach volume ,update local volume status ,create VolumeAttachment;
    action =='detach' detach volume ,update local volume status ,delete VolumeAttachment
    '''
    if 'attach' == action:
        nova.instance_volume_attach(rc, volume_id=volume.volume_id, instance_id=instance.uuid, device='')
        count = 0
        while True:
            time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
            cinder = volume_task.volume_get(volume)
            if cinder and cinder.status.upper() == u'ERROR':
                volume.status = VOLUME_STATE_ERROR
                volume.save()
                break
            elif cinder and cinder.status.upper() == u'ERROR_ATTACHING':
                volume.status = VOLUME_STATE_ERROR
                volume.instance = instance
                volume.save()
                break
            elif cinder and cinder.status.upper() == u'IN-USE':
                volume.status = VOLUME_STATE_IN_USE
                volume.instance = instance
                volume.save()
                break
            count += 1
            if count > settings.MAX_COUNT_SYNC:
                LOG.info("volume attach or detach,instance: [%s][%s] - volume: [%s][%s] - timeout for action:[%s]" % (instance.id, instance.name, volume.id, volume.name, action))
                break

    elif 'detach' == action:
        nova.instance_volume_detach(rc, instance_id=instance.uuid, att_id=volume.volume_id)

        count = 0
        while True:
            time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
            cinder = volume_task.volume_get(volume)

            if cinder and cinder.status.upper() == u'ERROR':
                volume.status = VOLUME_STATE_ERROR
                volume.save()
                break
            if cinder and cinder.status.upper() == u'AVAILABLE':
                volume.status = VOLUME_STATE_AVAILABLE
                volume.instance = None
                volume.save()
                break
            count += 1
            if count > settings.MAX_COUNT_SYNC:
                LOG.info("volume attach or detach,instance: [%s][%s] - volume: [%s][%s] - timeout for action:[%s]" % (instance.id, instance.name, volume.id, volume.name, action))
                break

    return True
