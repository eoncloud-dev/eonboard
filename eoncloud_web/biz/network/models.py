# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from biz.network.settings import NETWORK_STATES, NETWORK_STATE_BUILD
from biz.common.mixins import LivingDeadModel


class Network(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Network Name'), null=False, blank=False, max_length=128)
    network_id = models.CharField(_('OS Network UUID'), null=True, blank=True, max_length=128)
    status = models.IntegerField(_("Status"), null=False, blank=False, choices=NETWORK_STATES, default=0)
    is_default = models.BooleanField(_("Default"), null=False, blank=False, default=False)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)

    class Meta:
        db_table = "network"
        verbose_name = _("Network")
        verbose_name_plural = _("Network")

    @property
    def net_address(self):
        try:
            subnet_set = Subnet.objects.filter(deleted=False, network=self)
            return '\n'.join(subnet.address for subnet in subnet_set)
        except Subnet.DoesNotExist:
            return ''

    @property
    def router(self):
        interface_set = RouterInterface.objects.filter(network_id=self.id,
                                                       deleted=False)
        return '\n'.join(router_interface.router.name
                         for router_interface in interface_set)

    def change_status(self, status, save=True):
        self.status = status
        if save:
            self.save()

    @property
    def is_in_use(self):
        from biz.instance.models import Instance

        interface_set = RouterInterface.objects.filter(
            network_id=self.id, deleted=False)
        instance_set = Instance.objects.filter(
            network_id=self.id, deleted=False)

        return interface_set.exists() or instance_set.exists()


class Subnet(models.Model):
    IP_VERSION_CHOICES = (
        (4, "IP V4"),
        (6, "IP V6"),
    ) 
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Network Name'), null=False,
                            blank=False, max_length=128)
    network = models.ForeignKey(Network)
    subnet_id = models.CharField(_('OS Subnet UUID'), null=True,
                                 blank=True, max_length=128)

    address = models.CharField(_("IPv4 CIDR"), null=False,
                               blank=False, max_length=128)
    ip_version = models.IntegerField(_("IP Version"), null=False, blank=False,
                                     default=4, choices=IP_VERSION_CHOICES)

    status = models.IntegerField(_("Status"), null=False, blank=False,
                                 choices=NETWORK_STATES,
                                 default=NETWORK_STATE_BUILD)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)

    class Meta:
        db_table = "subnet"
        verbose_name = _("Subnet")
        verbose_name_plural = _("Subnet")


class Router(LivingDeadModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Router Name'), null=False, blank=False, max_length=128)
    router_id = models.CharField(_('OS Router UUID'), null=True, blank=True, max_length=128)
    gateway = models.CharField(_('OS Router UUID'), null=True, blank=True, max_length=128)
    is_gateway = models.BooleanField(_("Whether to open the gateway"), null=False, blank=False, default=False)
    status = models.IntegerField(_("Status"), null=False, blank=False, choices=NETWORK_STATES, default=0)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    deleted = models.BooleanField(_("Deleted"), null=False, blank=False, default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    is_default = models.BooleanField(_("Default"), null=False, blank=False, default=False)

    class Meta:
        db_table = "router"
        verbose_name = _("Router")
        verbose_name_plural = _("Router")

    @property
    def is_in_use(self):
        return RouterInterface.living.filter(router=self).exists()

    def change_status(self, status, save=True):
        self.status = status
        if save:
            self.save()

    def fake_delete(self):
        self.deleted = True
        self.save()


class RouterInterface(LivingDeadModel):
    id = models.AutoField(primary_key=True)
    os_port_id = models.CharField(_('Port'), null=True, blank=True, max_length=128)
    router = models.ForeignKey('network.Router')
    subnet = models.ForeignKey('network.Subnet')
    network_id = models.IntegerField(_("Network"), null=True, blank=True)
    deleted = models.BooleanField(_("Deleted"), null=False, blank=False, default=False)

    user = models.ForeignKey('auth.User', null=True, default=None)
    user_data_center = models.ForeignKey('idc.UserDataCenter', null=True, default=None)

    class Meta:
        db_table = "router_interface"
        verbose_name = _("RouterInterface")
        verbose_name_plural = _("RouterInterface")

    def fake_delete(self):
        self.deleted = True
        self.save()
