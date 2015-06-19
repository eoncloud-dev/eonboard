#coding=utf-8

from cloud.tasks import allocate_floating_task, floating_action_task
from biz.account.models import Operation
from biz.floating.models import Floating
from biz.floating.settings import ALLOWED_FLOATING_ACTIONS, \
                            FLOATING_ACTION_NEXT_STATE

OPERATION_SUCCESS = 1
OPERATION_FAILED = 0

def allocate_floating(floating):
    Operation.log(floating, obj_name=floating.ip, action='allocate', result=1)
    allocate_floating_task.delay(floating) 
    return {"OPERATION_STATUS": OPERATION_SUCCESS}


def floating_action(user, DATA):
    """
    floating action, action is a string
    """
    floating_id = DATA.get("floating_id")
    act = DATA.get("action")
    kwargs = DATA
   
    if act not in ALLOWED_FLOATING_ACTIONS.keys():
        return {"OPERATION_STATUS": OPERATION_FAILED, "status": "un supported action [%s]" % act}

    floating = Floating.objects.get(pk=floating_id, user=user) 
    floating.status = FLOATING_ACTION_NEXT_STATE[act]
    floating.save()

    Operation.log(floating, obj_name=floating.ip, action=act, result=1)
    
    floating_action_task.delay(floating, act, **kwargs)

    return {"OPERATION_STATUS": OPERATION_SUCCESS, "status": floating.status}
