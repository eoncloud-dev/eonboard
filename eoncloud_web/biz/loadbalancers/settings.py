#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

POOL_CREATING = 0
POOL_ACTIVE = 1
POOL_CREATED = 2
POOL_DOWN = 3
POOL_ERROR = 4
POOL_INACTIVE = 5
POOL_UPDATING = 6
POOL_DELETING = 7

POOL_STATES = (
    (POOL_CREATING, _("CREATING")), #0
    (POOL_ACTIVE, _("ACTIVE")), #0
    (POOL_CREATED, _("CREATED")),
    (POOL_DOWN, _("DOWN")),
    (POOL_ERROR, _("ERROR")),
    (POOL_INACTIVE, _("INACTIVE")),
    (POOL_UPDATING, _("UPDATING")),
    (POOL_DELETING, _("DELETING")),
)
POOL_STATES_DICT = {
    POOL_CREATING: (_("Creating"), 0),
    POOL_ACTIVE: (_("ACTIVE"), 1),
    POOL_CREATED: (_("CREATED"), 1),
    POOL_DOWN: (_("DOWN"), 1),
    POOL_ERROR: (_("ERROR"), 1),
    POOL_INACTIVE: (_("INACTIVE"), 1),
    POOL_UPDATING: (_("UPDATING"), 0),
    POOL_DELETING: (_("DELETING"), 0),
    }

PROTOCOL_CHOICES = (
    (0, "TCP"),
    (1, "HTTP"),
    (2, "HTTPS"),
)

LB_METHOD_CHOICES = (
    (0, 'ROUND_ROBIN'),
    (1, 'LEAST_CONNECTIONS'),
    (2, 'SOURCE_IP'),
)

SESSION_PER_CHOICES = (
    (0, 'SOURCE_IP'),
    (1, 'HTTP_COOKIE'),
    (2, 'APP_COOKIE'),
)


ADMIN_STATE_UP = (
    (True, 'UP'),
    (False, 'DOWN'),
)


MONITOR_TYPE = (
    (0, 'PING'),
    (1, 'TCP'),
    (2, 'HTTP'),
    (3, 'HTTPS'),
)

PROVIDER_CHOICES = (
    (0, 'haproxy'),
)
