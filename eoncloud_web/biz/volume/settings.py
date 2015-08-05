#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

VOLUME_STATE_CREATING = 0
VOLUME_STATE_ATTACHING = 1
VOLUME_STATE_AVAILABLE = 2
VOLUME_STATE_BACKING_UP = 3
VOLUME_STATE_DELETING = 4
VOLUME_STATE_DOWNLOADING = 5
VOLUME_STATE_ERROR = 6
VOLUME_STATE_ERROR_DELETING = 7
VOLUME_STATE_ERROR_RESTORING = 8
VOLUME_STATE_IN_USE = 9
VOLUME_STATE_RESTORING_BACKUP = 10
VOLUME_STATE_UPLOADING = 11
VOLUME_STATE_UNRECOGNIZED = 12
VOLUME_STATE_APPLYING = 13
VOLUME_STATE_REJECTED = 14


VOLUME_STATES = (
    (VOLUME_STATE_CREATING, _("Volume Creating")), #0
    (VOLUME_STATE_ATTACHING, _("Volume Attaching")), #1
    (VOLUME_STATE_AVAILABLE, _("Volume Available")), #2
    (VOLUME_STATE_BACKING_UP, _("Volume Backing Up")),#3
    (VOLUME_STATE_DELETING, _("Volume Deleting")), #4
    (VOLUME_STATE_DOWNLOADING, _("Volume Downloading")),#5
    (VOLUME_STATE_ERROR, _("Volume Error")),
    (VOLUME_STATE_ERROR_DELETING, _("Volume Error Deleting")),
    (VOLUME_STATE_ERROR_RESTORING, _("Volume Error Restoring")),
    (VOLUME_STATE_IN_USE, _("Volume In Use")),
    (VOLUME_STATE_RESTORING_BACKUP, _("Volume Restoring Backup")),
    (VOLUME_STATE_UNRECOGNIZED, _("Volume Unrecognized")),
    (VOLUME_STATE_UPLOADING, _("Volume Uploading")),
    (VOLUME_STATE_APPLYING, _("Applying")),
    (VOLUME_STATE_REJECTED, _("Rejected")),
)


#volume 的状态描述字典,  其中包含描述信息和该状态是否稳定的标识信息
#0表示不稳定，1表示稳定
VOLUME_STATES_DICT = {
    VOLUME_STATE_CREATING: (_("Volume Creating"), 0),
    VOLUME_STATE_ATTACHING: (_("Volume Attaching"), 0),
    VOLUME_STATE_AVAILABLE: (_("Volume Available"), 1),
    VOLUME_STATE_BACKING_UP: (_("Volume Backing Up"), 1),
    VOLUME_STATE_DELETING: (_("Volume Deleting"), 0),
    VOLUME_STATE_DOWNLOADING: (_("Volume Downloading"), 0),
    VOLUME_STATE_ERROR: (_("Volume Error"), 1),
    VOLUME_STATE_ERROR_DELETING: (_("Volume Error Deleting"), 0),
    VOLUME_STATE_ERROR_RESTORING: (_("Volume Error Restoring"), 0),
    VOLUME_STATE_IN_USE: (_("Volume In Use"), 1),
    VOLUME_STATE_RESTORING_BACKUP: (_("Volume Restoring Backup"), 0),
    VOLUME_STATE_UNRECOGNIZED: (_("Volume Unrecognized"), 1),
    VOLUME_STATE_UPLOADING: (_("Volume Uploading"), 0),
    VOLUME_STATE_APPLYING: (_("Applying"), 0),
    VOLUME_STATE_REJECTED: (_("Rejected"), 1),
}
VOLUME_TYPE_VOLUME = 0
VOLUME_TYPE_PERFORMANCE = 1
VOLUME_TYPES = (
    (VOLUME_TYPE_VOLUME, _("Capacity")), #0
    (VOLUME_TYPE_PERFORMANCE, _("Performance")), #1
)
