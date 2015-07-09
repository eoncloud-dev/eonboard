#-*- coding=utf-8 -*-

import logging

from biz.instance.models import Instance
from biz.instance.settings import INSTANCE_STATE_POWEROFF
from biz.account.models import Operation
from biz.backup.models import Backup

from cloud.backup_task import backup_action_task


OPERATION_SUCCESS = 1
OPERATION_FAILED = 0
OPERATION_FORBID = 2
LOG = logging.getLogger(__name__)


def backup_action(user, DATA):
    """
    Backup action, delete, restore
    """
    action, pk = DATA.get('action'), DATA.get('pk')

    if action not in ["delete", "restore"]:
        return {"OPERATION_STATUS": OPERATION_FAILED,
                "status": "un supported action [%s]" % action}
    try:    
        backup = Backup.objects.get(pk=pk, user=user) 
        Operation.log(backup, obj_name=backup.name, action=action, result=1)

        if action == "restore":
            if backup.instance:
                ins = Instance.objects.get(pk=backup.instance)
                if ins.status != INSTANCE_STATE_POWEROFF:
                    return {"OPERATION_STATUS": OPERATION_FORBID,
                            "status": backup.status}

            backup.mark_restore(DATA.get('item_id'))

        if action == "delete":
            backup.mark_delete()

        # celery call
        backup_action_task.delay(backup, action)

        return {"OPERATION_STATUS": OPERATION_SUCCESS, "status": backup.status}
    except Exception as ex:
        LOG.exception(ex)
        return {"OPERATION_STATUS": OPERATION_FAILED}
