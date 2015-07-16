# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('idc', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('network', '0002_add_user_udc_to_routerinterface'),
        ('instance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BalancerMember',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('member_uuid', models.CharField(max_length=40, null=True, verbose_name='Member_UUID', blank=True)),
                ('address', models.CharField(max_length=20, null=True, verbose_name='Address', blank=True)),
                ('protocol_port', models.IntegerField(null=True, verbose_name='Protocol port', blank=True)),
                ('weight', models.IntegerField(verbose_name='Weight')),
                ('admin_state_up', models.BooleanField(default=True, verbose_name='Admin state up', choices=[(True, b'UP'), (False, b'DOWN')])),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'CREATING'), (1, 'ACTIVE'), (2, 'CREATED'), (3, 'DOWN'), (4, 'ERROR'), (5, 'INACTIVE'), (6, 'UPDATING'), (7, 'DELETING')])),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('instance', models.ForeignKey(blank=True, to='instance.Instance', null=True)),
            ],
            options={
                'db_table': 'lbaas_member',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BalancerMonitor',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('monitor_uuid', models.CharField(max_length=40, verbose_name='Monitor uuid', blank=True)),
                ('name', models.CharField(max_length=128, null=True, verbose_name='Monitor name', blank=True)),
                ('type', models.IntegerField(verbose_name='Type', choices=[(0, b'PING'), (1, b'TCP'), (2, b'HTTP'), (3, b'HTTPS')])),
                ('delay', models.IntegerField(max_length=10, null=True, verbose_name='Delay', blank=True)),
                ('timeout', models.IntegerField(max_length=10, null=True, verbose_name='Timeout', blank=True)),
                ('max_retries', models.IntegerField(verbose_name='Max retries')),
                ('http_method', models.CharField(default=b'POST', max_length=10, null=True, verbose_name='Http method', blank=True)),
                ('url_path', models.CharField(default=b'/', max_length=10, null=True, verbose_name='Url path', blank=True)),
                ('expected_codes', models.CharField(default=b'200', max_length=128, null=True, verbose_name='Expected codes', blank=True)),
                ('admin_state_up', models.BooleanField(default=True, verbose_name='Admin state up', choices=[(True, b'UP'), (False, b'DOWN')])),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'lbaas_monitor',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BalancerPool',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('pool_uuid', models.CharField(max_length=40, null=True, verbose_name='Pool UUID', blank=True)),
                ('name', models.CharField(max_length=64, verbose_name='Pool name')),
                ('description', models.CharField(max_length=128, verbose_name='Description', blank=True)),
                ('protocol', models.IntegerField(verbose_name='protocol', choices=[(0, b'TCP'), (1, b'HTTP'), (2, b'HTTPS')])),
                ('lb_method', models.IntegerField(verbose_name='Lb method', choices=[(0, b'ROUND_ROBIN'), (1, b'LEAST_CONNECTIONS'), (2, b'SOURCE_IP')])),
                ('provider', models.IntegerField(default=0, verbose_name='Provider', choices=[(0, b'haproxy')])),
                ('admin_state_up', models.BooleanField(default=True, verbose_name='Admin state up', choices=[(True, b'UP'), (False, b'DOWN')])),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'CREATING'), (1, 'ACTIVE'), (2, 'CREATED'), (3, 'DOWN'), (4, 'ERROR'), (5, 'INACTIVE'), (6, 'UPDATING'), (7, 'DELETING')])),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('subnet', models.ForeignKey(to='network.Subnet')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'lbaas_pool',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BalancerPoolMonitor',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('monitor', models.ForeignKey(related_name='monitor_re', to='lbaas.BalancerMonitor')),
                ('pool', models.ForeignKey(related_name='pool_re', to='lbaas.BalancerPool')),
            ],
            options={
                'db_table': 'lbaas_pool_monitor',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BalancerVIP',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('vip_uuid', models.CharField(max_length=40, verbose_name='VIP_uuid', blank=True)),
                ('name', models.CharField(max_length=64, null=True, verbose_name='Pool name', blank=True)),
                ('description', models.CharField(max_length=128, null=True, verbose_name='Description', blank=True)),
                ('public_address', models.CharField(max_length=20, null=True, verbose_name='Address', blank=True)),
                ('address', models.CharField(max_length=20, null=True, verbose_name='Address', blank=True)),
                ('protocol', models.IntegerField(verbose_name='Protocol', choices=[(0, b'TCP'), (1, b'HTTP'), (2, b'HTTPS')])),
                ('protocol_port', models.IntegerField(null=True, verbose_name='Protocol port', blank=True)),
                ('port_id', models.CharField(max_length=40, null=True, verbose_name='Port id', blank=True)),
                ('session_persistence', models.IntegerField(blank=True, null=True, verbose_name='Session persistence', choices=[(0, b'SOURCE_IP'), (1, b'HTTP_COOKIE'), (2, b'APP_COOKIE')])),
                ('connection_limit', models.IntegerField(default=-1, verbose_name='Connection limit')),
                ('admin_state_up', models.BooleanField(default=True, verbose_name='Admin state up', choices=[(True, b'UP'), (False, b'DOWN')])),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'CREATING'), (1, 'ACTIVE'), (2, 'CREATED'), (3, 'DOWN'), (4, 'ERROR'), (5, 'INACTIVE'), (6, 'UPDATING'), (7, 'DELETING')])),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('subnet', models.ForeignKey(blank=True, to='network.Subnet', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'lbaas_vip',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='balancerpool',
            name='vip',
            field=models.ForeignKey(related_name='vip_obj', blank=True, to='lbaas.BalancerVIP', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='balancermember',
            name='pool',
            field=models.ForeignKey(blank=True, to='lbaas.BalancerPool', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='balancermember',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='balancermember',
            name='user_data_center',
            field=models.ForeignKey(to='idc.UserDataCenter'),
            preserve_default=True,
        ),
    ]
