#-*- coding=utf-8 -*-

import logging
import time
import traceback

from django.conf import settings
from cloud.celery import app


from fabric import tasks
from fabric.api import run
from fabric.api import env
from fabric.network import disconnect_all

from biz.backup.models import Backup
from biz.backup.settings import BACKUP_STATE_BACKUPING, \
            BACKUP_STATE_AVAILABLE, BACKUP_STATE_ERROR, \
            BACKUP_STATE_PENDING_RESTORE, BACKUP_STATE_DELETING, \
            BACKUP_STATE_DELETED, BACKUP_ACTION_NEXT_STATE, \
            BACKUP_STATE_WAITING, BACKUP_STATE_PENDING_DELETE, \
            BACKUP_STATE_RESTORING

LOG = logging.getLogger("cloud.tasks")

env.hosts = [
   settings.BACKUP_RBD_HOST, 
]

env.passwords = {
    settings.BACKUP_RBD_HOST: settings.BACKUP_RBD_HOST_PWD,
}

def _format_pool(backup_item):
    if backup_item.resource_type == "Instance":
        return ("%s_disk" % backup_item.resource_uuid,
                settings.RBD_COMPUTE_POOL)

    if backup_item.resource_type == "Volume":
        return ("volume-%s" % backup_item.resource_uuid,
                settings.RBD_VOLUME_POOL)

    raise Exception("not supported resource_type (%s)" % backup_item.resource_type)

def rbd_backup(backup_item): 
    LOG.info("BackupItem task start, [%s][%s][id:%s] action: [backup]" % (
            backup_item.resource_type, backup_item.resource_name,
            backup_item.resource_id)) 
    
    if backup_item.status != BACKUP_STATE_WAITING:
        LOG.info("BackupItem task start, status error: [%s][=%s]"
                    % backup_items.status, BACKUP_STATE_WAITING)
        return

    backup_item.status = BACKUP_STATE_BACKUPING
    backup_item.save()

    img, pool = _format_pool(backup_item)
    args = settings.BACKUP_COMMAND_ARGS.copy()
    args["source_pool"] = pool
    args["image"] = img
    args["mode"] = "full"
    cmd = settings.BACKUP_COMMAND % args
    result = run(cmd)
    
    if result.return_code == 0:
        backup_item.status = BACKUP_STATE_AVAILABLE
        backup_item.rbd_image = result
        backup_item.save()
    else:
        backup_item.rbd_image = "cmd error!"
        backup_item.status = BACKUP_STATE_ERROR
        backup_item.save()


    LOG.info("BackupItem task end, [%s][%s][id:%s] action: [backup][%s]" % (
            backup_item.resource_type, backup_item.resource_name,
            backup_item.resource_id, result)) 

    return result

def rbd_restore(backup_item):
    LOG.info("BackupItem task start, [%s][%s][id:%s] action: [restore]" % (
            backup_item.resource_type, backup_item.resource_name,
            backup_item.resource_id)) 

    if backup_item.status != BACKUP_STATE_PENDING_RESTORE:
        LOG.info("BackupItem task start, status error: [%s][=%s]"
                    % backup_items.status, BACKUP_STATE_PENDING_RESTORE)
        return

    backup_item.status = BACKUP_STATE_RESTORING
    backup_item.save()

    img, pool = _format_pool(backup_item)
    args = settings.BACKUP_COMMAND_ARGS.copy()
    args["source_pool"] = pool
    args["image"] = img
    args["rbd_image"] = backup_item.rbd_image
    cmd = settings.BACKUP_RESTORE_COMMAND % args
    result = run(cmd)
    
    if result.return_code == 0:
        backup_item.status = BACKUP_STATE_AVAILABLE
        backup_item.save()
    else:
        backup_item.status = BACKUP_STATE_ERROR
        backup_item.save()


    LOG.info("BackupItem task end, [%s][%s][id:%s] action: [restore][%s]" % (
            backup_item.resource_type, backup_item.resource_name,
            backup_item.resource_id, result)) 

    return result

def rbd_delete(backup_item):
    LOG.info("BackupItem task start, [%s][%s][id:%s] action: [delete]" % (
            backup_item.resource_type, backup_item.resource_name,
            backup_item.resource_id)) 

    if backup_item.status != BACKUP_STATE_PENDING_DELETE:
        LOG.info("BackupItem task start, status error: [%s][=%s]"
                    % backup_items.status, BACKUP_STATE_PENDING_DELETE)
        return

    backup_item.status =BACKUP_STATE_DELETING 
    backup_item.save()

    img, pool = _format_pool(backup_item)
    args = settings.BACKUP_COMMAND_ARGS.copy()
    args["source_pool"] = pool
    args["image"] = img
    args["rbd_image"] = backup_item.rbd_image
    cmd = settings.BACKUP_DELETE_COMMAND % args
    result = run(cmd)
    
    if result.return_code == 0:
        backup_item.status = BACKUP_STATE_DELETED
        backup_item.deleted = True
        backup_item.save()
    else:
        backup_item.status = BACKUP_STATE_ERROR
        backup_item.save()


    LOG.info("BackupItem task end, [%s][%s][id:%s] action: [delete][%s]" % (
            backup_item.resource_type, backup_item.resource_name,
            backup_item.resource_id, result)) 

    return result

FUNC_MAPPING = {
    "create": rbd_backup,
    "restore": rbd_restore,
    "delete": rbd_delete,
}

def do_action(backup_item, action, **kwargs):
    func = FUNC_MAPPING[action]
    result = tasks.execute(func, backup_item)
    disconnect_all()


@app.task
def backup_action_task(backup, action, **kwargs):
    LOG.info("Backup task start, [%s][%s] action: [%s]" % (
            backup.id, backup.name, action)) 
    success = "XXX"

    for item in backup.items.all():
        try:
            do_action(item, action, **kwargs)
        except Exception as ex:
            item.status = BACKUP_STATE_ERROR
            item.save()
            LOG.exception(ex)
    else:
        if len(backup.items.all().filter(status=BACKUP_STATE_ERROR,
                                                deleted=False)) > 0:
            backup.status = BACKUP_STATE_ERROR
        else:
            backup.status = BACKUP_ACTION_NEXT_STATE[action]
            if action == "delete":
                backup.deleted = True
            success = ":-)"
        backup.save()
 
    LOG.info("Backup task end, [%s][%s] action: [%s], result[%s]" % (
            backup.id, backup.name, action, success))
