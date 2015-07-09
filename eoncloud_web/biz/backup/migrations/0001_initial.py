# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('idc', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('backup_type', models.IntegerField(default=1, verbose_name='Back Type', choices=[(1, 'BACKUP_TYPE_FULL'), (2, 'BACKUP_TYPE_INCREMENT')])),
                ('volumes', models.CharField(default=None, max_length=255, null=True, verbose_name='Volumes', blank=True)),
                ('instance', models.IntegerField(default=None, null=True, verbose_name='Instance', blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('delete_date', models.DateTimeField(auto_now=True, verbose_name='Delete Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'Backup Waiting'), (1, 'Backup Available'), (2, 'Backup Error'), (9, 'Backup Deleted'), (10, 'Backup Backuping'), (11, 'Backup Restoring'), (20, 'Backup Pending Delete'), (21, 'Backup Pending Restore'), (19, 'Backup Deleting')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'ordering': ['-create_date'],
                'db_table': 'backup',
                'verbose_name': 'Backup',
                'verbose_name_plural': 'Backup',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BackupItem',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('resource_id', models.IntegerField(default=0, null=True, verbose_name='Resource ID', blank=True)),
                ('resource_uuid', models.CharField(max_length=64, null=True, verbose_name='Backend UUID', blank=True)),
                ('resource_type', models.CharField(max_length=64, null=True, verbose_name='Resource', blank=True)),
                ('resource_name', models.CharField(max_length=64, null=True, verbose_name='Resource Name', blank=True)),
                ('resource_size', models.IntegerField(default=0, null=True, verbose_name='Size(GB)', blank=True)),
                ('rbd_image', models.CharField(default=None, max_length=256, null=True, verbose_name='RBD Image', blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('delete_date', models.DateTimeField(auto_now=True, verbose_name='Delete Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'Backup Waiting'), (1, 'Backup Available'), (2, 'Backup Error'), (9, 'Backup Deleted'), (10, 'Backup Backuping'), (11, 'Backup Restoring'), (20, 'Backup Pending Delete'), (21, 'Backup Pending Restore'), (19, 'Backup Deleting')])),
                ('backup', models.ForeignKey(related_name='items', to='backup.Backup')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'ordering': ['-create_date'],
                'db_table': 'backup_item',
                'verbose_name': 'Backup Item',
                'verbose_name_plural': 'Backup Item',
            },
            bases=(models.Model,),
        ),
    ]
