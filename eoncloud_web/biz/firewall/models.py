from django.db import models
from biz.firewall.settings import DIRECTION_EGRESS, DIRECTION_INGRESS, DIRECTIONS, ENTER_TYPE_IPV6, ENTER_TYPE_IPV4, ENTER_TYPES
from django.utils.translation import ugettext_lazy as _


class Firewall(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Firewall Name"), null=False, blank=False, max_length=128)
    firewall_id = models.CharField(_("OS Firewall UUID"), null=True, blank=True, max_length=128)
    desc = models.CharField(_("Firewall desc"), null=True, blank=True, max_length=50)
    is_default = models.BooleanField(_("Default"), null=False, blank=False, default=False)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey("idc.UserDataCenter")
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    deleted = models.BooleanField(_("Deleted"), default=False)

    class Meta:
        db_table = "firewall"


class FirewallRules(models.Model):
    id = models.AutoField(primary_key=True)
    firewall = models.ForeignKey('Firewall')
    firewall_rules_id = models.CharField(_("OS Firewall Rules UUID"), null=True, blank=True, max_length=40)
    direction = models.CharField(_("Direction"), null=True, blank=True, max_length=10, choices=DIRECTIONS, default=DIRECTION_INGRESS)
    ether_type = models.CharField(_("Ether type"), null=True, blank=True, max_length=40, choices=ENTER_TYPES, default=ENTER_TYPE_IPV4)
    port_range_min = models.IntegerField(_("Port range min"), null=True, blank=True, default=0)
    port_range_max = models.IntegerField(_("Port range max"), null=True, blank=True, default=0)
    protocol = models.CharField(_("Protocol"), null=True, blank=True, max_length=40)
    remote_group_id = models.CharField(_("remote group id UUID"), null=True, blank=True, max_length=40)
    remote_ip_prefix = models.CharField(_("remote ip prefix"), null=True, blank=True, max_length=255,
                                        default='0.0.0.0/0')
    is_default = models.BooleanField(_("Default"), null=False, blank=False, default=False)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey("idc.UserDataCenter")
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)

    class Meta:
        db_table = "firewall_rules"
