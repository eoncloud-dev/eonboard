# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('idc', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Contract name')),
                ('customer', models.CharField(max_length=128, verbose_name='Customer name')),
                ('start_date', models.DateTimeField(verbose_name='Start Date')),
                ('end_date', models.DateTimeField(verbose_name='End Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('udc', models.ForeignKey(to='idc.UserDataCenter')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'db_table': 'user_contract',
                'verbose_name': 'Contract',
                'verbose_name_plural': 'Contract',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('resource', models.CharField(max_length=128, verbose_name='Resource', choices=[(b'Instance', 'Instance'), (b'Volume', 'Volume'), (b'Network', 'Volume'), (b'Subnet', 'Volume'), (b'Router', 'Volume'), (b'Floating', 'Volume')])),
                ('resource_id', models.IntegerField(verbose_name='Resource ID')),
                ('resource_name', models.CharField(max_length=128, verbose_name='Resource Name')),
                ('action', models.CharField(max_length=128, verbose_name='Action')),
                ('result', models.IntegerField(default=0, verbose_name='Result')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('udc', models.ForeignKey(to='idc.UserDataCenter')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-create_date'],
                'db_table': 'user_operation',
                'verbose_name': 'Operation',
                'verbose_name_plural': 'Operation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('resource', models.CharField(max_length=128, verbose_name='Resouce', choices=[(b'instance', 'Instance'), (b'vcpu', 'CPU'), (b'memory', 'Memory(MB)'), (b'volume_size', 'Volume(GB)'), (b'volume', 'Volume Count'), (b'floating_ip', 'Floating IP')])),
                ('limit', models.IntegerField(default=0, verbose_name='Limit')),
                ('create_date', models.DateTimeField(default=datetime.datetime(2015, 6, 24, 11, 10, 42, 388511), verbose_name='Create Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('contract', models.ForeignKey(related_name='quotas', to='account.Contract')),
            ],
            options={
                'db_table': 'user_quota',
                'verbose_name': 'Quota',
                'verbose_name_plural': 'Quota',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mobile', models.CharField(max_length=26, null=True, verbose_name='Mobile')),
                ('user_type', models.IntegerField(default=1, null=True, verbose_name='User Type', choices=[(1, 'Personal'), (2, 'Company')])),
                ('balance', models.DecimalField(default=0.0, max_digits=9, decimal_places=2)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'db_table': 'auth_user_profile',
                'verbose_name': 'UserProfile',
                'verbose_name_plural': 'UserProfile',
            },
            bases=(models.Model,),
        ),
    ]
