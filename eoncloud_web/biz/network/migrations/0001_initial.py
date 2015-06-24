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
            name='Network',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Network Name')),
                ('network_id', models.CharField(max_length=128, null=True, verbose_name='OS Network UUID', blank=True)),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'BUILD'), (1, 'ACTIVE'), (2, 'DOWN'), (3, 'ERROR'), (4, 'CREATING'), (5, 'DELETING'), (6, 'UPDATING')])),
                ('is_default', models.BooleanField(default=False, verbose_name='Default')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'network',
                'verbose_name': 'Network',
                'verbose_name_plural': 'Network',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Router',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Router Name')),
                ('router_id', models.CharField(max_length=128, null=True, verbose_name='OS Router UUID', blank=True)),
                ('gateway', models.CharField(max_length=128, null=True, verbose_name='OS Router UUID', blank=True)),
                ('is_gateway', models.BooleanField(default=False, verbose_name='Deleted')),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'BUILD'), (1, 'ACTIVE'), (2, 'DOWN'), (3, 'ERROR'), (4, 'CREATING'), (5, 'DELETING'), (6, 'UPDATING')])),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('is_default', models.BooleanField(default=False, verbose_name='Default')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'router',
                'verbose_name': 'Router',
                'verbose_name_plural': 'Router',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RouterInterface',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('os_port_id', models.CharField(max_length=128, null=True, verbose_name='Port', blank=True)),
                ('network_id', models.IntegerField(verbose_name='Network')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('router', models.ForeignKey(to='network.Router')),
            ],
            options={
                'db_table': 'router_interface',
                'verbose_name': 'RouterInterface',
                'verbose_name_plural': 'RouterInterface',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subnet',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Network Name')),
                ('subnet_id', models.CharField(max_length=128, null=True, verbose_name='OS Subnet UUID', blank=True)),
                ('address', models.CharField(max_length=128, verbose_name='IPv4 CIDR')),
                ('ip_version', models.IntegerField(default=4, verbose_name='IP Version', choices=[(4, b'IP V4'), (6, b'IP V6')])),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'BUILD'), (1, 'ACTIVE'), (2, 'DOWN'), (3, 'ERROR'), (4, 'CREATING'), (5, 'DELETING'), (6, 'UPDATING')])),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('network', models.ForeignKey(to='network.Network')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'subnet',
                'verbose_name': 'Subnet',
                'verbose_name_plural': 'Subnet',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='routerinterface',
            name='subnet',
            field=models.ForeignKey(to='network.Subnet'),
            preserve_default=True,
        ),
    ]
