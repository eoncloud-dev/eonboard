#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

INSTANCE_STATE_WAITING = 0
INSTANCE_STATE_RUNNING = 1
INSTANCE_STATE_BOOTING = 2
INSTANCE_STATE_REBOOTING = 3
INSTANCE_STATE_PAUSED = 4
INSTANCE_STATE_POWEROFF = 5
INSTANCE_STATE_SHUTTING_DOWN = 6
INSTANCE_STATE_DEPLOYING = 7
INSTANCE_STATE_DEPLOY_FAILED = 8
INSTANCE_STATE_LOCKED = 9
INSTANCE_STATE_DELETE = 10
INSTANCE_STATE_ERROR = 11
INSTANCE_STATE_BACKUPING = 12
INSTANCE_STATE_RESTORING = 13
INSTANCE_STATE_RESIZING = 14
INSTANCE_STATE_EXPIRED = 15
INSTANCE_STATE_DELETING = 16
INSTANCE_STATE_APPLYING = 17
INSTANCE_STATE_REJECTED = 18

INSTANCE_STATES = (
    (INSTANCE_STATE_WAITING, _("Instance Waiting")), #0
    (INSTANCE_STATE_RUNNING, _("Instance Running")), #1
    (INSTANCE_STATE_BOOTING, _("Instance Booting")), #2
    (INSTANCE_STATE_REBOOTING, _("Instance Rebooting")),#3
    (INSTANCE_STATE_PAUSED, _("Instance Paused")), #4
    (INSTANCE_STATE_POWEROFF, _("Instance Power Off")),#5
    (INSTANCE_STATE_SHUTTING_DOWN, _("Instance Shutting Down")),
    (INSTANCE_STATE_DEPLOYING, _("Instance Deploying")),
    (INSTANCE_STATE_DEPLOY_FAILED, _("Instance Deploy Failed")),
    (INSTANCE_STATE_LOCKED, _("Instance Locked")),
    (INSTANCE_STATE_DELETE, _("Instance Delete")),
    (INSTANCE_STATE_ERROR, _("Instance Error")),
    (INSTANCE_STATE_BACKUPING, _("Instance Backuping")),
    (INSTANCE_STATE_RESTORING, _("Instance Restoring")),
    (INSTANCE_STATE_RESIZING, _("Instance Resizing")),
    (INSTANCE_STATE_EXPIRED, _("Instance Expired")),
    (INSTANCE_STATE_DELETING, _("Instance Deleting")),
    (INSTANCE_STATE_APPLYING, _("Applying")),
    (INSTANCE_STATE_REJECTED, _("Rejected"))
)


#instance 的状态描述字典,  其中包含描述信息和该状态是否稳定的标识信息
#0表示不稳定，1表示稳定
INSTANCE_STATES_DICT = {
    INSTANCE_STATE_WAITING: (_("Instance Waiting"), 0),
    INSTANCE_STATE_RUNNING: (_("Instance Running"), 1),
    INSTANCE_STATE_BOOTING: (_("Instance Booting"), 0),
    INSTANCE_STATE_REBOOTING: (_("Instance Rebooting"), 0),
    INSTANCE_STATE_PAUSED: (_("Instance Paused"), 1),
    INSTANCE_STATE_POWEROFF: (_("Instance Power Off"), 1),
    INSTANCE_STATE_SHUTTING_DOWN: (_("Instance Shutting Down"), 0),
    INSTANCE_STATE_DEPLOYING: (_("Instance Deploying"), 0),
    INSTANCE_STATE_DEPLOY_FAILED: (_("Instance Deploy Failed"), 1),
    INSTANCE_STATE_LOCKED: (_("Instance Locked"), 1),
    INSTANCE_STATE_DELETE: (_("Instance Delete"), 1),
    INSTANCE_STATE_ERROR: (_("Instance Error"), 1),
    INSTANCE_STATE_BACKUPING: (_("Instance Backuping"), 0),
    INSTANCE_STATE_RESTORING: (_("Instance Restoring"), 0),
    INSTANCE_STATE_RESIZING: (_("Instance Resizing"), 0),
    INSTANCE_STATE_EXPIRED: (_("Instance Expired"), 1),
    INSTANCE_STATE_DELETING: (_("Instance Deleting"), 0),
    INSTANCE_STATE_APPLYING: (_("Applying"), 0),
    INSTANCE_STATE_REJECTED: (_("Rejected"), 1),
}

