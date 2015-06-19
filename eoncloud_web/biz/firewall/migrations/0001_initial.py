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
            name='Firewall',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Firewall Name')),
                ('firewall_id', models.CharField(max_length=128, null=True, verbose_name='OS Firewall UUID', blank=True)),
                ('desc', models.CharField(max_length=50, null=True, verbose_name='Firewall desc', blank=True)),
                ('is_default', models.BooleanField(default=False, verbose_name='Default')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'firewall',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FirewallRules',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('firewall_rules_id', models.CharField(max_length=40, null=True, verbose_name='OS Firewall Rules UUID', blank=True)),
                ('direction', models.CharField(default=b'ingress', choices=[(b'ingress', 'Ingress'), (b'egress', 'Egress')], max_length=10, blank=True, null=True, verbose_name='Direction')),
                ('ether_type', models.CharField(default=b'IPv4', choices=[(b'IPv4', 'IPv4'), (b'IPv6', 'IPv6')], max_length=40, blank=True, null=True, verbose_name='Ether type')),
                ('port_range_min', models.IntegerField(default=0, null=True, verbose_name='Port range min', blank=True)),
                ('port_range_max', models.IntegerField(default=0, null=True, verbose_name='Port range max', blank=True)),
                ('protocol', models.CharField(max_length=40, null=True, verbose_name='Protocol', blank=True)),
                ('remote_group_id', models.CharField(max_length=40, null=True, verbose_name='remote group id UUID', blank=True)),
                ('remote_ip_prefix', models.CharField(default=b'0.0.0.0/0', max_length=255, null=True, verbose_name='remote ip prefix', blank=True)),
                ('is_default', models.BooleanField(default=False, verbose_name='Default')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('firewall', models.ForeignKey(to='firewall.Firewall')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'firewall_rules',
            },
            bases=(models.Model,),
        ),
    ]
