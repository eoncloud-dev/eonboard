# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from biz.network.models import Network
from biz.instance.settings import (INSTANCE_STATE_WAITING,
                                   INSTANCE_STATES, INSTANCE_STATE_REJECTED, INSTANCE_STATE_ERROR)

from biz.floating.models import Floating
from biz.account.models import Notification

LINUX_IMAGE = 2
WINDOWS_IMAGE = 1
IMAGE_TYPE = (
    (LINUX_IMAGE, _("Linux Image")),
    (WINDOWS_IMAGE, _("Windows Image")),
)


class Instance(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Instance Name'), null=False, blank=False, max_length=128)
    status = models.IntegerField(_("Status"), choices=INSTANCE_STATES, 
                                default=INSTANCE_STATE_WAITING)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    terminate_date = models.DateTimeField(_("Terminate Date"), auto_now_add=True)
    cpu = models.IntegerField(_("Cpu Cores"))
    memory = models.IntegerField(_("Memory"))
    sys_disk = models.FloatField(_("System Disk"), null=False, blank=True)
    
    flavor_id = models.CharField(_("OS FlavorID"),null=True, max_length=36)

    image = models.ForeignKey("image.Image", db_column="image_id", null=True, blank=True)
    network_id = models.IntegerField(_("Network"), null=False, blank=False, default=0)
    
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    
    uuid = models.CharField('instance uuid', null=True, blank=True, max_length=128)
    private_ip = models.CharField(_("Private IP"), max_length=255, blank=True, null=True)
    public_ip = models.CharField(_("Public IP"), max_length=255, blank=True, null=True)

    deleted = models.BooleanField(_("Deleted"), default=False)
    
    firewall_group = models.ForeignKey("firewall.Firewall", null=True)

    class Meta:
        db_table = "instance"
        ordering = ['-create_date']
        verbose_name = _("Instance")
        verbose_name_plural = _("Instance")

    @property
    def network(self):
        try:
            network = Network.objects.get(pk=self.network_id) 
        except Network.DoesNotExist:
            network = None
        
        return network
        
    @property
    def floating_ip(self):
        fs = Floating.objects.filter(resource=self.id, deleted=0)
        floating = None
        if len(fs) > 0:
            floating = fs[0]
        
        return floating.ip if floating else None

    @property
    def workflow_info(self):
        return  _("Instance: %(name)s / %(cpu)s CPU/ %(memory)s MB/ %(sys_disk)d GB") \
            % {'name': self.name, 'cpu': self.cpu,
               'memory': self.memory, 'sys_disk': self.sys_disk}

    def __unicode__(self):
        return self.name

    def workflow_approve_callback(self, flow_instance):
        from cloud.instance_task import instance_create_task

        try:
            instance_create_task.delay(self, password=flow_instance.extra_data)

            self.status = INSTANCE_STATE_WAITING
            self.save()

            content = title = _('Your application for instance "%(instance_name)s" is approved! ') \
                % {'instance_name': self.name}
            Notification.info(flow_instance.owner, title, content, is_auto=True)
        except:

            self.status = INSTANCE_STATE_ERROR
            self.save()

            title = _('Error happened to your application for %(instance_name)s') \
                % {'instance_name': self.name}

            content = _('Your application for instance "%(instance_name)s" is approved, '
                        'but an error happened when creating instance.') % {'instance_name': self.name}

            Notification.error(flow_instance.owner, title, content, is_auto=True)

    def workflow_reject_callback(self, flow_instance):

        self.status = INSTANCE_STATE_REJECTED
        self.save()

        content = title = _('Your application for instance "%(instance_name)s" is rejected! ') \
            % {'instance_name': self.name}
        Notification.error(flow_instance.owner, title, content, is_auto=True)


class Flavor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Name'), null=False, blank=False, max_length=128)
    cpu = models.IntegerField(_("Cpu Cores"))
    memory = models.IntegerField(_("Memory MB"))
    price = models.FloatField(_("Price"))
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)

    class Meta:
        db_table = "flavor"
        ordering = ['cpu']
        verbose_name = _("Flavor")
        verbose_name_plural = _("Flavor")
