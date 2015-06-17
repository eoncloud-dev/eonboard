#coding=utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _


from biz.floating.settings import FLOATING_STATUS, FLOATING_AVAILABLE


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

    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    delete_date = models.DateTimeField(_("Delete Date"), null=True, blank=True)
    deleted = models.BooleanField(_("Deleted"), default=False)

    class Meta:
        db_table = "floating"
        ordering = ['-create_date']
 
