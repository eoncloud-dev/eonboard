#-*- coding=utf-8 -*-

import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Volume
from biz.instance.models import Instance
from biz.account.models import Operation
from .serializer import VolumeSerializer
from .settings import VOLUME_STATES_DICT, VOLUME_STATE_ATTACHING, VOLUME_STATE_DOWNLOADING, VOLUME_STATE_AVAILABLE, \
    VOLUME_STATE_DELETING, VOLUME_STATE_ERROR, VOLUME_STATE_IN_USE

from cloud.volume_task import volume_create_task,volume_delete_action_task, volume_get
from cloud.instance_task import volume_attach_or_detach_task
from django.utils.translation import ugettext_lazy as _

from biz.account.utils import check_quota

LOG = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
def volume_list_view(request, format=None):
    try:
        volume_set = Volume.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"])
        serializer = VolumeSerializer(volume_set, many=True)
        return Response(serializer.data)
    except Exception as e:
        LOG.info("query volume list error ,msg:[%s]" % e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def volume_list_view_by_instance(request, format=None):
    data = request.data
    if data.get('instance_id') is not None:
        volume_set = Volume.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"], instance=data.get('instance_id'))
        serializer = VolumeSerializer(volume_set, many=True)
        return Response(serializer.data)
    else:
        volume_set = Volume.objects.filter(deleted=False, user=request.user, user_data_center=request.session["UDC_ID"], status=VOLUME_STATE_AVAILABLE)
        serializer = VolumeSerializer(volume_set, many=True)
        return Response(serializer.data)

@check_quota(["volume", "volume_size"])
@api_view(['POST'])
def volume_create_view(request, format=None):
    try:
        serializer = VolumeSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            volume = serializer.save()
            try:
                volume_create_task.delay(volume)
                Operation.log(volume, obj_name=volume.name, action="create", result=1)
                return Response({"OPERATION_STATUS": 1, "MSG": _('Creating Volume')}, status=status.HTTP_201_CREATED)
            except Exception as e:
                LOG.error(e)
                volume.status = VOLUME_STATE_ERROR
                volume.save()
                return Response({"OPERATION_STATUS": 0, "MSG": _('Volume create error')})
        else:
            return Response({"OPERATION_STATUS": 0, "MSG": _('Data valid error')}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("create volume  error ,msg:[%s]" % e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Volume create error')})


@api_view(['POST'])
def volume_update_view(request, format=None):
    try:
        data = request.data
        if data.get('id') is not None:
            volume = Volume.objects.get(pk=data.get('id'))
            Operation.log(volume, obj_name=volume.name, action="update", result=1)
            volume.name = data.get('name')
            volume.save()
            return Response({"OPERATION_STATUS": 1, "MSG": _('Volume update success')}, status=status.HTTP_201_CREATED)
        else:
            return Response({"OPERATION_STATUS": 0, "MSG": _('No select Volume ')}, status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("create volume  error ,msg:[%s]" % e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Volume update error')})

@api_view(['POST'])
def volume_action_view(request, format=None):
    try:
        data = request.data
        action = data.get("action")
        volume = Volume.objects.get(pk=data.get('volume_id'))
        if 'attach' == action or 'detach' == action:
            return volume_attach_or_detach(data, volume, action)
        elif 'delete' == action:
            return delete_action(volume)
        return Response({"OPERATION_STATUS": 1, "MSG": _('Unknown volume action')}, status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("create volume  error ,msg:[%s]" % e)
        return Response({"OPERATION_STATUS": 0, "MSG": _('Volume action error')})


@api_view(['GET'])
def volume_status_view(request, format=None):
    return Response(VOLUME_STATES_DICT)


def volume_attach_or_detach(data, volume, action):
    if 'attach' == action:
        volume.status = VOLUME_STATE_ATTACHING
        instance = Instance.objects.get(pk=data.get('instance_id'))
        volume.save()
        Operation.log(volume, obj_name=volume.name, action="attach_volume", result=1)
        try:
            volume_attach_or_detach_task.delay(instance=instance, volume=volume, action=action)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Attaching volume')}, status=status.HTTP_201_CREATED)
        except Exception as e:
            volume.status = VOLUME_STATE_AVAILABLE
            volume.save()
            LOG.error("Attach volume error ,msg: %s" % e)
            return Response({"OPERATION_STATUS": 0, "MSG": _('Attach volume error')}, status=status.HTTP_201_CREATED)
    elif 'detach' == action:
        volume.status = VOLUME_STATE_DOWNLOADING
        instance = Instance.objects.get(pk=volume.instance.id)
        volume.save()
        Operation.log(volume, obj_name=volume.name, action="detach_volume", result=1)
        try:
            volume_attach_or_detach_task.delay(instance=instance, volume=volume, action=action)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Detaching volume')}, status=status.HTTP_201_CREATED)
        except Exception as e:
            LOG.error("Detach volume error , msg: % s" % e)
            volume.status = VOLUME_STATE_IN_USE
            volume.save()
            return Response({"OPERATION_STATUS": 0, "MSG": _('Detach volume error')}, status=status.HTTP_201_CREATED)


def delete_action(volume):
    if volume.instance is not None:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Volume attached to instance,instance:%(instance)s') % {'instance': volume.instance.name}}, status=status.HTTP_200_OK)

    if volume.volume_id:
        volume.status = VOLUME_STATE_DELETING
        volume.save()
        try:
            volume_delete_action_task.delay(volume)
            Operation.log(volume, obj_name=volume.name, action="terminate", result=1)
            return Response({"OPERATION_STATUS": 1, "MSG": _('Deleting Volume')}, status=status.HTTP_200_OK)
        except Exception as e:
            LOG.error("Delete volume error,msg:%s" % e)
            volume.status = VOLUME_STATE_ERROR
            volume.save()
            return Response({"OPERATION_STATUS": 0, "MSG": _('Deleting Volume error')}, status=status.HTTP_200_OK)
    else:
        volume.deleted = True
        volume.save()
        return Response({"OPERATION_STATUS": 1, "MSG": _('Deleting Volume')}, status=status.HTTP_200_OK)
