# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from .settings import (VOLUME_STATES, VOLUME_TYPES, VOLUME_STATE_CREATING,
                       VOLUME_TYPE_VOLUME, VOLUME_STATE_REJECTED, VOLUME_STATE_ERROR)
from biz.account.models import Notification


class Volume(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Volume name'), null=False, blank=False, max_length=128)
    volume_id = models.CharField(_('OS Volume UUID'), null=True, blank=False, max_length=128)

    size = models.IntegerField(_('Volume size'), null=False, blank=False)
    volume_type = models.IntegerField(_('Volume Type'),  choices=VOLUME_TYPES, default=VOLUME_TYPE_VOLUME)
    status = models.IntegerField(_('Status'), choices=VOLUME_STATES, default=VOLUME_STATE_CREATING)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    deleted = models.BooleanField(_("Deleted"), default=False)

    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')

    instance = models.ForeignKey('instance.Instance', null=True, blank=True)

    class Meta:
        db_table = "volume"
        ordering = ['-create_date']
        verbose_name = _("Volume")
        verbose_name_plural = _("Volume")

    @property
    def workflow_info(self):
        return _("Volume: %(name)s / %(size)d GB") % {'name': self.name, 'size': self.size}

    def workflow_approve_callback(self, flow_instance):
        from cloud.volume_task import volume_create_task

        try:
            self.status = VOLUME_STATE_CREATING
            self.save()

            volume_create_task.delay(self)

            content = title = _('Your application for %(size)d GB volume named %(name)s is approved! ') \
                % {'size': self.size, 'name': self.name}
            Notification.info(flow_instance.owner, title, content, is_auto=True)
        except:

            self.status = VOLUME_STATE_ERROR
            self.save()
            title = _('Error happened to your application for volume')

            content = _('Your application for %(size)d GB volume named %(name)s is approved, '
                        'but an error happened when creating it.') % {'size': self.size, 'name': self.name}

            Notification.error(flow_instance.owner, title, content, is_auto=True)

    def workflow_reject_callback(self, flow_instance):

        self.status = VOLUME_STATE_REJECTED
        self.save()

        content = title = _('Your application for %(disk_size)d GB volume named %(name)s is rejected! ') \
            % {'disk_size': self.size, 'name': self.name}
        Notification.error(flow_instance.owner, title, content, is_auto=True)