INSTANCE_ACTIVE = 0
INSTANCE_BUILD = 1
INSTANCE_POWER_OFF = 2
INSTANCE_PAUSE = 3
INSTANCE_LOCK = 4
INSTANCE_RESIZE = 5
INSTANCE_REBOOT = 6
INSTANCE_BACKUP = 7
INSTANCE_RESTORE = 8


INSTANCE_ACTIONS = (
    (INSTANCE_ACTIVE, _("Instance Active")),
    (INSTANCE_BUILD, _("Instance Build")),
    (INSTANCE_POWER_OFF, _("Instance Power Off")),
    (INSTANCE_PAUSE, _("Instance Pause")),
    (INSTANCE_LOCK, _("Instance Lock")),
    (INSTANCE_RESIZE, _("Instance Resize")),
    (INSTANCE_REBOOT, _("Instance Reboot")),
    (INSTANCE_RESTORE, _("Instance Restore")),
)


INSTANCE_ACTIONS_DICT = {
    'REBOOT': 'reboot',
    'TERMINATE': 'terminate',
    'POWER_ON': 'power_on',
    'POWER_OFF': 'power_off',
    'RESTORE': 'restore',
    'PAUSE': 'pause',
    'ACTIVE': 'active',
    'LAUNCH': 'launch',
}

ALLOWED_INSTANCE_ACTIONS = {
    "reboot": _("Instance Reboot"),
    "power_on": _("Instance Power On"),
    "power_off": _("Instance Power Off"),
    "vnc_console": _("Instance VNC"),
    "bind_floating": _("Instance Bind Floating"),
    "unbind_floating": _("Instance Unbind Floating"),
    "change_firewall": _("Instance Change Firewall"),
    "attach_volume": _("Instance Attach Volume"),
    "detach_volume": _("Instance Detach Volume"),
    "terminate": _("Instance Terminate"),
    "launch": _("Instance Launch"),
}


INSTANCE_ACTION_NEXT_STATE = {
    "power_off": INSTANCE_STATE_SHUTTING_DOWN,
    "power_on": INSTANCE_STATE_BOOTING,
    "reboot": INSTANCE_STATE_REBOOTING,
    "terminate": INSTANCE_STATE_DELETING,
    "pause": INSTANCE_STATE_PAUSED,
    "restore": INSTANCE_STATE_RESTORING,
}

PROTOCOL_ALL = 0
PROTOCOL_ICMP = 1
PROTOCOL_TCP = 2
PROTOCOL_UDP = 3

PROTOCOLs = (
    (PROTOCOL_ALL, "ALL"),
    (PROTOCOL_ICMP, "ICMP"),
    (PROTOCOL_TCP, "TCP"),
    (PROTOCOL_UDP, "UDP")
)


ACTION_ALLOW = 0
ACTION_DENY = 1

ACTIONS = (
    (ACTION_ALLOW, "ALLOW"),
    (ACTION_DENY, "DENY")
)

IPV4 = 4
IPV6 = 6

IP_VERSIONS = (
    (IPV4, "IPV4"),
    (IPV6, "IPV6")
)


class MonitorInterval(object):

    OPTIONS = (
        ('second', _('Second')),
        ('minute', _('Minute')),
        ('hour', _('Hourly')),
        ('day', _('Daily')),
        ('week', _('Weekly')),
        ('month', _('Monthly')),
        ('year', _('Yearly'))
    )

    @classmethod
    def filter_options(cls, keys):
        result = []

        for option in cls.OPTIONS:
            if option[0] in keys:
                result.append({'key': option[0], 'label': option[1]})

        return result

