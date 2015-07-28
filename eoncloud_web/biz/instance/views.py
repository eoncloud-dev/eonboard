#coding=utf-8

import re
import logging
from djproxy.views import HttpProxy
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from biz.volume.models import Volume
from biz.volume.serializer import VolumeSerializer
from biz.firewall.models import Firewall
from biz.firewall.serializer import FirewallSerializer
from biz.instance.models import Instance, Flavor
from biz.instance.serializer import InstanceSerializer, FlavorSerializer
from biz.instance.utils import instance_action
from biz.instance.settings import INSTANCE_STATES_DICT, INSTANCE_STATE_RUNNING, MonitorInterval
from biz.account.utils import check_quota
from biz.account.models import Operation

from eoncloud_web.decorators import require_GET
from cloud.instance_task import instance_create_task, instance_get_console_log, instance_get

LOG = logging.getLogger(__name__)


class InstanceList(generics.ListCreateAPIView):
    queryset = Instance.objects.all().filter(deleted=False)
    serializer_class = InstanceSerializer

    def list(self, request):
        try:
            queryset = self.get_queryset().filter(user=request.user)
            serializer = InstanceSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response()

    def create(self, request, *args, **kwargs):
        raise


class InstanceDetail(generics.RetrieveAPIView):
    queryset = Instance.objects.all().filter(deleted=False)
    serializer_class = InstanceSerializer

    def get(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            if obj and obj.user == request.user:
                serializer = InstanceSerializer(obj)
                return Response(serializer.data)
            else:
                raise
        except Exception as e:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FlavorList(generics.ListCreateAPIView):
    queryset = Flavor.objects.all()
    serializer_class = FlavorSerializer

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)


class FlavorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Flavor.objects.all()
    serializer_class = FlavorSerializer


@api_view(["POST"])
def create_flavor(request):
    try:
        serializer = FlavorSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Flavor is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Flavor data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create flavor for unknown reason.')})


@api_view(["POST"])
def update_flavor(request):
    try:
        flavor = Flavor.objects.get(pk=request.data['id'])
        serializer = FlavorSerializer(instance=flavor, data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Flavor is updated successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Flavor data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to update flavor for unknown reason.')})


@api_view(["POST"])
def delete_flavors(request):
    ids = request.data.getlist('ids[]')
    Flavor.objects.filter(pk__in=ids).delete()
    return Response({'success': True, "msg": _('Flavors have been deleted!')}, status=status.HTTP_201_CREATED)


@check_quota(["instance", "vcpu", "memory"])
@api_view(["POST"])
def instance_create_view(request):
    serializer = InstanceSerializer(data=request.data, context={"request": request}) 
    if serializer.is_valid():
        ins = serializer.save()
        Operation.log(ins, obj_name=ins.name, action="launch", result=1)
        instance_create_task.delay(ins, password=request.DATA["password"])
        return Response({"OPERATION_STATUS": 1}, status=status.HTTP_201_CREATED)
    else:
        return Response({"OPERATION_STATUS": 0}, status=status.HTTP_400_BAD_REQUEST) 


@api_view(["POST"])
def instance_action_view(request, pk):
    data = instance_action(request.user, request.DATA)
    return Response(data)


@api_view(["GET"])
def instance_status_view(request):
    return Response(INSTANCE_STATES_DICT)


@api_view(["GET"])
def instance_search_view(request, **kwargs):
    instance_set = Instance.objects.filter(deleted=False, status=INSTANCE_STATE_RUNNING,
                                           user=request.user, user_data_center=request.session["UDC_ID"])
    serializer = InstanceSerializer(instance_set, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def instance_detail_view(request, pk):
    tag = request.GET.get("tag", 'instance_detail')
    try:
        instance = Instance.objects.get(pk=pk, user=request.user)
    except Exception as e:
        LOG.error("Get instance error, msg:%s" % e)
        return Response({"OPERATION_STATUS": 0, "MSG": "Instance no exist"}, status=status.HTTP_200_OK)

    if "instance_detail" == tag:
        instance_data = dict(InstanceSerializer(instance).data)

        try:
            server = instance_get(instance)
            instance_data['host'] = getattr(server, 'OS-EXT-SRV-ATTR:host', None)
            instance_data['instance_name'] = getattr(server, 'OS-EXT-SRV-ATTR:instance_name', None)
        except Exception as e:
            LOG.error("Obtain host fail,msg: %s" % e)

        try:
            firewall = Firewall.objects.get(pk=instance.firewall_group.id)
            firewall_data = FirewallSerializer(firewall).data
            instance_data['firewall'] = firewall_data
        except Exception as e:
            LOG.exception("Obtain firewall fail, msg:%s" % e)

        # 挂载的所有硬盘
        volume_set = Volume.objects.filter(instance=instance, deleted=False)
        volume_data = VolumeSerializer(volume_set, many=True).data
        instance_data['volume_list'] = volume_data
        return Response(instance_data)
    elif 'instance_log' == tag:
        log_data = instance_get_console_log(instance)
        return Response(log_data)

@require_GET
def monitor_settings(request):
    monitor_config = settings.MONITOR_CONFIG.copy()
    monitor_config['INTERVAL_OPTIONS'] = MonitorInterval.\
        filter_options(monitor_config['INTERVAL_OPTIONS'])

    monitor_config.pop('BASE_URL')

    return Response(monitor_config)


class MonitorProxy(HttpProxy):
    base_url = settings.MONITOR_CONFIG['BASE_URL']

    forbidden_pattern = re.compile(r"elasticsearch/.kibana/visualization/")

    def proxy(self):
        url = self.kwargs.get('url', '')

        if self.forbidden_pattern.search(url):
            return HttpResponse('', status=status.HTTP_403_FORBIDDEN)

        return super(MonitorProxy, self).proxy()

monitor_proxy = login_required(csrf_exempt(MonitorProxy.as_view()))
