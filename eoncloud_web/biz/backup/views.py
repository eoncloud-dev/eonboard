#coding=utf-8

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import generics

from biz.account.models import Operation
from biz.idc.models import UserDataCenter
from biz.backup.models import Backup
from biz.backup.serializer import BackupSerializer
from biz.backup.settings import BACKUP_STATES_DICT
from biz.backup.utils import backup_action
from biz.backup.settings import BACKUP_STATE_DELETED, BACKUP_STATE_BACKUPING
from cloud.backup_task import backup_action_task


class BackupList(generics.ListAPIView):
    queryset = Backup.objects.all()
    serializer_class = BackupSerializer

    def list(self, request):
        udc = UserDataCenter.objects.get(pk=request.session["UDC_ID"])
        queryset = self.get_queryset().filter(
                    user_data_center=udc,
                    user=request.user,
                    deleted=False)
        serializer = BackupSerializer(queryset, many=True)
        
        return Response(serializer.data)


@api_view(["POST"])
def backup_action_view(request):
    return Response(backup_action(request.user, request.DATA),
                    status=status.HTTP_201_CREATED)


@api_view(["POST"])
def backup_create_view(request):
    serializer = BackupSerializer(data=request.data, context={"request": request}) 
    if serializer.is_valid():
        backup = serializer.save()
        backup.create_items()
        Operation.log(backup, obj_name=backup.name, action="create", result=1)
        backup_action_task.delay(backup, "create")
        backup.status = BACKUP_STATE_BACKUPING
        backup.save()
        return Response({"OPERATION_STATUS": 1}, status=status.HTTP_201_CREATED)
    else:
        return Response({"OPERATION_STATUS": 0}, status=status.HTTP_400_BAD_REQUEST) 


@api_view(["GET"])
def backup_status_view(request):
    return Response(BACKUP_STATES_DICT)
