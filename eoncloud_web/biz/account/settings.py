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
