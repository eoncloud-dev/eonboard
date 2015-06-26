#coding=utf-8

import random
from django.db.models import Count, Q
from biz.account.models import Operation
from biz.backup.models import BackupItem
from biz.backup.settings import BACKUP_STATE_RESTORING, \
                BACKUP_STATE_PENDING_RESTORE
from biz.instance.models import Instance
from biz.instance.settings import ALLOWED_INSTANCE_ACTIONS, \
                            INSTANCE_ACTION_NEXT_STATE
from cloud.tasks import instance_action_task, instance_get_vnc_console

OPERATION_SUCCESS = 1
OPERATION_FAILED = 0
OPERATION_FORBID = 2

def get_instance_vnc_console(instance):
    vnc = instance_get_vnc_console(instance) 
    if vnc and vnc.url:
        return {"OPERATION_STATUS": OPERATION_SUCCESS, "vnc_url": vnc.url}
    else:
        return {"OPERATION_STATUS": OPERATION_FAILED}


def instance_action(user, DATA):
    """
    Instance action, action is a string
    """
    instance_id = DATA.get("instance")
    action = DATA.get("action")
   
    if action not in ALLOWED_INSTANCE_ACTIONS.keys():
        return {"OPERATION_STATUS": OPERATION_FAILED, 
                "status": "un supported action [%s]" % action}

    instance = Instance.objects.get(pk=instance_id,
                                    user=user,
                                    deleted=False)

    # restoring instance can't do any action!
    restoring = BackupItem.objects.filter(deleted=False,
            resource_id=instance_id,
            resource_type=instance.__class__.__name__,
            status__in=[BACKUP_STATE_RESTORING, BACKUP_STATE_PENDING_RESTORE]
            )
    if len(restoring) > 0:
        return {"OPERATION_STATUS": OPERATION_FORBID, 
            "status": "Restoring....."}

    Operation.log(instance, obj_name=instance.name, action=action, result=1)
    
    if action == "vnc_console":
        return get_instance_vnc_console(instance)
    
    instance.status = INSTANCE_ACTION_NEXT_STATE[action]
    instance.save()

    instance_action_task.delay(instance, action)

    return {"OPERATION_STATUS": OPERATION_SUCCESS, "status": instance.status}
