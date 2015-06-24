# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('image', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('firewall', '__first__'),
        ('idc', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flavor',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('cpu', models.IntegerField(verbose_name='Cpu Cores')),
                ('memory', models.IntegerField(verbose_name='Memory MB')),
                ('price', models.FloatField(verbose_name='Price')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
            ],
            options={
                'ordering': ['cpu'],
                'db_table': 'flavor',
                'verbose_name': 'Flavor',
                'verbose_name_plural': 'Flavor',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Instance Name')),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'Instance Waiting'), (1, 'Instance Running'), (2, 'Instance Booting'), (3, 'Instance Rebooting'), (4, 'Instance Paused'), (5, 'Instance Power Off'), (6, 'Instance Shutting Down'), (7, 'Instance Deploying'), (8, 'Instance Deploy Failed'), (9, 'Instance Locked'), (10, 'Instance Delete'), (11, 'Instance Error'), (12, 'Instance Backuping'), (13, 'Instance Restoring'), (14, 'Instance Resizing'), (15, 'Instance Expired'), (16, 'Instance Deleting')])),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('terminate_date', models.DateTimeField(auto_now_add=True, verbose_name='Terminate Date')),
                ('cpu', models.IntegerField(verbose_name='Cpu Cores')),
                ('memory', models.IntegerField(verbose_name='Memory')),
                ('sys_disk', models.FloatField(verbose_name='System Disk', blank=True)),
                ('flavor_id', models.CharField(max_length=36, null=True, verbose_name='OS FlavorID')),
                ('network_id', models.IntegerField(default=0, verbose_name='Network')),
                ('uuid', models.CharField(max_length=128, null=True, verbose_name=b'instance uuid', blank=True)),
                ('private_ip', models.CharField(max_length=255, null=True, verbose_name='Private IP', blank=True)),
                ('public_ip', models.CharField(max_length=255, null=True, verbose_name='Public IP', blank=True)),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('firewall_group', models.ForeignKey(to='firewall.Firewall', null=True)),
                ('image', models.ForeignKey(db_column=b'image_id', blank=True, to='image.Image', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'ordering': ['-create_date'],
                'db_table': 'instance',
                'verbose_name': 'Instance',
                'verbose_name_plural': 'Instance',
            },
            bases=(models.Model,),
        ),
    ]
