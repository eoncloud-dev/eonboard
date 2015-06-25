#coding=utf-8

from django.utils.translation import ugettext_lazy as _


USER_TYPE_CHOICES = (
    (1, _("Personal")),
    (2, _("Company")),
)

QUOTA_ITEM = (
    ("instance", _("Instance")),
    ("vcpu", _("CPU")),
    ("memory", _("Memory(MB)")),
    ("volume_size", _("Volume(GB)")),
    ("volume", _("Volume Count")),
    ("floating_ip", _("Floating IP")),
)

RESOURCE_CHOICES = (
    ("Instance", _("Instance")),
    ("Volume", _("Volume")),
    ("Network", _("Network")),
    ("Subnet", _("Subnet")),
    ("Router", _("Router")),
    ("Floating", _("Volume")),
    ("Firewall", _("Firewall")),
    ("FirewallRules", _("FirewallRules")),
)

RESOURCE_ACTION_CHOICES = (
    ("reboot", _("reboot")),
    ("power_on", _("power_on")),
    ("power_off", _("power_off")),
    ("vnc_console", _("vnc_console")),
    ("bind_floating", _("bind_floating")),
    ("unbind_floating", _("unbind_floating")),
    ("change_firewall", _("change_firewall")),
    ("attach_volume", _("attach_volume")),
    ("detach_volume", _("detach_volume")),
    ("terminate", _("terminate")),
    ("launch", _("launch")),
    ("create", _("create")),
    ("update", _("update")),
    ("attach_router", _("attach router")),
    ("detach_router", _("detach router")),
)
