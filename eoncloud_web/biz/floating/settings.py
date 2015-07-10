#coding=utf-8

from django.utils.translation import ugettext_lazy as _

FLOATING_ERROR = 0
FLOATING_ALLOCATE = 1
FLOATING_AVAILABLE = 10
FLOATING_BINDED = 20
FLOATING_BINDING = 21
FLOATING_RELEASED = 90
FLOATING_RELEASING = 91


FLOATING_STATUS = (
    (FLOATING_ERROR, _("Floating ERROR")),
    (FLOATING_ALLOCATE, _("Floating Allocate")),
    (FLOATING_AVAILABLE, _("Floating Avaiable")), 
    (FLOATING_BINDED, _("Floating Binded")), 
    (FLOATING_BINDING, _("Floating Binding")), 
    (FLOATING_RELEASED, _("Floating Released")), 
    (FLOATING_RELEASING, _("Floating Releasing")), 
)


# 0表示不稳定，1表示稳定
FLOATING_STATUS_DICT = {
    FLOATING_ERROR: (_("Floating ERROR"), 1),
    FLOATING_ALLOCATE: (_("Floating Allocate"), 0),
    FLOATING_AVAILABLE: (_("Floating Avaiable"), 1), 
    FLOATING_BINDED: (_("Floating Binded"), 1), 
    FLOATING_BINDING: (_("Floating Binding"), 0), 
    FLOATING_RELEASED: (_("Floating Released"), 1), 
    FLOATING_RELEASING: (_("Floating Releasing"), 0), 
}

FLOATING_ACTION_NEXT_STATE = {
    "allocate": FLOATING_AVAILABLE,
    "release": FLOATING_RELEASING,
    "associate": FLOATING_BINDING,
    "disassociate": FLOATING_RELEASING,
}

ALLOWED_FLOATING_ACTIONS = {
    "allocate": _("allocate"),
    "release": _("release"),
    "associate": _("associate"),
    "disassociate": _("disassociate"),
}
#绑定公网IP资源类型
RESOURCE_TYPE = (
    ('INSTANCE', 'INSTANCE'),
    ("LOADBALANCER", 'LOADBALANCER'),
)
