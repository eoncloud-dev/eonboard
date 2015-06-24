#coding=utf-8

import random
from django.db.models import Count, Q
from biz.account.models import Operation
from biz.instance.models import Instance
from biz.instance.settings import ALLOWED_INSTANCE_ACTIONS, \
                            INSTANCE_ACTION_NEXT_STATE
from cloud.tasks import instance_action_task, instance_get_vnc_console

OPERATION_SUCCESS = 1
OPERATION_FAILED = 0

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
        return {"OPERATION_STATUS": OPERATION_FAILED, "status": "un supported action [%s]" % action}

    instance = Instance.objects.get(pk=instance_id, user=user)


    Operation.log(instance, obj_name=instance.name, action=action, result=1)
    
    if action == "vnc_console":
        return get_instance_vnc_console(instance)
    
    instance.status = INSTANCE_ACTION_NEXT_STATE[action]
    instance.save()

    instance_action_task.delay(instance, action)

    return {"OPERATION_STATUS": OPERATION_SUCCESS, "status": instance.status}
