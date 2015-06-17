# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from .settings import VOLUME_STATES, VOLUME_TYPES, VOLUME_STATE_CREATING, VOLUME_TYPE_VOLUME


class Volume(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Volume name'), null=False, blank=False, max_length=128)
    volume_id = models.CharField(_('OS Volume UUID'), null=True, blank=False, max_length=128)

    size = models.IntegerField(_('Volume size'), null=False, blank=False)
    volume_type = models.IntegerField(_('Volume Type'),  choices=VOLUME_TYPES, default=VOLUME_TYPE_VOLUME)
    status = models.IntegerField(_('Status'), choices=VOLUME_STATES, default=VOLUME_STATE_CREATING)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    deleted = models.BooleanField(_("Deleted"), default=False)
    """
    User info
    """
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')

    instance = models.ForeignKey('instance.Instance', null=True, blank=True)

    class Meta:
        db_table = "volume"
        ordering = ['-create_date']
