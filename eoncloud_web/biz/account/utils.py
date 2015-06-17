#coding=utf-8

import json
from django.conf import settings
from django.http import HttpResponse

from biz.account.models import Contract, Quota
from biz.instance.models import Instance
from biz.volume.models import Volume
from biz.floating.models import Floating


def get_quota_usage(user, udc_id):
    def instance_used(quota):
        instances = Instance.objects.filter(user=user, user_data_center__id=udc_id, deleted=0)
        vcpu_count, memory_count = 0, 0
        for ins in instances:
            vcpu_count += ins.cpu
            memory_count += ins.memory

        d = {}
        d["instance_used"] = len(instances)
        d["vcpu_used"] = vcpu_count
        d["memory_used"] = memory_count

        instance_quota = quota.get("instance", 0)
        vcpu_quota = quota.get("vcpu", 0)
        memory_quota = quota.get("memory", 0)
        d["instance_persent"] = len(instances) * 1.0 / instance_quota if instance_quota > 0 else 0
        d["vcpu_persent"] = vcpu_count * 1.0 / vcpu_quota if vcpu_quota > 0 else 0
        d["memory_persent"] = memory_count * 1.0 / memory_quota if memory_quota > 0 else 0
        return d

    def volume_used(quota):
        volumes = Volume.objects.filter(user=user, user_data_center__id=udc_id, deleted=0)
        volume_size_count = 0
        for volume in volumes:
            volume_size_count += volume.size
        d = {}
        d["volume_used"] = len(volumes)
        d["volume_size_used"] = volume_size_count

        volume_quota = quota.get("volume", 0)
        volume_size_quota = quota.get("volume_size", 0)
        d["volume_persent"] = len(volumes) * 1.0 / volume_quota if volume_quota > 0 else 0
        d["volume_size_persent"] = volume_size_count * 1.0 / volume_size_quota if volume_size_quota > 0 else 0
        return d

    def floating_used(quota):
        floatings = Floating.objects.filter(user=user, user_data_center__id=udc_id, deleted=0)
        d = {}
        d["floating_ip_used"] = len(floatings)

        floating_ip_quota = quota.get("floating_ip", 0)
        d["floating_ip_persent"] = len(floatings) * 1.0 / floating_ip_quota if floating_ip_quota > 0 else 0
        return d

    c = Contract.objects.filter(user=user, udc__id=udc_id, deleted=0)[0]
    quota = c.get_quotas()
    quota.update(instance_used(quota))
    quota.update(volume_used(quota))
    quota.update(floating_used(quota))

    if not settings.QUOTA_CHECK:
        for k in quota.keys():
            quota[k] = 0;

    return quota


def check_quota(resource_checkers):
    def __func__(func):
        def wraprer(request, *args, **kwargs):
            if settings.QUOTA_CHECK:
                quota = get_quota_usage(request.user, request.session["UDC_ID"])
                for resource in resource_checkers:
                    if quota[resource] > 0 and \
                                    quota["%s_used" % resource] >= quota[resource]:
                        d = {"OPERATION_STATUS":0, "status":"not enough quota for [%s]" % resource}
                        return HttpResponse(json.dumps(d), content_type="application/json")
            return func(request, *args, **kwargs)
        return wraprer
    return __func__
