#coding=utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _


from biz.floating.settings import FLOATING_STATUS, FLOATING_AVAILABLE, RESOURCE_TYPE


class Floating(models.Model):

    id = models.AutoField(primary_key=True) 
    ip = models.CharField(_("Public IP"), max_length=255, blank=True, null=True)
    uuid = models.CharField('Floating uuid', null=True, blank=True, max_length=128)
    fixed_ip = models.CharField('Fixed IP', null=True, blank=True, max_length=128)
    port_id = models.CharField('Port uuid', null=True, blank=True, max_length=128)
    status = models.IntegerField(_("Status"), choices=FLOATING_STATUS, 
                                default=FLOATING_AVAILABLE)
    bandwidth = models.IntegerField(_("Bandwidth MB"), default=2)
    instance = models.ForeignKey('instance.Instance', null=True, blank=True, default=None)

    resource = models.IntegerField(_("Resource"), null=True, blank=True, default=None)
    resource_type = models.CharField(_("reource type"), null=True, blank=True, choices=RESOURCE_TYPE, max_length=40)

    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    delete_date = models.DateTimeField(_("Delete Date"), null=True, blank=True)
    deleted = models.BooleanField(_("Deleted"), default=False)

    @property
    def re_resource(self):
        resource_dict = dict(RESOURCE_TYPE)
        try:
            if resource_dict[self.resource_type] =='INSTANCE':
                from biz.instance.models import Instance
                from biz.instance.serializer import InstanceSerializer
                instance = Instance.objects.get(pk=self.resource, user=self.user)
                return {"id": instance.id, "name": instance.name, "resource_type": self.resource_type}
            elif resource_dict[self.resource_type] =='LOADBALANCER':
                from biz.lbaas.models import BalancerPool
                from biz.lbaas.serializer import BalancerPoolSerializer
                pool = BalancerPool.objects.get(pk=self.resource, user=self.user)
                return {"id": pool.id, "name": pool.name, "resource_type": self.resource_type}
        except Exception as e:
            return {}

    class Meta:
        db_table = "floating"
        ordering = ['-create_date']
        verbose_name = _('Floating')
        verbose_name_plural = _('Floating') 
