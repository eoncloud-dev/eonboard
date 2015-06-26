#coding=utf-8

from django.utils.translation import ugettext_lazy as _

BACKUP_TYPE_FULL = 1
BACKUP_TYPE_INCREMENT = 2

BACKUP_TYPE_CHOICES = (
    (BACKUP_TYPE_FULL, _("BACKUP_TYPE_FULL")),
    (BACKUP_TYPE_INCREMENT, _("BACKUP_TYPE_INCREMENT")),
)

BACKUP_STATE_WAITING = 0
BACKUP_STATE_AVAILABLE = 1
BACKUP_STATE_ERROR=2
BACKUP_STATE_DELETED=9

BACKUP_STATE_BACKUPING = 10
BACKUP_STATE_RESTORING = 11
BACKUP_STATE_DELETING=19

BACKUP_STATE_PENDING_DELETE=20
BACKUP_STATE_PENDING_RESTORE=21


BACKUP_STATES = (
    (BACKUP_STATE_WAITING, _("Backup Waiting")),
    (BACKUP_STATE_AVAILABLE, _("Backup Available")),
    (BACKUP_STATE_ERROR, _("Backup Error")),
    (BACKUP_STATE_DELETED, _("Backup Deleted")),
    (BACKUP_STATE_BACKUPING, _("Backup Backuping")),
    (BACKUP_STATE_RESTORING, _("Backup Restoring")),
    (BACKUP_STATE_PENDING_DELETE, _("Backup Pending Delete")),
    (BACKUP_STATE_PENDING_RESTORE, _("Backup Pending Restore")),
    (BACKUP_STATE_DELETING, _("Backup Deleting")),
)


BACKUP_STATES_DICT = {
    BACKUP_STATE_WAITING: (_("Backup Waiting"), 0),
    BACKUP_STATE_AVAILABLE: (_("Backup Available"), 1),
    BACKUP_STATE_ERROR: (_("Backup Error"), 1),
    BACKUP_STATE_DELETED: (_("Backup Deleted"), 1),
    BACKUP_STATE_BACKUPING: (_("Backup Backuping"), 0),
    BACKUP_STATE_RESTORING: (_("Backup Restoring"), 0),
    BACKUP_STATE_PENDING_DELETE: (_("Backup Pending Delete"), 0),
    BACKUP_STATE_PENDING_RESTORE: (_("Backup Pending Restore"), 0),
    BACKUP_STATE_DELETING: (_("Backup Deleting"), 0),
}

BACKUP_ACTION_NEXT_STATE = {
    "create": BACKUP_STATE_AVAILABLE,
    "restore": BACKUP_STATE_AVAILABLE,
    "delete": BACKUP_STATE_DELETED,
}

