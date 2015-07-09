#-*- coding=utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


from biz.instance.models import Instance
from biz.volume.models import Volume
from biz.backup.settings import BACKUP_TYPE_CHOICES, BACKUP_TYPE_FULL, \
                BACKUP_STATES, BACKUP_STATE_WAITING, \
                BACKUP_STATE_PENDING_DELETE, BACKUP_STATE_PENDING_RESTORE


class Backup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Name"), max_length=64)
    backup_type = models.IntegerField(_("Back Type"),
            choices=BACKUP_TYPE_CHOICES, default=BACKUP_TYPE_FULL)

    volumes = models.CharField(_("Volumes"), max_length=255,
                                null=True, blank=True, default=None)
    instance = models.IntegerField(_("Instance"),
                        null=True, blank=True, default=None)

    user_data_center = models.ForeignKey('idc.UserDataCenter')
    user = models.ForeignKey('auth.User')

    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    delete_date = models.DateTimeField(_("Delete Date"), auto_now=True)
    deleted = models.BooleanField(_("Deleted"), default=False)
    status = models.IntegerField(_("Status"), choices=BACKUP_STATES, 
                                default=BACKUP_STATE_WAITING)


    @property
    def backup_type_desc(self):
        return self.get_backup_type_display()

    @property
    def instance_name(self):
        if self.instance:
            try:
                ins = Instance.objects.get(pk=self.instance)
                return ins.name
            except:
                return '---'
        else:
            return 'N/A'

    @property
    def volume_name(self):
        if not self.instance and self.volumes:
            try:
                vol = Volume.objects.get(pk=self.volumes)
                return vol.name
            except:
                return '---'
        else:
            return 'N/A'

    def mark_delete(self):
        self.status = BACKUP_STATE_PENDING_DELETE
        self.save()
        self.items.all().update(status=BACKUP_STATE_PENDING_DELETE)

    def mark_restore(self, item_id=None):
        self.status = BACKUP_STATE_PENDING_RESTORE
        self.save()
        backup_items = self.items.all()
        if item_id:
            backup_items.filter(pk=item_id).update(status=BACKUP_STATE_PENDING_RESTORE)
        else:
            backup_items.update(status=BACKUP_STATE_PENDING_RESTORE)
    
    def create_items(self): 
        if self.instance:
            try:
                ins = Instance.objects.get(pk=self.instance) 
                BackupItem.objects.create(
                    backup=self,
                    resource_id=ins.id,
                    resource_uuid=ins.uuid,
                    resource_size=ins.sys_disk,
                    resource_type=Instance.__name__,
                    resource_name=ins.name,
                    user_data_center=self.user_data_center,
                    user=self.user,
                    status=self.status
                )
            except:
                pass
        if self.volumes:
            try: 
               for vol_id in self.volumes.split(','):
                    volume = Volume.objects.get(pk=vol_id) 
                    BackupItem.objects.create(
                        backup=self,
                        resource_id=volume.id,
                        resource_uuid=volume.volume_id,
                        resource_size=volume.size,
                        resource_type=Volume.__name__,
                        resource_name=volume.name,
                        user_data_center=self.user_data_center,
                        user=self.user,
                        status=self.status
                    )
            except:
                pass
        
    class Meta:
        db_table = "backup"
        verbose_name = _("Backup")
        verbose_name_plural = _("Backup")
        ordering = ['-create_date']


class BackupItem(models.Model):
    id = models.AutoField(primary_key=True)
    backup = models.ForeignKey(Backup, related_name="items")

    resource_id = models.IntegerField(_("Resource ID"),
                        null=True, blank=True, default=0)
    resource_uuid = models.CharField(_("Backend UUID"),
                        max_length=64, null=True, blank=True)
    resource_type = models.CharField(_("Resource"),
                        max_length=64, null=True, blank=True)
    resource_name = models.CharField(_("Resource Name"),
                            max_length=64, null=True, blank=True)
    resource_size = models.IntegerField(_("Size(GB)"),
                        null=True, blank=True, default=0)

    rbd_image = models.CharField(_("RBD Image"), max_length=256,
                        null=True, blank=True, default=None)
    
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    user = models.ForeignKey('auth.User')
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    delete_date = models.DateTimeField(_("Delete Date"), auto_now=True)
    deleted = models.BooleanField(_("Deleted"), default=False)
    status = models.IntegerField(_("Status"), choices=BACKUP_STATES, 
                                default=BACKUP_STATE_WAITING)

    class Meta:
        db_table = "backup_item"
        verbose_name = _("Backup Item")
        verbose_name_plural = _("Backup Item")
        ordering = ['-create_date']
