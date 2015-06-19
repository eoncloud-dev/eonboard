# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DataCenter',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('host', models.CharField(help_text='IP of Compute Center', unique=True, max_length=255, verbose_name='openstack host')),
                ('project', models.CharField(help_text='Project Name of Data Center,recommended: admin', max_length=255, verbose_name='default project')),
                ('user', models.CharField(help_text='User who can visit the project', max_length=255, verbose_name='default project user')),
                ('password', models.CharField(max_length=255, verbose_name='default user password')),
                ('auth_url', models.CharField(max_length=255, verbose_name='usually http://host:5000/v2.0')),
                ('ext_net', models.CharField(default=b'net04_ext', max_length=255, verbose_name='External Network Name')),
            ],
            options={
                'db_table': 'data_center',
                'verbose_name': 'DataCenter',
                'verbose_name_plural': 'DataCenter',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserDataCenter',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('tenant_name', models.CharField(max_length=255, verbose_name='Tenant')),
                ('tenant_uuid', models.CharField(max_length=64, verbose_name='Tenant UUID')),
                ('keystone_user', models.CharField(max_length=255, verbose_name='User')),
                ('keystone_password', models.CharField(max_length=255, verbose_name='Password')),
                ('data_center', models.ForeignKey(to='idc.DataCenter')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_data_center',
                'verbose_name': 'UserDataCenter',
                'verbose_name_plural': 'UserDataCenter',
            },
            bases=(models.Model,),
        ),
    ]
